import bcrypt
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QToolButton, QFrame, QTextEdit
)
from PyQt5.QtCore import Qt
from db_config import get_connection
from password_validator import PasswordValidator

import re


class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register - Password Vault")
        self.setFixedSize(450, 900)  # Increased height for validation feedback
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setModal(True)
        self.center_window()
        self.setup_ui()
        self.apply_styles()
        
    @staticmethod
    def is_valid_email(email):
        pattern = r"^[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+$"
        return re.match(pattern, email) is not None

    def center_window(self):
        screen = self.screen().geometry()
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
        header_layout.setContentsMargins(40, 30, 40, 15)
        
        # App title
        title_label = QLabel("🔐 Password Vault")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Create Your Secure Account")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_frame.setLayout(header_layout)
        
        # Content section
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 20, 40, 30)
        content_layout.setSpacing(15)
                
        # Register form title
        form_title = QLabel("Create Account")
        form_title.setObjectName("formTitle")
        form_title.setAlignment(Qt.AlignCenter)
        
        # Email field
        email_label = QLabel("Email")
        email_label.setObjectName("inputLabel")
        
        email_container = QFrame()
        email_container.setObjectName("inputContainer")
        email_layout = QVBoxLayout()
        email_layout.setContentsMargins(20, 10, 20, 10)
        email_layout.setSpacing(0)
        
        self.email_input = QLineEdit()
        self.email_input.setObjectName("modernInput")
        self.email_input.setPlaceholderText("Enter your email address")
        
        email_layout.addWidget(self.email_input)
        email_container.setLayout(email_layout)
        
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
        self.username_input.setPlaceholderText("Choose a username")
        
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
        self.password_input.setPlaceholderText("Create a strong password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.on_password_changed)
        
        self.pw_toggle = QToolButton()
        self.pw_toggle.setObjectName("toggleButton")
        self.pw_toggle.setText("show")
        self.pw_toggle.clicked.connect(self.toggle_password)
        
        pw_input_layout.addWidget(self.password_input)
        pw_input_layout.addWidget(self.pw_toggle)
        
        password_layout.addLayout(pw_input_layout)
        password_container.setLayout(password_layout)
        
        # Password strength indicator
        self.strength_label = QLabel("")
        self.strength_label.setObjectName("strengthLabel")
        self.strength_label.setAlignment(Qt.AlignCenter)
        
        # Password validation feedback
        self.validation_text = QTextEdit()
        self.validation_text.setObjectName("validationText")
        self.validation_text.setMaximumHeight(120)
        self.validation_text.setReadOnly(True)
        self.validation_text.setPlainText(PasswordValidator.get_password_requirements())
        
        # Confirm Password field
        confirm_label = QLabel("Confirm Password")
        confirm_label.setObjectName("inputLabel")
        
        confirm_container = QFrame()
        confirm_container.setObjectName("inputContainer")
        confirm_layout = QVBoxLayout()
        confirm_layout.setContentsMargins(20, 10, 20, 10)
        confirm_layout.setSpacing(0)
        
        confirm_input_layout = QHBoxLayout()
        confirm_input_layout.setSpacing(10)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setObjectName("modernInput")
        self.confirm_input.setPlaceholderText("Confirm your password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        
        self.confirm_toggle = QToolButton()
        self.confirm_toggle.setObjectName("toggleButton")
        self.confirm_toggle.setText("show")
        self.confirm_toggle.clicked.connect(self.toggle_confirm)
        
        confirm_input_layout.addWidget(self.confirm_input)
        confirm_input_layout.addWidget(self.confirm_toggle)
        
        confirm_layout.addLayout(confirm_input_layout)
        confirm_container.setLayout(confirm_layout)
        
        # Register Button
        self.register_btn = QPushButton("Create Account")
        self.register_btn.setObjectName("primaryButton")
        self.register_btn.setEnabled(False)  # Initially disabled
        self.register_btn.clicked.connect(self.register)
        
        # Back to Login Button
        self.back_btn = QPushButton("Already have an account? Sign In")
        self.back_btn.setObjectName("textButton")
        self.back_btn.clicked.connect(self.close)
        
        # Add everything to content layout
        content_layout.addWidget(form_title)
        content_layout.addWidget(email_label)
        content_layout.addWidget(email_container)
        content_layout.addWidget(username_label)
        content_layout.addWidget(username_container)
        content_layout.addWidget(password_label)
        content_layout.addWidget(password_container)
        content_layout.addWidget(self.strength_label)
        content_layout.addWidget(self.validation_text)
        content_layout.addWidget(confirm_label)
        content_layout.addWidget(confirm_container)
        content_layout.addWidget(self.register_btn)
        content_layout.addWidget(self.back_btn)
        content_frame.setLayout(content_layout)
        
        # Add to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)

    def on_password_changed(self):
        password = self.password_input.text()
        
        if not password:
            self.strength_label.setText("")
            self.validation_text.setPlainText(PasswordValidator.get_password_requirements())
            self.register_btn.setEnabled(False)
            return
        
        # Validate password
        is_valid, missing_requirements, strength = PasswordValidator.validate_password(password)
        
        # Update strength indicator
        strength_colors = {
            "Very Strong": "#00b894",
            "Strong": "#00cec9", 
            "Medium": "#fdcb6e",
            "Weak": "#e17055"
        }
        
        color = strength_colors.get(strength, "#6c757d")
        self.strength_label.setText(f"Password Strength: {strength}")
        self.strength_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
        
        # Update validation feedback
        if is_valid:
            self.validation_text.setPlainText("✅ Password meets all security requirements!")
            self.validation_text.setStyleSheet("color: #00b894; background-color: #d1f2eb;")
            self.register_btn.setEnabled(True)
        else:
            feedback = PasswordValidator.suggest_improvements(missing_requirements)
            self.validation_text.setPlainText(feedback)
            self.validation_text.setStyleSheet("color: #e17055; background-color: #fdf2f2;")
            self.register_btn.setEnabled(False)

    def apply_styles(self):
        self.setStyleSheet("""
            /* Main Window */
            QWidget {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            /* Header Section */
            #headerFrame {
                background-color: #00cec9;
                border: none;
            }
            
            #titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #000000;
                margin-bottom: 2px;
            }
            
            #subtitleLabel {
                font-size: 14px;
                color: #00cec9;
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
                color: #000000;
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
                color: #000000;
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
            
            /* Strength Label */
            #strengthLabel {
                margin: 5px 0;
                padding: 5px;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            
            /* Validation Text */
            #validationText {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.4;
                background-color: #f8f9fa;
                color: #495057;
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
                color: #00cec9;
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
            
            #primaryButton:disabled {
                background-color: #dee2e6;
                color: #6c757d;
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

    def toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.pw_toggle.setText("hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.pw_toggle.setText("show")

    def toggle_confirm(self):
        if self.confirm_input.echoMode() == QLineEdit.Password:
            self.confirm_input.setEchoMode(QLineEdit.Normal)
            self.confirm_toggle.setText("hide")
        else:
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_toggle.setText("show")

    def register(self):
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()

        if not email or not username or not password or not confirm:
            QMessageBox.warning(self, "Missing Info", "All fields are required.")
            return

        # Email validation
        if not self.is_valid_email(email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address (example@domain.com).")
            return

        if password != confirm:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return

        # Final validation check
        is_valid, missing_requirements, strength = PasswordValidator.validate_password(password)
        if not is_valid:
            QMessageBox.warning(
                self, 
                "Password Requirements Not Met", 
                f"Your master password does not meet security requirements:\n\n{PasswordValidator.suggest_improvements(missing_requirements)}"
            )
            return

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, username, master_password_hash) VALUES (%s, %s, %s)",
                (email, username, hashed_pw)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "Registration complete ✅")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not register:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
