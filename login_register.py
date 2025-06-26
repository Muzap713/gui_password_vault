import sys
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QToolButton, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from db_config import get_connection
from register_window import RegisterWindow
from forgot_password_window import ForgotPasswordWindow


class LoginRegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Vault")
        self.setFixedSize(450, 630)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.center_window()
        self.setup_ui()
        self.apply_styles()

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(40, 30, 40, 15)  # reduce last value from 20 to 15
        
        # App title
        title_label = QLabel("🔐 Password Vault")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Secure • Private • Reliable")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_frame.setLayout(header_layout)
        
        # Content section
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout()
        # Reduce content padding and spacing
        content_layout.setContentsMargins(40, 20, 40, 30)  # was (40, 30, 40, 40)
        content_layout.setSpacing(15)  # was 20
                
        # Login form title
        form_title = QLabel("Sign In")
        form_title.setObjectName("formTitle")
        form_title.setAlignment(Qt.AlignCenter)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setObjectName("inputLabel")
        
        username_container = QFrame()
        username_container.setObjectName("inputContainer")
        username_layout = QVBoxLayout()
        username_layout.setContentsMargins(20, 10, 20, 10)
        username_layout.setSpacing(0)
        
        self.username_input = QLineEdit()
        self.username_input.setObjectName("modernInput")
        self.username_input.setPlaceholderText("Enter your username")
        
        username_layout.addWidget(self.username_input)
        username_container.setLayout(username_layout)
        
        # Password field
        password_label = QLabel("Master Password")
        password_label.setObjectName("inputLabel")
        
        password_container = QFrame()
        password_container.setObjectName("inputContainer")
        password_layout = QVBoxLayout()
        password_layout.setContentsMargins(20, 10, 20, 10)
        password_layout.setSpacing(0)
        
        pw_input_layout = QHBoxLayout()
        pw_input_layout.setSpacing(10)
        
        self.password_input = QLineEdit()
        self.password_input.setObjectName("modernInput")
        self.password_input.setPlaceholderText("Enter your master password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.toggle_pw_btn = QToolButton()
        self.toggle_pw_btn.setObjectName("toggleButton")
        self.toggle_pw_btn.setText("show")
        self.toggle_pw_btn.clicked.connect(self.toggle_password_visibility)
        
        pw_input_layout.addWidget(self.password_input)
        pw_input_layout.addWidget(self.toggle_pw_btn)
        
        password_layout.addLayout(pw_input_layout)
        password_container.setLayout(password_layout)
        
        # Buttons
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("primaryButton")
        self.login_btn.clicked.connect(self.login)
        
        self.register_btn = QPushButton("Create Account")
        self.register_btn.setObjectName("secondaryButton")
        self.register_btn.clicked.connect(self.open_register_window)
        
        self.forgot_btn = QPushButton("Forgot Password?")
        self.forgot_btn.setObjectName("textButton")
        self.forgot_btn.clicked.connect(self.open_forgot_window)
        
        # Add everything to content layout
        content_layout.addWidget(form_title)
        content_layout.addWidget(username_label)
        content_layout.addWidget(username_container)
        content_layout.addWidget(password_label)
        content_layout.addWidget(password_container)
        content_layout.addWidget(self.login_btn)
        content_layout.addWidget(self.register_btn)
        content_layout.addWidget(self.forgot_btn)
        content_frame.setLayout(content_layout)
        
        # Add to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            /* Main Window */
            QWidget {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            /* Header Section */
            /*#headerFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f8f9fa, stop: 1 #e9ecef);
                border: none;
                border-bottom: 3px solid #00cec9;
            }*/
                           
            #headerFrame {
                background-color: #00cec9;
                border: none;
            }
            
            #titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #000000;  /* Change from #2c3e50 to #000000 */
                margin-bottom: 2px;  /* was 5px */
            }
            
            #subtitleLabel {
                font-size: 14px;
                color: #00cec9;  /* Change from #00b894 to #00cec9 (same as button) */
                font-weight: 500;
            }
            
            /* Content Section */
            #contentFrame {
                background-color: #ffffff;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
            }
            
            #formTitle {
                font-size: 22px;
                font-weight: 600;
                color: #000000;  /* Change from #2c3e50 to #000000 */
                margin-bottom: 10px;
            }
            
            /* Input Containers */
            #inputContainer {
                background-color: #f8f9fa;
                border-radius: 12px;
                border: 2px solid #e9ecef;
            }
            
            #inputContainer:hover {
                border-color: #00cec9;
            }
            
            #inputLabel {
                font-size: 12px;
                font-weight: 600;
                color: #000000;  /* Change from #6c757d to #000000 */
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            /* Modern Input Fields */
            #modernInput {
                background-color: transparent;
                border: none;
                font-size: 16px;
                color: #2c3e50;
                padding: 8px 5px;
                outline: none;
                min-height: 21px;
            }
            
            #modernInput:focus {
                color: #2c3e50;
            }
            
            #modernInput::placeholder {
                color: #adb5bd;
            }
            
            /* Toggle Button */
            #toggleButton {
                background-color: #e9ecef;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #000000;
                min-width: 40px;
            }
            
            #toggleButton:hover {
                background-color: #00cec9;
                /*color: #ffffff;*/
            }
            
            /* Primary Button */
            #primaryButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00cec9, stop: 1 #00b894);
                border: none;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                margin-top: 10px;
                min-height: 21px;
            }
            
            #primaryButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1dd1cc, stop: 1 #00d2a4);
            }
            
            #primaryButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00a085, stop: 1 #009688);
            }
            
            /* Secondary Button */
            #secondaryButton {
                background-color: transparent;
                border: 2px solid #00cec9;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: 500;
                color: #00cec9;
                min-height: 21px;
            }
            
            #secondaryButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00cec9, stop: 1 #00b894);  /* Same as Sign In button */
                color: #ffffff;
            }
            
            /* Text Button */
            #textButton {
                background-color: transparent;
                border: none;
                padding: 10px;
                font-size: 14px;
                color: #000000;
                text-decoration: underline;
            }
            
            #textButton:hover {
                color: #00cec9;
            }
            
            /* Message Boxes */
            QMessageBox {
                background-color: #ffffff;
                color: #2c3e50;
            }
            
            QMessageBox QPushButton {
                background-color: #00cec9;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
                font-weight: 500;
                min-width: 80px;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #1dd1cc;
            }
        """)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pw_btn.setText("hide")  # Eye open
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_pw_btn.setText("show")  # Eye covered
                
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both fields.")
            return

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode(), user["master_password_hash"].encode()):
            # QMessageBox.information(self, "Success", "Login successful ✅")
            self.open_main_window(user["id"])
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")

    def open_register_window(self):
        # Create modal register window
        self.reg_win = RegisterWindow()
        self.reg_win.exec_()  # Modal - blocks login window

    def open_forgot_window(self):
        # Create modal forgot password window
        self.forgot_win = ForgotPasswordWindow()
        self.forgot_win.exec_()  # Modal - blocks login window

    def open_main_window(self, user_id):
        from dashboard import Dashboard
        self.main_win = Dashboard(user_id)
        self.main_win.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginRegisterWindow()
    window.show()
    sys.exit(app.exec_())
