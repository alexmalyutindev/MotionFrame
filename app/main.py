#!/usr/bin/env python3

import os
import re
from PySide6.QtWidgets import (QApplication, QFileDialog, QMessageBox, QMainWindow)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTranslator
from PIL import Image
from MainWindow import Ui_MotionFrame
from pathlib import Path
import lib

class MotionFrameApp(QMainWindow, Ui_MotionFrame):
    def __init__(self):
        super(MotionFrameApp, self).__init__()
        self.setupUi(self)

        self.setWindowTitle('MotionFrame')
        self.language = 'en'
        self.directory = None

        self.translator = QTranslator()
        self.load_translator()

        self.button_file_browse.clicked.connect(self.select_file)
        self.button_generate.clicked.connect(self.start_processing)
        self.button_copy_motion_strength.clicked.connect(self.copy_motion_strength)
        self.button_save.clicked.connect(self.save_results)

        self.radio_button_language_english.toggled.connect(lambda: self.change_language('en'))
        self.radio_button_language_japanese.toggled.connect(lambda: self.change_language('ja'))

        self.button_update_frames.clicked.connect(self.update_frame_count)

        self.number_atlas_width.valueChanged.connect(self._update_optimal_frame_count)
        self.number_atlas_height.valueChanged.connect(self._update_optimal_frame_count)
        self.number_frame_skip.valueChanged.connect(self._update_optimal_frame_count)
        self.checkbox_loop.toggled.connect(self._update_optimal_frame_count)

        self._update_optimal_frame_count()

    def get_path_qm(self, lang):
        return (Path(__file__).parent / f"./translation/motionframe_{lang}.qm").absolute().as_posix()

    def load_translator(self):
        if self.language == 'ja':
            self.translator.load(self.get_path_qm(self.language))
            app.installTranslator(self.translator)

    def change_language(self, language):
        if language != self.language:
            self.language = language
            if language == 'en':
                app.removeTranslator(self.translator)
            else:
                self.translator.load(self.get_path_qm(self.language))
                app.installTranslator(self.translator)
            self.retranslateUi(self)

    def set_input_frame(self, frame_path):
        if not frame_path:
            return

        self.directory = os.path.dirname(frame_path)
        self.text_directory.setText(self.directory)
        prefix, ext, zeros = self.detect_image_sequence_pattern(os.path.basename(frame_path))
        self.text_file_prefix.setText(prefix)
        self.text_extension.setText(ext)
        self.number_sequence_digits.setValue(zeros)

        self.update_frame_count()

    def select_file(self):
        frame_path = QFileDialog.getOpenFileName(self, self.tr('Select Frame'), '',
                                                 'Images (*.jpg *.jpeg *.png *.bmp *.tiff *.tga)')[0]
        self.set_input_frame(frame_path)

    def load_frame_paths(self):
        prefix = self.text_file_prefix.text()
        extension = self.text_extension.text()
        num_digits = self.number_sequence_digits.value()

        pattern = f"^{prefix}[0-9]{{{int(num_digits)}}}.{extension}$"
        pattern = re.compile(pattern)
        files = os.listdir(self.directory)
        files.sort()

        file_paths = []

        for image_file in files:
            match = pattern.match(image_file)
            if match:
                file_paths.append(os.path.join(self.directory, image_file))

        return file_paths

    def get_optimal_frame_count(self):
        atlas_size = self.number_atlas_width.value() * self.number_atlas_height.value()
        frame_skip = self.number_frame_skip.value()

        used_frames = atlas_size * (1 + frame_skip)

        # When not looping, the last frame doesn't use the frame skip to analyze motion
        if not self.checkbox_loop.isChecked():
            used_frames -= frame_skip

        return used_frames

    def update_frame_count(self):
        self.label_input_number_of_frames_value.setText(str(len(self.load_frame_paths())))
        self._update_optimal_frame_count()

    def _update_optimal_frame_count(self):
        self.label_optimal_input_number_of_frames_value.setText(str(self.get_optimal_frame_count()))

    def detect_image_sequence_pattern(self, file_path):
        pattern = re.compile(r'(.*?)(\d+)\.(\w+)$')

        match = pattern.match(file_path)
        if not match:
            return None, None, None

        prefix, number, extension = match.groups()
        return prefix, extension, len(number)

    def copy_motion_strength(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_motion_strength.text())

    def check_atlas_fit(self, atlas_width, atlas_height, frame_skip, total_frame_count):
        expected_frames = atlas_width * atlas_height
        actual_frames = lib.calculate_required_frames(total_frame_count, frame_skip)

        if actual_frames <= expected_frames:
            return True, self.tr('Frames can fit into the atlas.')

        excess_frames = actual_frames - expected_frames
        if excess_frames == 1:
            message = self.tr('1 frame won\'t fit into the atlas.')
        else:
            message = self.tr('%n frame(s) won\'t fit into the atlas.', '', excess_frames)

        min_skip = 0
        while lib.calculate_required_frames(total_frame_count, min_skip) > expected_frames:
            min_skip += 1

        message += '\n'
        message += self.tr('Try reducing the frame skip count or increasing the atlas size.')
        message += '\n'
        message += self.tr('Minimum frame skip required to fit the frames is %n.', '', min_skip)

        return False, message

    def start_processing(self):
        if not self.directory:
            QMessageBox.critical(self, self.tr('Error'), self.tr('No frames loaded. Check the file pattern and paths.'))
            return

        atlas_width = self.number_atlas_width.value()
        atlas_height = self.number_atlas_height.value()
        frame_skip = self.number_frame_skip.value()
        is_loop = self.checkbox_loop.isChecked()
        analyze_skipped_frames = self.checkbox_analyze_skipped_frames.isChecked()
        halve_motion = self.checkbox_downsample_motion_vector.isChecked()

        atlas_pixel_width = self.combo_atlas_resolution_width.currentIndex()
        # Convert the width to pixels, starts at 0 index with 32
        atlas_pixel_width = 32 * (2 ** atlas_pixel_width)

        frame_paths = self.load_frame_paths()

        can_fit, error_message = self.check_atlas_fit(atlas_width, atlas_height, frame_skip, len(frame_paths))
        if not can_fit:
            QMessageBox.critical(self, self.tr('Error'), error_message)
            return

        frames = lib.load_frames(frame_paths)

        if not frames or len(frames) == 0:
            QMessageBox.critical(self, self.tr('Error'), self.tr('No frames loaded. Check the file pattern and paths.'))
            return

        if len(frames) != len(frame_paths):
            QMessageBox.warning(self, self.tr('Error'), self.tr('Some frames could not be loaded.'))
            return

        motion_vector_encoding = lib.MotionVectorEncoding(self.combo_motion_vector_encoding.currentIndex())

        self.result = lib.encode_atlas(frames, atlas_width, atlas_height, atlas_pixel_width, frame_skip, motion_vector_encoding, is_loop, analyze_skipped_frames, halve_motion)

        self.display_image(self.result.color_atlas, self.label_color_atlas_image)
        self.display_image(self.result.motion_atlas, self.label_motion_vector_image)
        self.display_image(self.result.flow_directions, self.label_visualization_image)

        discarded_frames = len(frames) - ((lib.calculate_required_frames(len(frames), frame_skip) - 1) * (1 + frame_skip) - 1)
        self.text_motion_strength.setText(f"{self.result.strength:.8f}")
        self.label_discarded_trailing_frames_value.setText(str(discarded_frames))
        self.label_total_frames_value.setText(str(self.result.total_frames))

    def display_image(self, image, label):
        channels = lib.channel_count(image)
        image = lib.bgr_to_rgb(image)

        height, width = image.shape[0], image.shape[1]
        bytes_per_line = channels * width
        image_format = QImage.Format_RGBA8888
        if channels == 1:
            image_format = QImage.Format_Grayscale8
        if channels == 3:
            image_format = QImage.Format_RGB888

        q_img = QImage(image.data, width, height, bytes_per_line, image_format)
        pixmap = QPixmap(q_img)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)

    def save_results(self):
        save_path = QFileDialog.getSaveFileName(self, self.tr('Save'))[0]
        if not save_path:
            return

        color_atlas_path = save_path + "_color_atlas.tga"
        motion_atlas_path = save_path + "_motion_atlas.tga"

        color_atlas = lib.bgr_to_rgb(self.result.color_atlas)
        motion_atlas = lib.bgr_to_rgb(self.result.motion_atlas)

        Image.fromarray(color_atlas).save(color_atlas_path)
        Image.fromarray(motion_atlas).save(motion_atlas_path)

        QMessageBox.information(self, self.tr('Save'), self.tr('The results have been saved successfully.'))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()

            if os.path.isdir(path):
                files = os.listdir(path)
                for file in files:
                    if re.search(r'\.(jpg|jpeg|png|bmp|tiff|tga)$', file, re.IGNORECASE):
                        self.set_input_frame(os.path.join(path, file))
                        event.acceptProposedAction()
                        break

            if os.path.isfile(path):
                self.set_input_frame(path)
                event.acceptProposedAction()
                break

if __name__ == '__main__':
    app = QApplication([])
    window = MotionFrameApp()
    window.show()
    app.exec()

