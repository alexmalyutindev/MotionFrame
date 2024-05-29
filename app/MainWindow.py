# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFormLayout,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QRadioButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_MotionFrame(object):
    def setupUi(self, MotionFrame):
        if not MotionFrame.objectName():
            MotionFrame.setObjectName(u"MotionFrame")
        MotionFrame.resize(923, 461)
        self.central = QWidget(MotionFrame)
        self.central.setObjectName(u"central")
        self.horizontalLayout = QHBoxLayout(self.central)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.layout_left = QVBoxLayout()
        self.layout_left.setObjectName(u"layout_left")
        self.form_config = QFormLayout()
        self.form_config.setObjectName(u"form_config")
        self.form_config.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.label_language = QLabel(self.central)
        self.label_language.setObjectName(u"label_language")
        self.label_language.setTextFormat(Qt.PlainText)

        self.form_config.setWidget(0, QFormLayout.LabelRole, self.label_language)

        self.layout_language = QHBoxLayout()
        self.layout_language.setObjectName(u"layout_language")
        self.radio_button_language_english = QRadioButton(self.central)
        self.radio_button_language_english.setObjectName(u"radio_button_language_english")
        self.radio_button_language_english.setText(u"English")
        self.radio_button_language_english.setChecked(True)

        self.layout_language.addWidget(self.radio_button_language_english)

        self.radio_button_language_japanese = QRadioButton(self.central)
        self.radio_button_language_japanese.setObjectName(u"radio_button_language_japanese")
        self.radio_button_language_japanese.setText(u"\u65e5\u672c\u8a9e")

        self.layout_language.addWidget(self.radio_button_language_japanese)


        self.form_config.setLayout(0, QFormLayout.FieldRole, self.layout_language)

        self.label_directory = QLabel(self.central)
        self.label_directory.setObjectName(u"label_directory")
        self.label_directory.setTextFormat(Qt.PlainText)

        self.form_config.setWidget(1, QFormLayout.LabelRole, self.label_directory)

        self.layout_directory = QVBoxLayout()
        self.layout_directory.setObjectName(u"layout_directory")
        self.text_directory = QLineEdit(self.central)
        self.text_directory.setObjectName(u"text_directory")

        self.layout_directory.addWidget(self.text_directory)

        self.button_directory_browse = QPushButton(self.central)
        self.button_directory_browse.setObjectName(u"button_directory_browse")
        self.button_directory_browse.setMaximumSize(QSize(221, 32))

        self.layout_directory.addWidget(self.button_directory_browse)


        self.form_config.setLayout(1, QFormLayout.FieldRole, self.layout_directory)

        self.label_file_prefix = QLabel(self.central)
        self.label_file_prefix.setObjectName(u"label_file_prefix")
        self.label_file_prefix.setTextFormat(Qt.PlainText)

        self.form_config.setWidget(2, QFormLayout.LabelRole, self.label_file_prefix)

        self.text_file_prefix = QLineEdit(self.central)
        self.text_file_prefix.setObjectName(u"text_file_prefix")
        self.text_file_prefix.setText(u"flipbook_")

        self.form_config.setWidget(2, QFormLayout.FieldRole, self.text_file_prefix)

        self.label_sequence_digits = QLabel(self.central)
        self.label_sequence_digits.setObjectName(u"label_sequence_digits")
        self.label_sequence_digits.setTextFormat(Qt.PlainText)

        self.form_config.setWidget(3, QFormLayout.LabelRole, self.label_sequence_digits)

        self.number_sequence_digits = QSpinBox(self.central)
        self.number_sequence_digits.setObjectName(u"number_sequence_digits")
        self.number_sequence_digits.setMinimum(1)
        self.number_sequence_digits.setMaximum(10)
        self.number_sequence_digits.setValue(3)

        self.form_config.setWidget(3, QFormLayout.FieldRole, self.number_sequence_digits)

        self.label_extension = QLabel(self.central)
        self.label_extension.setObjectName(u"label_extension")
        self.label_extension.setTextFormat(Qt.PlainText)

        self.form_config.setWidget(4, QFormLayout.LabelRole, self.label_extension)

        self.text_extension = QLineEdit(self.central)
        self.text_extension.setObjectName(u"text_extension")
        self.text_extension.setText(u"tga")

        self.form_config.setWidget(4, QFormLayout.FieldRole, self.text_extension)

        self.label_atlas_width = QLabel(self.central)
        self.label_atlas_width.setObjectName(u"label_atlas_width")
        self.label_atlas_width.setTextFormat(Qt.PlainText)

        self.form_config.setWidget(5, QFormLayout.LabelRole, self.label_atlas_width)

        self.number_atlas_width = QSpinBox(self.central)
        self.number_atlas_width.setObjectName(u"number_atlas_width")
        self.number_atlas_width.setMinimum(1)
        self.number_atlas_width.setMaximum(64)
        self.number_atlas_width.setValue(8)

        self.form_config.setWidget(5, QFormLayout.FieldRole, self.number_atlas_width)

        self.label_atlas_height = QLabel(self.central)
        self.label_atlas_height.setObjectName(u"label_atlas_height")
        self.label_atlas_height.setTextFormat(Qt.PlainText)

        self.form_config.setWidget(6, QFormLayout.LabelRole, self.label_atlas_height)

        self.number_atlas_height = QSpinBox(self.central)
        self.number_atlas_height.setObjectName(u"number_atlas_height")
        self.number_atlas_height.setMinimum(1)
        self.number_atlas_height.setMaximum(64)
        self.number_atlas_height.setValue(8)

        self.form_config.setWidget(6, QFormLayout.FieldRole, self.number_atlas_height)

        self.label_frame_skip = QLabel(self.central)
        self.label_frame_skip.setObjectName(u"label_frame_skip")
        self.label_frame_skip.setTextFormat(Qt.PlainText)

        self.form_config.setWidget(7, QFormLayout.LabelRole, self.label_frame_skip)

        self.number_frame_skip = QSpinBox(self.central)
        self.number_frame_skip.setObjectName(u"number_frame_skip")
        self.number_frame_skip.setMinimum(0)
        self.number_frame_skip.setMaximum(128)
        self.number_frame_skip.setValue(0)

        self.form_config.setWidget(7, QFormLayout.FieldRole, self.number_frame_skip)

        self.label_scale = QLabel(self.central)
        self.label_scale.setObjectName(u"label_scale")
        self.label_scale.setTextFormat(Qt.PlainText)

        self.form_config.setWidget(8, QFormLayout.LabelRole, self.label_scale)

        self.number_scale = QDoubleSpinBox(self.central)
        self.number_scale.setObjectName(u"number_scale")
        self.number_scale.setMaximum(1.000000000000000)
        self.number_scale.setSingleStep(0.100000000000000)
        self.number_scale.setValue(1.000000000000000)

        self.form_config.setWidget(8, QFormLayout.FieldRole, self.number_scale)

        self.label_motion_vector_encoding = QLabel(self.central)
        self.label_motion_vector_encoding.setObjectName(u"label_motion_vector_encoding")
        self.label_motion_vector_encoding.setTextFormat(Qt.PlainText)

        self.form_config.setWidget(9, QFormLayout.LabelRole, self.label_motion_vector_encoding)

        self.combo_motion_vector_encoding = QComboBox(self.central)
        self.combo_motion_vector_encoding.addItem(u"R8G8 Remapped to 0-1")
        self.combo_motion_vector_encoding.addItem(u"SideFX Labs R8G8 Encoding")
        self.combo_motion_vector_encoding.addItem(u"R16G16")
        self.combo_motion_vector_encoding.setObjectName(u"combo_motion_vector_encoding")

        self.form_config.setWidget(9, QFormLayout.FieldRole, self.combo_motion_vector_encoding)


        self.layout_left.addLayout(self.form_config)

        self.button_generate = QPushButton(self.central)
        self.button_generate.setObjectName(u"button_generate")

        self.layout_left.addWidget(self.button_generate)

        self.label_motion_vector = QLabel(self.central)
        self.label_motion_vector.setObjectName(u"label_motion_vector")

        self.layout_left.addWidget(self.label_motion_vector)

        self.left_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_left.addItem(self.left_spacer)


        self.horizontalLayout.addLayout(self.layout_left)

        self.layout_right = QVBoxLayout()
        self.layout_right.setObjectName(u"layout_right")
        self.tabs_result = QTabWidget(self.central)
        self.tabs_result.setObjectName(u"tabs_result")
        self.tabs_result.setTabPosition(QTabWidget.North)
        self.tabs_result.setTabShape(QTabWidget.Rounded)
        self.tabs_result.setUsesScrollButtons(False)
        self.tab_color = QWidget()
        self.tab_color.setObjectName(u"tab_color")
        self.gridLayout = QGridLayout(self.tab_color)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scroll_color = QScrollArea(self.tab_color)
        self.scroll_color.setObjectName(u"scroll_color")
        self.scroll_color.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_color.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_color.setWidgetResizable(True)
        self.scroll_content_color = QWidget()
        self.scroll_content_color.setObjectName(u"scroll_content_color")
        self.scroll_content_color.setGeometry(QRect(0, 0, 420, 114))
        self.gridLayout_2 = QGridLayout(self.scroll_content_color)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_color_atlas_image = QLabel(self.scroll_content_color)
        self.label_color_atlas_image.setObjectName(u"label_color_atlas_image")

        self.gridLayout_2.addWidget(self.label_color_atlas_image, 0, 0, 1, 1)

        self.scroll_color.setWidget(self.scroll_content_color)

        self.gridLayout.addWidget(self.scroll_color, 0, 0, 1, 1)

        self.tabs_result.addTab(self.tab_color, "")
        self.tab_motion_vector = QWidget()
        self.tab_motion_vector.setObjectName(u"tab_motion_vector")
        self.gridLayout_3 = QGridLayout(self.tab_motion_vector)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.scroll_motion_vector = QScrollArea(self.tab_motion_vector)
        self.scroll_motion_vector.setObjectName(u"scroll_motion_vector")
        self.scroll_motion_vector.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_motion_vector.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_motion_vector.setWidgetResizable(True)
        self.scroll_content_motion_vector = QWidget()
        self.scroll_content_motion_vector.setObjectName(u"scroll_content_motion_vector")
        self.scroll_content_motion_vector.setGeometry(QRect(0, 0, 420, 114))
        self.gridLayout_4 = QGridLayout(self.scroll_content_motion_vector)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_motion_vector_image = QLabel(self.scroll_content_motion_vector)
        self.label_motion_vector_image.setObjectName(u"label_motion_vector_image")

        self.gridLayout_4.addWidget(self.label_motion_vector_image, 0, 0, 1, 1)

        self.scroll_motion_vector.setWidget(self.scroll_content_motion_vector)

        self.gridLayout_3.addWidget(self.scroll_motion_vector, 0, 0, 1, 1)

        self.tabs_result.addTab(self.tab_motion_vector, "")
        self.tab_visualization = QWidget()
        self.tab_visualization.setObjectName(u"tab_visualization")
        self.gridLayout_6 = QGridLayout(self.tab_visualization)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.scroll_visualization = QScrollArea(self.tab_visualization)
        self.scroll_visualization.setObjectName(u"scroll_visualization")
        self.scroll_visualization.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_visualization.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_visualization.setWidgetResizable(True)
        self.scroll_content_motion_vector_2 = QWidget()
        self.scroll_content_motion_vector_2.setObjectName(u"scroll_content_motion_vector_2")
        self.scroll_content_motion_vector_2.setGeometry(QRect(0, 0, 420, 114))
        self.gridLayout_5 = QGridLayout(self.scroll_content_motion_vector_2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_visualization_image = QLabel(self.scroll_content_motion_vector_2)
        self.label_visualization_image.setObjectName(u"label_visualization_image")

        self.gridLayout_5.addWidget(self.label_visualization_image, 0, 0, 1, 1)

        self.scroll_visualization.setWidget(self.scroll_content_motion_vector_2)

        self.gridLayout_6.addWidget(self.scroll_visualization, 0, 0, 1, 1)

        self.tabs_result.addTab(self.tab_visualization, "")

        self.layout_right.addWidget(self.tabs_result)

        self.form_result = QFormLayout()
        self.form_result.setObjectName(u"form_result")
        self.label_motion_strength = QLabel(self.central)
        self.label_motion_strength.setObjectName(u"label_motion_strength")
        self.label_motion_strength.setTextFormat(Qt.PlainText)

        self.form_result.setWidget(3, QFormLayout.LabelRole, self.label_motion_strength)

        self.label_discarded_trailing_frames = QLabel(self.central)
        self.label_discarded_trailing_frames.setObjectName(u"label_discarded_trailing_frames")
        self.label_discarded_trailing_frames.setTextFormat(Qt.PlainText)

        self.form_result.setWidget(1, QFormLayout.LabelRole, self.label_discarded_trailing_frames)

        self.label_discarded_trailing_frames_value = QLabel(self.central)
        self.label_discarded_trailing_frames_value.setObjectName(u"label_discarded_trailing_frames_value")
        self.label_discarded_trailing_frames_value.setText(u"0")
        self.label_discarded_trailing_frames_value.setTextFormat(Qt.PlainText)

        self.form_result.setWidget(1, QFormLayout.FieldRole, self.label_discarded_trailing_frames_value)

        self.layout_motion_strength = QHBoxLayout()
        self.layout_motion_strength.setObjectName(u"layout_motion_strength")
        self.text_motion_strength = QLineEdit(self.central)
        self.text_motion_strength.setObjectName(u"text_motion_strength")
        self.text_motion_strength.setReadOnly(True)

        self.layout_motion_strength.addWidget(self.text_motion_strength)

        self.button_copy_motion_strength = QPushButton(self.central)
        self.button_copy_motion_strength.setObjectName(u"button_copy_motion_strength")

        self.layout_motion_strength.addWidget(self.button_copy_motion_strength)


        self.form_result.setLayout(3, QFormLayout.FieldRole, self.layout_motion_strength)

        self.label_total_frames = QLabel(self.central)
        self.label_total_frames.setObjectName(u"label_total_frames")

        self.form_result.setWidget(0, QFormLayout.LabelRole, self.label_total_frames)

        self.label_total_frames_value = QLabel(self.central)
        self.label_total_frames_value.setObjectName(u"label_total_frames_value")
        self.label_total_frames_value.setText(u"0")

        self.form_result.setWidget(0, QFormLayout.FieldRole, self.label_total_frames_value)


        self.layout_right.addLayout(self.form_result)

        self.button_save = QPushButton(self.central)
        self.button_save.setObjectName(u"button_save")

        self.layout_right.addWidget(self.button_save)


        self.horizontalLayout.addLayout(self.layout_right)

        self.horizontalLayout.setStretch(1, 1)
        MotionFrame.setCentralWidget(self.central)

        self.retranslateUi(MotionFrame)

        self.tabs_result.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MotionFrame)
    # setupUi

    def retranslateUi(self, MotionFrame):
        MotionFrame.setWindowTitle(QCoreApplication.translate("MotionFrame", u"MainWindow", None))
        self.label_language.setText(QCoreApplication.translate("MotionFrame", u"Language:", None))
        self.label_directory.setText(QCoreApplication.translate("MotionFrame", u"Directory:", None))
        self.button_directory_browse.setText(QCoreApplication.translate("MotionFrame", u"Browse\u2026", None))
        self.label_file_prefix.setText(QCoreApplication.translate("MotionFrame", u"File Prefix:", None))
        self.label_sequence_digits.setText(QCoreApplication.translate("MotionFrame", u"Sequence Digits:", None))
        self.label_extension.setText(QCoreApplication.translate("MotionFrame", u"Extension:", None))
        self.label_atlas_width.setText(QCoreApplication.translate("MotionFrame", u"Atlas Width:", None))
        self.label_atlas_height.setText(QCoreApplication.translate("MotionFrame", u"Atlas Height:", None))
        self.label_frame_skip.setText(QCoreApplication.translate("MotionFrame", u"Frame Skip:", None))
        self.label_scale.setText(QCoreApplication.translate("MotionFrame", u"Motion Texture Scale:", None))
        self.label_motion_vector_encoding.setText(QCoreApplication.translate("MotionFrame", u"Motion Vector Encoding:", None))

        self.button_generate.setText(QCoreApplication.translate("MotionFrame", u"Generate", None))
        self.label_motion_vector.setText("")
        self.label_color_atlas_image.setText("")
        self.tabs_result.setTabText(self.tabs_result.indexOf(self.tab_color), QCoreApplication.translate("MotionFrame", u"Color", None))
        self.label_motion_vector_image.setText("")
        self.tabs_result.setTabText(self.tabs_result.indexOf(self.tab_motion_vector), QCoreApplication.translate("MotionFrame", u"Motion Vector", None))
        self.label_visualization_image.setText("")
        self.tabs_result.setTabText(self.tabs_result.indexOf(self.tab_visualization), QCoreApplication.translate("MotionFrame", u"Visualization", None))
        self.label_motion_strength.setText(QCoreApplication.translate("MotionFrame", u"Motion Strength:", None))
        self.label_discarded_trailing_frames.setText(QCoreApplication.translate("MotionFrame", u"Discarded Trailing Frames:", None))
        self.button_copy_motion_strength.setText(QCoreApplication.translate("MotionFrame", u"Copy", None))
        self.label_total_frames.setText(QCoreApplication.translate("MotionFrame", u"Total Frames:", None))
        self.button_save.setText(QCoreApplication.translate("MotionFrame", u"Save", None))
    # retranslateUi

