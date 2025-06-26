import bcrypt
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QToolButton, QFrame, QTextEdit
)
from PyQt5.QtCore import Qt
from db_config import get_connection
from password_validator import PasswordValidator

import re


class ForgotPasswordWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forgot Password - Password Vault")
        self.setFixedSize(450, 500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setModal(True)
        self.center_window()
        self.setup_ui()
        self.apply_styles()
        self.user_email = None

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
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(40, 40, 40, 35)
        
        # App title
        title_label = QLabel("🔐 Password Vault")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Recover Your Account")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_frame.setLayout(header_layout)
        
        # Content section
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(40, 15, 40, 25)
        self.content_layout.setSpacing(12)
                
        # Forgot Password form title
        form_title = QLabel("Reset Password")
        form_title.setObjectName("formTitle")
        form_title.setAlignment(Qt.AlignCenter)
        
        # Email field
        self.email_label = QLabel("Email Address")
        self.email_label.setObjectName("inputLabel")
        
        email_container = QFrame()
        email_container.setObjectName("inputContainer")
        email_layout = QVBoxLayout()
        email_layout.setContentsMargins(20, 10, 20, 10)
        email_layout.setSpacing(0)
        
        # Create horizontal layout for email input and checkmark
        email_input_layout = QHBoxLayout()
        email_input_layout.setSpacing(10)
        
        self.email_input = QLineEdit()
        self.email_input.setObjectName("modernInput")
        self.email_input.setPlaceholderText("Enter your registered email")
        
        # Add checkmark label (initially hidden)
        self.email_checkmark = QLabel("✅")
        self.email_checkmark.setObjectName("checkmarkLabel")
        self.email_checkmark.hide()  # Hidden initially
        
        email_input_layout.addWidget(self.email_input)
        email_input_layout.addWidget(self.email_checkmark)
        
        email_layout.addLayout(email_input_layout)
        email_container.setLayout(email_layout)
        
        # Submit Button
        self.submit_btn = QPushButton("Verify Email")
        self.submit_btn.setObjectName("primaryButton")
        self.submit_btn.clicked.connect(self.verify_email)
        
        # Back to Login Button
        self.back_btn = QPushButton("Back to Sign In")
        self.back_btn.setObjectName("textButton")
        self.back_btn.clicked.connect(self.close)
        
        # Add initial elements to content layout
        self.content_layout.addWidget(form_title)
        self.content_layout.addWidget(self.email_label)
        self.content_layout.addWidget(email_container)
        self.content_layout.addWidget(self.submit_btn)
        self.content_layout.addWidget(self.back_btn)
        self.content_frame.setLayout(self.content_layout)
        
        # Add to main layout
        self.main_layout.addWidget(header_frame)
        self.main_layout.addWidget(self.content_frame)
        self.setLayout(self.main_layout)

    def verify_email(self):
        email = self.email_input.text().strip()

        if not email:
            QMessageBox.warning(self, "Input Required", "Please enter your email.")
            return

        # Email validation
        if not self.is_valid_email(email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address (example@domain.com).")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        finally:
            cursor.close()
            conn.close()

        if not user:
            QMessageBox.warning(self, "Not Found", "Email not found in the system.")
        else:
            self.user_email = email
            # Show checkmark at top right of email field
            self.email_checkmark.show()
            self.email_input.setDisabled(True)
            self.submit_btn.setDisabled(True)
            
            # Immediately show reset fields without popup
            self.show_reset_fields()

    def show_reset_fields(self):
        # New Password field
        password_label = QLabel("New Password")
        password_label.setObjectName("inputLabel")
        
        password_container = QFrame()
        password_container.setObjectName("inputContainer")
        password_layout = QVBoxLayout()
        password_layout.setContentsMargins(20, 10, 20, 10)
        password_layout.setSpacing(0)
        
        pw_input_layout = QHBoxLayout()
        pw_input_layout.setSpacing(10)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setObjectName("modernInput")
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.textChanged.connect(self.on_password_changed)
        
        self.pw_toggle = QToolButton()
        self.pw_toggle.setObjectName("toggleButton")
        self.pw_toggle.setText("show")
        self.pw_toggle.clicked.connect(self.toggle_password)
        
        pw_input_layout.addWidget(self.new_password_input)
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
        self.validation_text.setMaximumHeight(100)
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
        self.confirm_input.setPlaceholderText("Confirm new password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        
        self.confirm_toggle = QToolButton()
        self.confirm_toggle.setObjectName("toggleButton")
        self.confirm_toggle.setText("show")
        self.confirm_toggle.clicked.connect(self.toggle_confirm)
        
        confirm_input_layout.addWidget(self.confirm_input)
        confirm_input_layout.addWidget(self.confirm_toggle)
        
        confirm_layout.addLayout(confirm_input_layout)
        confirm_container.setLayout(confirm_layout)
        
        # Buttons
        self.confirm_btn = QPushButton("Reset Password")
        self.confirm_btn.setObjectName("primaryButton")
        self.confirm_btn.setEnabled(False)  # Initially disabled
        self.confirm_btn.clicked.connect(self.reset_password)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.clicked.connect(self.close)
        
        # Add new fields to layout
        self.content_layout.addWidget(password_label)
        self.content_layout.addWidget(password_container)
        self.content_layout.addWidget(self.strength_label)
        self.content_layout.addWidget(self.validation_text)
        self.content_layout.addWidget(confirm_label)
        self.content_layout.addWidget(confirm_container)
        self.content_layout.addWidget(self.confirm_btn)
        self.content_layout.addWidget(self.cancel_btn)
        
        # Increase window height to accommodate new fields
        self.setFixedSize(450, 950)
        # Re-center the window after resizing
        self.center_window()

    def on_password_changed(self):
        password = self.new_password_input.text()
        
        if not password:
            self.strength_label.setText("")
            self.validation_text.setPlainText(PasswordValidator.get_password_requirements())
            self.confirm_btn.setEnabled(False)
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
            self.confirm_btn.setEnabled(True)
        else:
            feedback = PasswordValidator.suggest_improvements(missing_requirements)
            self.validation_text.setPlainText(feedback)
            self.validation_text.setStyleSheet("color: #e17055; background-color: #fdf2f2;")
            self.confirm_btn.setEnabled(False)

    def toggle_password(self):
        if self.new_password_input.echoMode() == QLineEdit.Password:
            self.new_password_input.setEchoMode(QLineEdit.Normal)
            self.pw_toggle.setText("hide")
        else:
            self.new_password_input.setEchoMode(QLineEdit.Password)
            self.pw_toggle.setText("show")

    def toggle_confirm(self):
        if self.confirm_input.echoMode() == QLineEdit.Password:
            self.confirm_input.setEchoMode(QLineEdit.Normal)
            self.confirm_toggle.setText("hide")
        else:
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_toggle.setText("show")

    def reset_password(self):
        pw = self.new_password_input.text().strip()
        confirm = self.confirm_input.text().strip()

        if not pw or not confirm:
            QMessageBox.warning(self, "Missing Info", "Fill in both password fields.")
            return

        if pw != confirm:
            QMessageBox.warning(self, "Mismatch", "Passwords do not match.")
            return

        # Final validation check
        is_valid, missing_requirements, strength = PasswordValidator.validate_password(pw)
        if not is_valid:
            QMessageBox.warning(
                self, 
                "Password Requirements Not Met", 
                f"Your new master password does not meet security requirements:\n\n{PasswordValidator.suggest_improvements(missing_requirements)}"
            )
            return

        hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET master_password_hash = %s WHERE email = %s",
                (hashed, self.user_email)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "Password updated successfully ✅")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            cursor.close()
            conn.close()

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
            
            #inputContainer:disabled {
                background-color: #e9ecef;
                border-color: #dee2e6;
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
            
            #modernInput:disabled {
                color: #6c757d;
            }
            
            #modernInput::placeholder {
                color: #adb5bd;
            }
            
            /* Checkmark Label */
            #checkmarkLabel {
                font-size: 16px;
                color: #00b894;
                font-weight: bold;
                background-color: transparent;
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
                    stop: 0 #00cec9, stop: 1 #00b894);
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
