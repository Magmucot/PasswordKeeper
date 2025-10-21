import sys
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QComboBox,
    QLabel,
    QStackedWidget,
    QScrollArea,
    QMessageBox,
    QFrame,
    QGridLayout,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QAbstractSpinBox,
)
import resources  # noqa: F401
from PySide6.QtGui import QIcon, QCursor, QAction, QKeySequence
from PySide6.QtCore import QSize, Qt, QEvent
from OOP1 import Shifrator
from OOP4 import (
    Characters,
    StrengthToEntropy,
    generate_password,
    get_entropy,
    CHARACTER_NUMBER,
    GENERATE_PASSWORD,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мультитул")
        self.resize(400, 400)
        self.setMinimumSize(QSize(300, 400))
        self.setWindowIcon(QIcon(":/icons/icon.png"))
        central_widget = QWidget()

        self.setStyleSheet(
            """QWidget {background-color: #121212; color: white; font-family: Work Sans;
                            font-size: 12pt; font-weight: 600;}
                            QPushButton {background-color: #282828; border:none;}
                            QPushButton:hover {background-color: #888;}
                            QPushButton:pressed {background-color: #AAA;}
                            QComboBox {background-color: #282828; border: white 1px;}
                            QLineEdit, QTextEdit {background-color: #282828; border: white 1px;}
                            QLabel {color: #888; border: solid white 1px}"""
        )

        self.btn_active_style = "QPushButton { background-color: #A04602; border-radius: 2px; border: none; }"
        self.btn_inactive_style = "QPushButton { background-color: #FF8C00; border-radius: 2px; border: none; }"

        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.btn_style = """QPushButton {color: black;background-color: #FF8C00; border-radius: 2px; border: none;}
            QPushButton:hover {background-color: #E07B00; border: none;}
            QPushButton:pressed {background-color: #CC6A00;border: none;}"""

        self.ans = ""
        self.up_layout = QHBoxLayout()

        icon1 = QIcon(":/icons/vpnkey_black.png")
        self.btn_pass = QPushButton()
        self.btn_pass.setIcon(icon1)
        self.btn_pass.setIconSize(QSize(32, 32))
        self.btn_pass.setFixedSize(40, 40)
        self.btn_pass.setStyleSheet(
            """QPushButton {background-color: #FF8C00; border-radius: 2px;border: none;}
            QPushButton:hover {background-color: #E07B00;border: none;}
            QPushButton:pressed {background-color: #CC6A00;border: none;}"""
        )

        icon = QIcon(":/icons/fingerprint.png")
        self.btn_shifr = QPushButton()
        self.btn_shifr.setStyleSheet(self.btn_style)
        self.btn_shifr.setIcon(icon)
        self.btn_shifr.setIconSize(QSize(32, 32))
        self.btn_shifr.setFixedSize(40, 40)

        self.up_layout.addWidget(self.btn_shifr)
        self.up_layout.addWidget(self.btn_pass)
        self.up_layout.addStretch()

        self.main_layout.addLayout(self.up_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        self.main_layout.addWidget(separator)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.shifr_page()
        self.pass_page()

        self.btn_pass.clicked.connect(lambda: self.show_page(0, self.btn_pass))
        self.btn_shifr.clicked.connect(lambda: self.show_page(1, self.btn_shifr))
        self.show_page(1, self.btn_shifr)

    def copy(self, text):
        QApplication.clipboard().setText(text)

    def show_page(self, page_index, active_button):
        self.stack.setCurrentIndex(page_index)
        buttons = [self.btn_pass, self.btn_shifr]
        for button in buttons:
            button.setStyleSheet(
                self.btn_active_style
                if button == active_button
                else self.btn_inactive_style
            )

    def pass_page(self):
        page = QWidget()
        page.setStyleSheet("""
            QWidget {font-size: 16pt; font-weight: 600;}
            QPushButton {
                border-radius: 5px;
                background-color: transparent;
                border: 2px solid gray;
            }
            QPushButton:pressed {border: 3px solid #FF8C00;}
            QPushButton:checked {
                background-color: #010; border: 3px solid #FF8C00;}
            QSpinBox {
                border: 2px solid gray; border-radius: 5px;
                background: transparent;padding: 5px;}
            QSpinBox:hover {
                border-color: #FF8C00;
            }
        """)
        self.gridLayout = QGridLayout(page)
        self.layout_length = QHBoxLayout()
        self.slider_length = QSlider(page)
        self.slider_length.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.slider_length.setStyleSheet("""
            QSlider::groove:horizontal {
                background-color: transparent;
                height: 5px;}
            QSlider::sub-page:horizontal {
                background-color: #FF8C00;}
            QSlider::add-page:horizontal {
                background-color: gray;}
            QSlider::handle:horizontal {
                background-color: orange; width: 22px;
                border-radius: 10px; margin-top: -8px;
                margin-bottom: -8px;}""")
        self.slider_length.setMaximum(200)
        self.slider_length.setValue(12)
        self.slider_length.setOrientation(Qt.Orientation.Horizontal)

        self.layout_length.addWidget(self.slider_length)

        self.cnt_length = QSpinBox(page)
        self.cnt_length.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cnt_length.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cnt_length.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.cnt_length.setMaximum(200)

        self.layout_length.addWidget(self.cnt_length)

        self.gridLayout.addLayout(self.layout_length, 3, 0, 1, 1)

        self.layout_info = QHBoxLayout()
        self.label_diff = QLabel(page)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_diff.sizePolicy().hasHeightForWidth())
        self.label_diff.setSizePolicy(sizePolicy)
        self.label_diff.setStyleSheet("font-size: 12pt; font-weight: 600;")
        self.label_diff.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout_info.addWidget(self.label_diff)

        self.label_entropy = QLabel(page)
        sizePolicy.setHeightForWidth(
            self.label_entropy.sizePolicy().hasHeightForWidth()
        )
        self.label_entropy.setSizePolicy(sizePolicy)
        self.label_entropy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_entropy.setStyleSheet("font-size: 12pt; font-weight: 600;")

        self.layout_info.addWidget(self.label_entropy)

        self.gridLayout.addLayout(self.layout_info, 2, 0, 1, 1)

        self.layout_password = QHBoxLayout()
        self.frame = QFrame(page)
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy1)
        self.frame.setStyleSheet("""
            QFrame {
                border: 2px solid gray;
                border-radius: 5px;
                margin-right: 0;}
            QFrame:hover {
                border-color: #FF8C00;}""")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.password = QLineEdit(self.frame)
        sizePolicy1.setHeightForWidth(self.password.sizePolicy().hasHeightForWidth())
        self.password.setSizePolicy(sizePolicy1)
        self.password.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                margin: 0;
                font-size: 20pt;}""")
        self.horizontalLayout.addWidget(self.password)

        self.btn_visibility = QPushButton(self.frame)
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.btn_visibility.sizePolicy().hasHeightForWidth()
        )
        self.btn_visibility.setSizePolicy(sizePolicy2)
        self.btn_visibility.setStyleSheet("""
            QPushButton {
                border: none;
                margin: 0;
                background-color: transparent;}""")
        icon = QIcon()
        icon.addFile(
            ":/icons/visibility_off_white.svg",
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        icon.addFile(
            ":/icons/visibility_white.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On
        )
        icon.addFile(
            ":/icons/visibility_white.svg",
            QSize(),
            QIcon.Mode.Disabled,
            QIcon.State.Off,
        )
        icon.addFile(
            ":/icons/visibility_off_white.svg",
            QSize(),
            QIcon.Mode.Disabled,
            QIcon.State.On,
        )
        self.btn_visibility.setIcon(icon)
        self.btn_visibility.setIconSize(QSize(35, 35))
        self.btn_visibility.setCheckable(True)
        self.btn_visibility.clicked.connect(self.change_visibility)

        self.horizontalLayout.addWidget(self.btn_visibility)

        self.layout_password.addWidget(self.frame)

        self.btn_refresh = QPushButton(page)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.btn_refresh.sizePolicy().hasHeightForWidth())
        self.btn_refresh.setSizePolicy(sizePolicy3)
        icon1 = QIcon()
        icon1.addFile(
            ":/icons/refresh_white.svg", QSize(), QIcon.Mode.Disabled, QIcon.State.On
        )
        self.btn_refresh.setIcon(icon1)
        self.btn_refresh.setIconSize(QSize(52, 52))

        self.layout_password.addWidget(self.btn_refresh)

        self.btn_copy = QPushButton(page)
        sizePolicy3.setHeightForWidth(self.btn_copy.sizePolicy().hasHeightForWidth())
        self.btn_copy.setSizePolicy(sizePolicy3)
        icon2 = QIcon()
        icon2.addFile(
            ":/icons/copy_white.svg", QSize(), QIcon.Mode.Disabled, QIcon.State.On
        )
        self.btn_copy.setIcon(icon2)
        self.btn_copy.setIconSize(QSize(52, 52))

        self.layout_password.addWidget(self.btn_copy)

        self.gridLayout.addLayout(self.layout_password, 1, 0, 1, 1)

        self.icon_lock = QPushButton(page)
        self.icon_lock.setEnabled(False)
        self.icon_lock.setStyleSheet("""border: none""")
        icon1 = QIcon()
        icon1.addFile(
            ":/icons/lock_white.svg", QSize(), QIcon.Mode.Disabled, QIcon.State.On
        )
        self.icon_lock.setIcon(icon1)
        self.icon_lock.setIconSize(QSize(70, 70))

        self.gridLayout.addWidget(self.icon_lock, 0, 0, 1, 1)

        self.layout_chars = QHBoxLayout()
        self.layout_lower = QVBoxLayout()
        self.btn_lower = QPushButton("a-z", page)
        sizePolicy1.setHeightForWidth(self.btn_lower.sizePolicy().hasHeightForWidth())
        self.btn_lower.setSizePolicy(sizePolicy1)
        self.btn_lower.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_lower.setCheckable(True)
        self.btn_lower.setChecked(True)

        self.layout_lower.addWidget(self.btn_lower)

        self.cnt_lower = QSpinBox(page)
        sizePolicy1.setHeightForWidth(self.cnt_lower.sizePolicy().hasHeightForWidth())
        self.cnt_lower.setSizePolicy(sizePolicy1)
        self.cnt_lower.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cnt_lower.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cnt_lower.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.cnt_lower.setMaximum(200)

        self.layout_lower.addWidget(self.cnt_lower)

        self.layout_chars.addLayout(self.layout_lower)

        self.verticalLayout = QVBoxLayout()
        self.btn_up = QPushButton("A-Z", page)
        self.btn_up.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_up.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.btn_up.setCheckable(True)
        self.btn_up.setChecked(True)
        self.verticalLayout.addWidget(self.btn_up)

        self.cnt_up = QSpinBox(page)
        sizePolicy1.setHeightForWidth(self.cnt_up.sizePolicy().hasHeightForWidth())
        self.cnt_up.setSizePolicy(sizePolicy1)
        self.cnt_up.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cnt_up.setFrame(True)
        self.cnt_up.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cnt_up.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.cnt_up.setMaximum(200)

        self.verticalLayout.addWidget(self.cnt_up)

        self.layout_chars.addLayout(self.verticalLayout)

        self.verticalLayout_8 = QVBoxLayout()
        self.btn_nums = QPushButton("0-9", page)
        self.btn_nums.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_nums.setCheckable(True)
        self.btn_nums.setChecked(True)

        self.verticalLayout_8.addWidget(self.btn_nums)

        self.cnt_nums = QSpinBox(page)
        sizePolicy1.setHeightForWidth(self.cnt_nums.sizePolicy().hasHeightForWidth())
        self.cnt_nums.setSizePolicy(sizePolicy1)
        self.cnt_nums.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cnt_nums.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cnt_nums.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.cnt_nums.setMaximum(999)

        self.verticalLayout_8.addWidget(self.cnt_nums)

        self.layout_chars.addLayout(self.verticalLayout_8)

        self.verticalLayout_9 = QVBoxLayout()
        self.btn_spec = QPushButton("$#*", page)
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.btn_spec.sizePolicy().hasHeightForWidth())
        self.btn_spec.setSizePolicy(sizePolicy4)
        self.btn_spec.setMinimumSize(QSize(0, 33))
        self.btn_spec.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_spec.setCheckable(True)

        self.verticalLayout_9.addWidget(self.btn_spec)

        self.cnt_spec = QSpinBox(page)
        sizePolicy1.setHeightForWidth(self.cnt_spec.sizePolicy().hasHeightForWidth())
        self.cnt_spec.setSizePolicy(sizePolicy1)
        self.cnt_spec.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cnt_spec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cnt_spec.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.cnt_spec.setMaximum(999)

        self.verticalLayout_9.addWidget(self.cnt_spec)

        self.layout_chars.addLayout(self.verticalLayout_9)

        self.gridLayout.addLayout(self.layout_chars, 4, 0, 1, 1)
        self.connect_slider_to_spinbox()
        for btn in GENERATE_PASSWORD:
            getattr(self, btn).clicked.connect(self.set_password)
        self.btn_copy.clicked.connect(lambda: self.copy(self.password.text()))
        self.stack.addWidget(page)

    def connect_slider_to_spinbox(self):
        self.slider_length.valueChanged.connect(self.cnt_length.setValue)
        self.cnt_length.valueChanged.connect(self.slider_length.setValue)
        self.cnt_length.valueChanged.connect(self.set_password)

    def get_chars(self) -> str:
        chars = ""

        for btn in Characters:
            if getattr(self, btn.name).isChecked():
                chars += btn.value

        return chars

    def set_password(self) -> None:
        try:
            self.password.setText(
                generate_password(
                    length=self.slider_length.value(), chars=self.get_chars()
                )
            )
        except IndexError:
            self.password.clear()
        self.set_entropy()
        self.set_diff()

    def set_diff(self) -> None:
        length = len(self.password.text())
        char_num = self.get_character_number()

        for strength in StrengthToEntropy:
            if get_entropy(length, char_num) >= strength.value:
                self.label_diff.setText(f"Сложность: {strength.name}")

    def change_visibility(self) -> None:
        if self.btn_visibility.isChecked():
            self.password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password.setEchoMode(QLineEdit.EchoMode.Password)

    def get_character_number(self) -> int:
        num = 0

        for btn in CHARACTER_NUMBER.items():
            if getattr(self, btn[0]).isChecked():
                num += btn[1]
        return num

    def set_entropy(self) -> None:
        length = len(self.password.text())
        char_num = self.get_character_number()

        self.label_entropy.setText(f"Entropy: {get_entropy(length, char_num)} bit")

    def shifr_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Введите текст")
        layout.addWidget(self.input_text)

        input_deystv = QLabel("Выберите действие (шифровка или дешифровка):")
        layout.addWidget(input_deystv)

        self.combo_deystv = QComboBox()
        self.combo_deystv.addItem("Шифровать")
        self.combo_deystv.addItem("Дешифровать")
        layout.addWidget(self.combo_deystv)

        input_tip = QLabel("Выберите шифр (Цезарь или Виженер):")
        layout.addWidget(input_tip)

        self.combo_tip = QComboBox()
        self.combo_tip.addItem("Цезарь")
        self.combo_tip.addItem("Виженер")
        layout.addWidget(self.combo_tip)

        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("Введите ключ")
        layout.addWidget(self.input_key)

        layout_btns = QHBoxLayout()
        btn = QPushButton("Выполнить")
        btn.setFixedHeight(20)
        btn.setStyleSheet(
            """QPushButton {color: black; background-color: #63F113; border-radius: 2px; border: none; }
            QPushButton:hover { background-color: #309112; }"""
        )
        btn_copy = QPushButton()
        btn_copy.setStyleSheet("""
            QPushButton {
                border-radius: 5px;background-color: #888;
                border: 2px solid gray;}
            QPushButton:hover { border: 2px solid #333; }""")
        icon = QIcon(":/icons/copy_black.svg")
        btn_copy.setIcon(icon)
        btn_copy.setFixedHeight(20)
        policy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        btn_copy.setSizePolicy(policy)
        layout_btns.addWidget(btn)
        layout_btns.addWidget(btn_copy)
        btn.clicked.connect(self.btn_shifr_click)
        btn_copy.clicked.connect(lambda: self.copy(self.res_output.toPlainText()))
        layout.addLayout(layout_btns)

        self.res_output = QTextEdit()
        self.res_output.setPlaceholderText("Результат")
        self.res_output.setReadOnly(True)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.res_output)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        self.stack.addWidget(page)

    def btn_shifr_click(self):
        stor = self.combo_deystv.currentText()
        tip = self.combo_tip.currentText()
        text = self.input_text.toPlainText()
        key = self.input_key.text()
        if not text or not stor or not tip or not key:
            QMessageBox.warning(self, "Ошибка!", "Ошибка!\nЗаполните все поля!")
            return
        if tip == "Цезарь" and not key.isdigit():
            QMessageBox.warning(
                self, "Ошибка!", "Ошибка!\nКлюч для Цезаря должен быть целым числом!"
            )
            return
        shifrator = Shifrator(text, key)
        res = shifrator.opred(stor, tip)
        self.res_output.setText(res)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
