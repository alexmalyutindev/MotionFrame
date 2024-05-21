#!/usr/bin/env python3
import os
import cv2
import numpy as np
import imageio.v3 as imageio
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import lib

# Localization dictionary
localization = {
        'en': {
            'select_directory': 'Select Directory',
            'directory': 'Directory:',
            'file_prefix': 'File Prefix:',
            'extension': 'Extension:',
            'num_digits': 'Number of Digits:',
            'atlas_width': 'Atlas Width:',
            'atlas_height': 'Atlas Height:',
            'frame_skip': 'Frame Skip:',
            'scale': 'Scale:',
            'motion_vector_u': 'Motion Strength U:',
            'motion_vector_v': 'Motion Strength V:',
            'start': 'Start',
            'save': 'Save',
            'color_atlas': 'Color Atlas',
            'motion_atlas': 'Motion Atlas',
            'motion_vectors': 'Motion Vectors',
            'results_saved': 'The results have been saved successfully.',
            'error': 'Error',
            'no_frames_loaded': 'No frames loaded. Check the file pattern and paths.',
            'frames_fit': "Frames can fit into the atlas.",
            'one_frame_wont_fit': "1 frame won't fit into the atlas.",
            'frames_wont_fit': "{} frames won't fit into the atlas.",
            'try_adjusting': " Try reducing the frame skip count or increasing the atlas size.",
            'min_skip': " Minimum frame skip required to fit the frames is {}."
            },
        'ja': {
            'select_directory': 'ディレクトリを選択',
            'directory': 'ディレクトリ:',
            'file_prefix': 'ファイル接頭辞:',
            'extension': '拡張子:',
            'num_digits': 'フレーム番号桁数:',
            'atlas_width': 'アトラス幅:',
            'atlas_height': 'アトラス高さ:',
            'frame_skip': 'フレームスキップ:',
            'scale': 'スケール:',
            'motion_vector_u': 'モーション強度U:',
            'motion_vector_v': 'モーション強度V:',
            'start': '開始',
            'save': '保存',
            'color_atlas': 'カラーマップ',
            'motion_atlas': 'モーションマップ',
            'motion_vectors': 'モーションベクトル',
            'results_saved': '結果が正常に保存されました。',
            'error': 'エラー',
            'no_frames_loaded': 'フレームが読み込まれていません。ファイルパターンとパスを確認してください。',
            'frames_fit': "フレームはアトラスに収まります。",
            'one_frame_wont_fit': "1フレームがアトラスに収まりません。",
            'frames_wont_fit': "{}フレームがアトラスに収まりません。",
            'try_adjusting': " フレームスキップ数を減らすか、アトラスのサイズを増やしてください。",
            'min_skip': " フレームを収めるために必要な最小フレームスキップは{}です。"
            }
}

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title('MotionFrame')
        self.root.geometry('1000x800')
        self.language = 'en'

        self.create_widgets()

    def create_widgets(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Form frame
        form_frame = ttk.Frame(self.root)
        form_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=20)

        row = 0

        # Language switch
        ttk.Label(form_frame, text="Language:").grid(row=row, column=0, sticky=tk.W)
        self.language_var = tk.StringVar(value=self.language)
        language_frame = ttk.Frame(form_frame)
        ttk.Radiobutton(language_frame, text="English", variable=self.language_var, value='en', command=self.change_language).pack(side=tk.LEFT)
        ttk.Radiobutton(language_frame, text="日本語", variable=self.language_var, value='ja', command=self.change_language).pack(side=tk.LEFT)
        language_frame.grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Directory selection
        ttk.Label(form_frame, text=localization[self.language]['directory']).grid(row=row, column=0, sticky=tk.W)
        self.selectDirButton = ttk.Button(form_frame, text=localization[self.language]['select_directory'], command=self.select_directory)
        self.selectDirButton.grid(row=row, column=1, sticky=tk.W)
        row += 1

        ttk.Label(form_frame, text=localization[self.language]['file_prefix']).grid(row=row, column=0, sticky=tk.W)
        self.filePrefixInput = ttk.Entry(form_frame)
        self.filePrefixInput.grid(row=row, column=1, sticky=tk.W)
        self.filePrefixInput.insert(0, "")
        row += 1

        ttk.Label(form_frame, text=localization[self.language]['extension']).grid(row=row, column=0, sticky=tk.W)
        self.fileExtensionInput = ttk.Entry(form_frame)
        self.fileExtensionInput.grid(row=row, column=1, sticky=tk.W)
        self.fileExtensionInput.insert(0, "tga")
        row += 1

        ttk.Label(form_frame, text=localization[self.language]['num_digits']).grid(row=row, column=0, sticky=tk.W)
        self.numDigitsInput = ttk.Spinbox(form_frame, from_=1, to=10)
        self.numDigitsInput.grid(row=row, column=1, sticky=tk.W)
        self.numDigitsInput.set(3)
        row += 1

        # Atlas width input
        ttk.Label(form_frame, text=localization[self.language]['atlas_width']).grid(row=row, column=0, sticky=tk.W)
        self.atlasWidthInput = ttk.Spinbox(form_frame, from_=2, to=32)
        self.atlasWidthInput.grid(row=row, column=1, sticky=tk.W)
        self.atlasWidthInput.set(8)
        row += 1

        # Atlas height input
        ttk.Label(form_frame, text=localization[self.language]['atlas_height']).grid(row=row, column=0, sticky=tk.W)
        self.atlasHeightInput = ttk.Spinbox(form_frame, from_=2, to=32)
        self.atlasHeightInput.grid(row=row, column=1, sticky=tk.W)
        self.atlasHeightInput.set(8)
        row += 1

        # Frame skip input
        ttk.Label(form_frame, text=localization[self.language]['frame_skip']).grid(row=row, column=0, sticky=tk.W)
        self.frameSkipInput = ttk.Spinbox(form_frame, from_=0, to=64)
        self.frameSkipInput.grid(row=row, column=1, sticky=tk.W)
        self.frameSkipInput.set(0)
        row += 1

        # Scale input
        ttk.Label(form_frame, text=localization[self.language]['scale']).grid(row=row, column=0, sticky=tk.W)
        self.globalScaleInput = ttk.Spinbox(form_frame, from_=0.1, to=1.0, increment=0.1)
        self.globalScaleInput.grid(row=row, column=1, sticky=tk.W)
        self.globalScaleInput.set(0.5)
        row += 1

        # Motion Vector Strength display
        ttk.Label(form_frame, text=localization[self.language]['motion_vector_u']).grid(row=row, column=0, sticky=tk.W)
        self.motionVectorInputU = ttk.Entry(form_frame, state='readonly')
        self.motionVectorInputU.grid(row=row, column=1, sticky=tk.W)
        row += 1

        ttk.Label(form_frame, text=localization[self.language]['motion_vector_v']).grid(row=row, column=0, sticky=tk.W)
        self.motionVectorInputV = ttk.Entry(form_frame, state='readonly')
        self.motionVectorInputV.grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Buttons
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.startProcessingButton = ttk.Button(buttons_frame, text='Start', command=self.start_processing)
        self.startProcessingButton.pack(side=tk.LEFT, padx=5)

        self.saveResultsButton = ttk.Button(buttons_frame, text='Save', command=self.save_results)
        self.saveResultsButton.pack(side=tk.LEFT, padx=5)

        # Tabs
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(expand=1, fill='both')

        self.colorTab = ttk.Frame(self.tabs)
        self.motionTab = ttk.Frame(self.tabs)
        self.directionTab = ttk.Frame(self.tabs)
        self.tabs.add(self.colorTab, text=localization[self.language]['color_atlas'])
        self.tabs.add(self.motionTab, text=localization[self.language]['motion_atlas'])
        self.tabs.add(self.directionTab, text=localization[self.language]['motion_vectors'])

        self.color_canvas, self.color_scroll_x, self.color_scroll_y, self.colorFrame = self.create_image_display(self.colorTab)
        self.motion_canvas, self.motion_scroll_x, self.motion_scroll_y, self.motionFrame = self.create_image_display(self.motionTab)
        self.direction_canvas, self.direction_scroll_x, self.direction_scroll_y, self.directionFrame = self.create_image_display(self.directionTab)

    def change_language(self):
        self.language = self.language_var.get()
        self.create_widgets()

    def create_image_display(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True)

        canvas = tk.Canvas(frame, bg="gray")
        canvas.grid(row=0, column=0, sticky="nsew")

        scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")

        scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")

        canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        # Bind mouse wheel events for scrolling
        canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)  # Windows and macOS
        canvas.bind_all("<Button-4>", self._on_mouse_wheel)  # Linux scroll up
        canvas.bind_all("<Button-5>", self._on_mouse_wheel)  # Linux scroll down

        # Configure grid row and column weights to expand with parent
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        return canvas, scroll_x, scroll_y, inner_frame

    def _on_mouse_wheel(self, event):
        # Normalize scroll units
        if event.delta != 0:
            scroll_units = int(event.delta / abs(event.delta))  # Normalize delta to 1 or -1
        else:
            scroll_units = 1 if event.num == 4 else -1

        scroll_units = -scroll_units

        if event.state & 0x1:  # Shift key pressed
            self.color_canvas.xview_scroll(scroll_units, "units")
            self.motion_canvas.xview_scroll(scroll_units, "units")
            self.direction_canvas.xview_scroll(scroll_units, "units")
        else:
            self.color_canvas.yview_scroll(scroll_units, "units")
            self.motion_canvas.yview_scroll(scroll_units, "units")
            self.direction_canvas.yview_scroll(scroll_units, "units")

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory = directory
            self.selectDirButton.config(text=directory)
            prefix, ext, zeros = self._detect_image_sequence_pattern()
            self.filePrefixInput.delete(0, tk.END)
            self.filePrefixInput.insert(0, prefix)
            self.fileExtensionInput.delete(0, tk.END)
            self.fileExtensionInput.insert(0, ext)
            self.numDigitsInput.set(zeros)

    def display_image(self, image, canvas, frame):
        for widget in frame.winfo_children():
            widget.destroy()

        channels = lib.channel_count(image)
        if channels == 3 or channels == 4:
            image_copy = np.zeros_like(image)
            # RGB to BGR conversion
            if channels == 3:
                image_copy[..., [0, 1, 2]] = image[..., [2, 1, 0]]
            elif channels == 4:
                image_copy[..., [0, 1, 2, 3]] = image[..., [2, 1, 0, 3]]
            image = image_copy

        # Convert the image to PIL format
        image_pil = Image.fromarray(image)

        # Create a PhotoImage object from the PIL image
        image_tk = ImageTk.PhotoImage(image_pil)

        # Display the image on the canvas
        canvas.create_image(0, 0, anchor='nw', image=image_tk)

        # Keep a reference to the image to prevent it from being garbage collected
        canvas.image = image_tk

        # Update the scroll region to match the size of the image
        canvas.config(scrollregion=canvas.bbox("all"))
        canvas.update_idletasks()

    def _detect_image_sequence_pattern(self):
        directory_path = self.directory

        files = os.listdir(directory_path)
        image_files = [f for f in files if re.search(r'\.(jpg|jpeg|png|bmp|tiff|tga)$', f, re.IGNORECASE)]

        if not image_files:
            return None, None, None

        pattern = re.compile(r'(.*?)(\d+)\.(\w+)$')

        prefixes = []
        numbers = []
        extensions = []

        for image_file in image_files:
            match = pattern.match(image_file)
            if match:
                prefix, number, extension = match.groups()
                prefixes.append(prefix)
                numbers.append(number)
                extensions.append(extension)

        if not prefixes:
            return None, None, None

        common_prefix = prefixes[0]
        extension = extensions[0]
        number_of_zeros = len(numbers[0])

        return common_prefix, extension, number_of_zeros

    def _check_atlas_fit(self, atlas_width, atlas_height, frame_skip, total_frame_count):
        expected_frames = atlas_width * atlas_height
        actual_frames = lib.calculate_required_frames(total_frame_count, frame_skip)

        if actual_frames <= expected_frames:
            return True, localization[self.language]['frames_fit']
        else:
            excess_frames = actual_frames - expected_frames
            if excess_frames == 1:
                message = localization[self.language]['one_frame_wont_fit']
            else:
                message = localization[self.language]['frames_wont_fit'].format(excess_frames)

            min_skip = 0
            while lib.calculate_required_frames(total_frame_count, min_skip) > expected_frames:
                min_skip += 1

            message += localization[self.language]['try_adjusting']
            message += localization[self.language]['min_skip'].format(min_skip)

            return False, message

    def start_processing(self):
        directory = self.directory
        file_prefix = self.filePrefixInput.get()
        num_digits = self.numDigitsInput.get()
        extension = self.fileExtensionInput.get()

        if directory is None or file_prefix is None or num_digits is None or extension is None:
            return

        pattern = os.path.join(directory, f"{file_prefix}%0{int(num_digits)}d.{extension}")

        frames = lib.load_frames(pattern)
        if not frames:
            messagebox.showerror(localization[self.language]['error'], localization[self.language]['no_frames_loaded'])
            return

        atlas_width = int(self.atlasWidthInput.get())
        atlas_height = int(self.atlasHeightInput.get())
        frame_skip = int(self.frameSkipInput.get())

        can_fit, error_message = self._check_atlas_fit(atlas_width, atlas_height, frame_skip, len(frames))
        if not can_fit:
            messagebox.showerror(localization[self.language]['error'], error_message)
            return

        result = lib.encode_atlas(frames, atlas_width, atlas_height, frame_skip)

        self.color_atlas = result.color_atlas
        self.motion_atlas = result.motion_atlas
        self.flow_directions = result.flow_directions

        self.motionVectorInputU.config(state=tk.NORMAL)
        self.motionVectorInputU.delete(0, tk.END)
        self.motionVectorInputU.insert(0, result.strength_u)
        self.motionVectorInputU.config(state='readonly')

        self.motionVectorInputV.config(state=tk.NORMAL)
        self.motionVectorInputV.delete(0, tk.END)
        self.motionVectorInputV.insert(0, result.strength_v)
        self.motionVectorInputV.config(state='readonly')

        self.display_image(self.color_atlas, self.color_canvas, self.colorFrame)
        self.display_image(self.motion_atlas, self.motion_canvas, self.motionFrame)
        self.display_image(self.flow_directions, self.direction_canvas, self.directionFrame)

    def save_results(self):
        out_dir = filedialog.askdirectory()
        if not out_dir:
            return  # User cancelled the dialog

        out_name = 'flow'

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        cv2.imwrite(os.path.join(out_dir, f'{out_name}_color.png'), self.color_atlas)
        cv2.imwrite(os.path.join(out_dir, f'{out_name}_motion.png'), self.motion_atlas)
        messagebox.showinfo(localization[self.language]['title'], localization[self.language]['results_saved'])

if __name__ == '__main__':
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()

