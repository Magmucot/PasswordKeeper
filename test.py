import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QSplitter,
    QListWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QInputDialog,
    QToolBar,
    QSizePolicy,
    QSpacerItem,
    QWidgetAction,
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QAction, QDesktopServices


class PasswordEntry:
    def __init__(self, name: str, username: str, password: str, notes: str = ""):
        self.name = name
        self.username = username
        self.password = password
        self.notes = notes


class PasswordManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Manager")
        self.resize(900, 500)

        # 🔹 Применяем общий стиль
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
                font-family: "Work Sans";
                font-size: 12pt;
                font-weight: 600;
            }
            QListWidget {
                background-color: #1E1E1E;
                border: 1px solid #282828;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #FF8C00;
                color: white;
            }
            QPushButton {
                background-color: #282828;
                border: none;
                padding: 6px 10px;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #888;
            }
            QPushButton:pressed {
                background-color: #AAA;
            }
            QLineEdit, QTextEdit {
                background-color: #1E1E1E;
                border: 1px solid white;
                color: white;
                padding: 3px;
            }
            QLabel {
                color: #BBBBBB;
                font-weight: 500;
                border: none;
            }
            QToolBar {
                background-color: #181818;
                border-bottom: 1px solid #333;
            }
            QToolButton {
                background-color: #282828;
                border-radius: 3px;
                margin: 2px;
                padding: 4px 6px;
            }
            QToolButton:hover {
                background-color: #FF8C00;
            }
        """)

        # 🔸 Отдельный акцентный стиль для оранжевых кнопок
        self.orange_button_style = """
            QPushButton {
                background-color: #FF8C00;
                border-radius: 2px;
                border: none;
                color: white;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background-color: #E07B00;
            }
            QPushButton:pressed {
                background-color: #CC6A00;
            }
        """

        self.entries: list[PasswordEntry] = []
        self.current_entry: PasswordEntry | None = None

        self._setup_ui()
        self._populate_demo_data()

    # ------------------------ UI setup ------------------------
    def _setup_ui(self):
        toolbar = self._create_toolbar()
        self.addToolBar(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.list_widget = QListWidget()
        self.details_widget = self._create_details_panel()

        splitter.addWidget(self.list_widget)
        splitter.addWidget(self.details_widget)
        splitter.setStretchFactor(1, 2)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(splitter)
        self.setCentralWidget(container)

        self.list_widget.itemClicked.connect(self.display_details)

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")

        add_action = QAction("➕", self)
        add_action.triggered.connect(self.add_entry)
        toolbar.addAction(add_action)

        edit_action = QAction("✏", self)
        edit_action.triggered.connect(self.edit_entry)
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
        self.search_input.textChanged.connect(self.filter_entries)
        self.search_input.setFixedWidth(200)
        toolbar.addWidget(self.search_input)

        return toolbar

    def _create_details_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок
        self.name_lbl = QLabel()
        font = self.name_lbl.font()
        font.setPointSize(14)
        font.setBold(True)
        self.name_lbl.setFont(font)
        self.name_lbl.setStyleSheet("color: #FF8C00;")

        # Поля
        self.login_edit = QLineEdit()
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.notes_edit = QLineEdit()

        link_layout = QHBoxLayout()
        self.link_edit = QLineEdit()
        self.link_edit.setPlaceholderText("https://example.com")
        self.btn_open_link = QPushButton("🌌Открыть")
        self.btn_open_link.clicked.connect(self.open_link)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.show_pass_btn = QPushButton("👁")
        self.show_pass_btn.setStyleSheet(self.orange_button_style)
        self.show_pass_btn.clicked.connect(self.toggle_password_visibility)

        copy_btn = QPushButton("📋")
        copy_btn.setStyleSheet(self.orange_button_style)
        copy_btn.clicked.connect(self.copy_password)

        btn_layout.addWidget(self.show_pass_btn)
        btn_layout.addWidget(copy_btn)
        btn_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding))

        link_layout.addWidget(self.link_edit)
        link_layout.addWidget(self.btn_open_link)

        layout.addWidget(QLabel("Сервис"))
        layout.addWidget(self.name_lbl)
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

    # ------------------------ Data logic ------------------------
    def _populate_demo_data(self):
        demo = [
            PasswordEntry("GitHub", "dev_user", "ghp_abc123", "Репозитории"),
            PasswordEntry("Gmail", "mail_user", "Pa$$word1", "Почта"),
            PasswordEntry("AWS", "root", "aws_secret", "Рабочий аккаунт"),
        ]
        self.entries.extend(demo)
        self._refresh_list()

    def open_link(self):
        url = self.link_edit.text().strip()
        if not url:
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        QDesktopServices.openUrl(QUrl(url))

    def _refresh_list(self, filter_text: str = ""):
        self.list_widget.clear()
        for entry in self.entries:
            if filter_text.lower() in entry.name.lower():
                self.list_widget.addItem(entry.name)

    def filter_entries(self, text: str):
        self._refresh_list(text)

    # ------------------------ CRUD actions ------------------------
    def save_entry(self):
        pass

    def add_entry(self):
        name, ok = QInputDialog.getText(self, "Новая запись", "Название сервиса:")
        if not ok or not name.strip():
            return
        username, ok = QInputDialog.getText(self, "Логин", "Имя пользователя:")
        if not ok:
            return
        password, ok = QInputDialog.getText(self, "Пароль", "Введите пароль:")
        if not ok:
            return
        notes, _ = QInputDialog.getText(self, "Заметки", "Дополнительная информация:")

        new_entry = PasswordEntry(
            name.strip(), username.strip(), password.strip(), notes.strip()
        )
        self.entries.append(new_entry)
        self._refresh_list()

    def edit_entry(self):
        if not self.current_entry:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования.")
            return
        self.current_entry.username = self.login_edit.text()
        self.current_entry.password = self.pass_edit.text()
        self.current_entry.notes = self.notes_edit.text()
        QMessageBox.information(self, "Сохранено", "Изменения сохранены успешно.")

    def delete_entry(self):
        if not self.current_entry:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления.")
            return
        confirm = QMessageBox.question(
            self,
            "Удалить?",
            f"Удалить запись '{self.current_entry.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.entries.remove(self.current_entry)
            self.current_entry = None
            self._refresh_list()
            self._clear_details()

    # ------------------------ Display ------------------------
    def display_details(self, item):
        entry = next((e for e in self.entries if e.name == item.text()), None)
        if not entry:
            return
        self.current_entry = entry
        self.name_lbl.setText(entry.name)
        self.login_edit.setText(entry.username)
        self.pass_edit.setText(entry.password)
        self.notes_edit.setText(entry.notes)

    def _clear_details(self):
        self.name_lbl.setText("")
        self.login_edit.clear()
        self.pass_edit.clear()
        self.notes_edit.clear()

    # ------------------------ Utils ------------------------
    def toggle_password_visibility(self):
        if self.pass_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.pass_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pass_btn.setText("🙈 Скрыть")
        else:
            self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pass_btn.setText("👁 Показать")

    def copy_password(self):
        if self.current_entry:
            QApplication.clipboard().setText(self.current_entry.password)
            QMessageBox.information(
                self, "Скопировано", "Пароль скопирован в буфер обмена."
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordManagerGUI()
    window.show()
    sys.exit(app.exec())
