import sys
import os
import resources  # noqa: F401
from PyQt6.QtCore import QSize, Qt, QUrl
from PyQt6.QtGui import QCursor, QIcon, QAction, QDesktopServices
from PyQt6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QSplitter,
    QListWidget,
    QToolBar,
    QSpacerItem,
    QInputDialog,
)
from Shifrator import Shifrator
from PasswordGen import (
    CHARACTER_NUMBER,
    GENERATE_PASSWORD,
    Characters,
    StrengthToEntropy,
    generate_password,
    get_entropy,
)
from PasswordManager import PasswordManager, PasswordIncorrectError, InitializationError


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Менеджер паролей")
        self.resize(450, 500)
        self.setMinimumSize(QSize(450, 450))
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

        self.orange_btn_style = """QPushButton {background-color: #FF8C00; border-radius: 2px;border: none;}
            QPushButton:hover {background-color: #E07B00;border: none;}
            QPushButton:pressed {background-color: #CC6A00;border: none;}"""

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

        icon = QIcon(":/icons/fingerprint.png")
        self.btn_shifr = QPushButton()
        self.btn_shifr.setStyleSheet(self.btn_style)
        self.btn_shifr.setIcon(icon)
        self.btn_shifr.setIconSize(QSize(32, 32))
        self.btn_shifr.setFixedSize(40, 40)
        self.btn_shifr.setStyleSheet(self.orange_btn_style)

        icon1 = QIcon(":/icons/vpnkey_black.png")
        self.btn_pass = QPushButton()
        self.btn_pass.setIcon(icon1)
        self.btn_pass.setIconSize(QSize(32, 32))
        self.btn_pass.setFixedSize(40, 40)
        self.btn_pass.setStyleSheet(self.orange_btn_style)

        icon2 = QIcon(":/icons/folder_black.svg")
        self.btn_pass_man = QPushButton()
        self.btn_pass_man.setIcon(icon2)
        self.btn_pass_man.setIconSize(QSize(32, 32))
        self.btn_pass_man.setFixedSize(40, 40)
        self.btn_pass_man.setStyleSheet(self.orange_btn_style)

        self.up_layout.addWidget(self.btn_pass)
        self.up_layout.addWidget(self.btn_pass_man)
        self.up_layout.addWidget(self.btn_shifr)
        self.up_layout.addStretch()

        self.main_layout.addLayout(self.up_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        self.main_layout.addWidget(separator)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.master_password = ""

        self.pass_page()
        self.pass_manager_page()
        self.shifr_page()

        self.btn_pass.clicked.connect(lambda: self.show_page(0, self.btn_pass))
        self.btn_pass_man.clicked.connect(lambda: self.show_page(1, self.btn_pass_man))
        self.btn_shifr.clicked.connect(lambda: self.show_page(2, self.btn_shifr))

        self.show_page(0, self.btn_pass)

    def copy(self, text):
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(
                self, "Скопировано", "Пароль скопирован в буфер обмена."
            )

    def show_page(self, page_index, active_button):
        self.stack.setCurrentIndex(page_index)
        if page_index == 1:
            self.master_password = str(
                self.ask_master_password(visible=not os.path.exists("passwords.txt"))
            )[::-1]
        buttons = [self.btn_pass, self.btn_pass_man, self.btn_shifr]
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
        for attr in GENERATE_PASSWORD:
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.clicked.connect(self.set_password)
            else:
                print(f"[WARN] Нет виджета: {attr}")

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
        sender = self.sender()
        if sender == self.btn_visibility:
            if sender.isChecked():
                self.password.setEchoMode(QLineEdit.EchoMode.Normal)
            else:
                self.password.setEchoMode(QLineEdit.EchoMode.Password)
        elif sender == self.show_pass_btn:
            if sender.isChecked():
                self.pass_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            else:
                self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def get_character_number(self) -> int:
        num = 0

        for key, val in CHARACTER_NUMBER.items():
            widget = getattr(self, key, None)
            if widget is not None and widget.isChecked():
                num += val
        return num

    def set_entropy(self) -> None:
        length = len(self.password.text())
        char_num = self.get_character_number()

        self.label_entropy.setText(f"Entropy: {get_entropy(length, char_num)} bit")

    def validate_master_password(self, pwd: str) -> bool:
        return (
            len(pwd) >= 8
            and any(c.islower() for c in pwd)
            and any(c.isupper() for c in pwd)
            and any(c.isdigit() for c in pwd)
        )

    def pass_manager_page(self) -> None:
        """Страница менеджера паролей"""
        page = QWidget()
        toolbar = self._create_toolbar()
        self.dirty = False
        self.entries = {}
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.display_details)
        self.details_widget = self._create_details_panel()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.list_widget)
        splitter.addWidget(self.details_widget)
        splitter.setStretchFactor(1, 2)

        layout = QVBoxLayout(page)
        layout.addWidget(toolbar)
        layout.addWidget(splitter)

        self.stack.addWidget(page)
        self.disable_interface()

    def disable_interface(self):
        self.name_edit.setEnabled(False)
        self.login_edit.setEnabled(False)
        self.pass_edit.setEnabled(False)
        self.link_edit.setEnabled(False)
        self.notes_edit.setEnabled(False)

    def enable_interface(self):
        self.name_edit.setEnabled(True)
        self.login_edit.setEnabled(True)
        self.pass_edit.setEnabled(True)
        self.link_edit.setEnabled(True)
        self.notes_edit.setEnabled(True)

    def ask_master_password(self, visible=False):
        while True:
            if visible:
                pwd, ok = QInputDialog.getText(
                    self,
                    "Мастер-пароль",
                    "Придумайте мастер-пароль\n(минимальная длина пароля - 8 символов и он должен содержать большую, маленькую букву и цифру):",
                )
            else:
                pwd, ok = QInputDialog.getText(
                    self,
                    "Мастер-пароль",
                    "Введите мастер-пароль:",
                    echo=QLineEdit.EchoMode.Password,
                )
            if not ok:
                QMessageBox.information(self, "Выход", "Доступ к хранилищу отменён.")
                self.disable_interface()
                self._clear_details()
                self.list_widget.setEnabled(False)
                return None
            if visible:
                if self.validate_master_password(pwd):
                    self.enable_interface()
                    self.list_widget.setEnabled(True)
                    self._refresh_list()
                    QMessageBox.information(self, "Успех", "Мастер пароль создан!")
                    print("Пароль: ", pwd)
                    return pwd
                else:
                    QMessageBox.information(
                        self,
                        "Ошибка",
                        "Минимальная длина пароля - 8 символов!\nА Также должная присутсвовать большая, маленькая буква и цифра!",
                    )
                    continue
            if self.try_unlock(pwd):
                self.enable_interface()
                self.list_widget.setEnabled(True)
                self.load_vault(pwd)
                QMessageBox.information(self, "Успех", "Хранилище разблокировано.")
                return pwd
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный мастер-пароль!")
                print(self.master_password)
                continue

    def try_unlock(self, password):
        try:
            PasswordManager(password)
            return True
        except (PasswordIncorrectError, InitializationError):
            print("Неверно: ", password)
            return False

    def load_vault(self, password):
        try:
            pass_man = PasswordManager(password)
            self.entries = pass_man.get_storage(password)
        except PasswordIncorrectError:
            print("Неверный пароль")
            print(self.master_password[::-1])
        except InitializationError:
            print("ошибка инициализации")

    def display_details(self, item):
        if not self.try_switch():
            return
        entry = self.entries.get(item.text(), None)
        if not entry:
            return
        if item.text() in self.entries.keys():
            self.curr_entry = item.text().strip()
        else:
            self.curr_entry = None
        self._block_signals(True)
        self.name_edit.setText(self.curr_entry)
        self.link_edit.setText(entry.get("link", ""))
        self.login_edit.setText(entry.get("name", ""))
        self.pass_edit.setText(entry.get("password", ""))
        self.notes_edit.setText(entry.get("notes", ""))
        self._block_signals(False)
        self.dirty = False
        self.disable_interface()

    def _block_signals(self, block: bool):
        """Helper для блокировки/разблокировки сигналов всех редакторов."""
        editors = [self.name_edit, self.login_edit, self.pass_edit, self.link_edit]
        for editor in editors:
            editor.blockSignals(block)
        self.notes_edit.blockSignals(block)

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")

        add_action = QAction("➕", self)
        add_action.triggered.connect(self.add_entry)
        toolbar.addAction(add_action)

        edit_action = QAction("✏", self)
        edit_action.triggered.connect(self.enable_interface)
        toolbar.addAction(edit_action)

        del_action = QAction("🗑", self)
        del_action.triggered.connect(self.delete_entry)
        toolbar.addAction(del_action)

        save_action = QAction("💾", self)
        save_action.triggered.connect(self.save_entry)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self._refresh_list)
        self.search_input.setFixedWidth(200)
        toolbar.addWidget(self.search_input)

        return toolbar

    def _create_details_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок
        self.name_edit = QLineEdit()
        """font = self.name_edit.font()
        font.setPointSize(14)
        font.setBold(True)
        self.name_edit.setFont(font)
        self.name_edit.setStyleSheet("color: #FF8C00;")"""

        # Поля
        self.login_edit = QLineEdit()

        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.notes_edit = QTextEdit()

        # Ссылка
        link_layout = QHBoxLayout()
        self.link_edit = QLineEdit()
        self.link_edit.setPlaceholderText("https://example.com")
        self.btn_open_link = QPushButton("🌌")
        self.btn_open_link.clicked.connect(self.open_link)

        # Кнопки

        btn_layout = QHBoxLayout()

        self.show_pass_btn = QPushButton("👁")
        self.show_pass_btn.setStyleSheet(self.orange_btn_style)
        self.show_pass_btn.clicked.connect(self.change_visibility)

        copy_btn = QPushButton("📋")
        copy_btn.clicked.connect(lambda: self.copy(self.pass_edit.text()))
        copy_btn.setStyleSheet(self.orange_btn_style)

        btn_layout.addWidget(self.show_pass_btn)
        btn_layout.addWidget(copy_btn)
        btn_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))
        # Инициализатор
        self.link_edit.textChanged.connect(self.mark_dirty)
        self.login_edit.textChanged.connect(self.mark_dirty)
        self.pass_edit.textChanged.connect(self.mark_dirty)
        self.notes_edit.textChanged.connect(self.mark_dirty)

        link_layout.addWidget(self.link_edit)
        link_layout.addWidget(self.btn_open_link)

        layout.addWidget(QLabel("Сервис"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Ссылка"))
        layout.addLayout(link_layout)
        layout.addWidget(QLabel("Логин"))
        layout.addWidget(self.login_edit)
        layout.addWidget(QLabel("Пароль"))
        layout.addWidget(self.pass_edit)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Заметки"))
        layout.addWidget(self.notes_edit)
        layout.addStretch()
        return widget

    def open_link(self):
        url = self.link_edit.text().strip()
        if not url:
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        QDesktopServices.openUrl(QUrl(url))

    def _refresh_list(self, filter_text: str = ""):
        self.list_widget.clear()
        for site_name, entry in self.entries.items():
            if filter_text.lower() in site_name.lower():
                self.list_widget.addItem(site_name)

    def add_entry(self):
        self.is_creating = True
        self.curr_entry = None
        self._clear_details()
        self.enable_interface()

        self.login_edit.setFocus()
        if any(
            [
                not btn.text()
                for btn in [
                    self.name_edit,
                    self.login_edit,
                    self.pass_edit,
                ]
            ]
        ):
            self.mark_dirty()

    def _clear_details(self):
        self.blockSignals(True)
        self.name_edit.clear()
        self.login_edit.clear()
        self.pass_edit.clear()
        self.link_edit.clear()
        self.notes_edit.clear()
        self.blockSignals(False)

    def delete_entry(self):
        try:
            master_password = self.master_password[::-1]
            pass_manager = PasswordManager(master_password)
            if not self.curr_entry:
                QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления.")
                return
            confirm = QMessageBox.question(
                self,
                "Удалить?",
                f"Удалить запись '{self.curr_entry}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if confirm == QMessageBox.StandardButton.Yes:
                pass_manager.delete_from_storage(master_password, self.curr_entry())
                pass_manager.get_storage(master_password)

                self.curr_entry = None
                self._refresh_list()
                self._clear_details()
        except PasswordIncorrectError:
            print("Неверный пароль")
            print(self.master_password[::-1])
        except InitializationError:
            print("ошибка инициализации")

    def save_entry(self):
        try:
            master_password = self.master_password[::-1]
            pass_manager = PasswordManager(master_password)

            name = self.name_edit.text().strip()
            login = self.login_edit.text().strip()
            password = self.pass_edit.text().strip()
            link = self.link_edit.text().strip()
            note = self.notes_edit.toPlainText()

            pass_manager.add_to_storage(
                master_password, name, login, password, link, note
            )
            self.entries = pass_manager.get_storage(master_password)
            self.disable_interface()
            self._refresh_list()
        except PasswordIncorrectError:
            print("Неверный пароль")
            print(self.master_password[::-1])
        except InitializationError:
            print("ошибка инициализации")

    def mark_dirty(self):
        self.dirty = True

    def try_switch(self):
        if self.dirty:
            choice = QMessageBox.question(
                self,
                "Несохранённые данные",
                "Вы хотите сохранить изменения?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )

            if choice == QMessageBox.StandardButton.Save:
                self.save_entry()
                self.dirty = False
                return True
            elif choice == QMessageBox.StandardButton.Discard:
                self.dirty = False
                return True
            else:
                return False
        return True

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
