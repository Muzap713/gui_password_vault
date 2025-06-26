import bcrypt
from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QToolButton, QFrame
)
from PyQt5.QtCore import Qt
from encryption import get_fernet
from db_config import get_connection


class UpdatePasswordWindow(QDialog):
    def __init__(self, user_id, password_id, description, encrypted_password, refresh_callback):
        super().__init__()
        self.setModal(True)

        self.user_id = user_id
        self.password_id = password_id
        self.description = description
        self.encrypted_password = encrypted_password
        self.refresh_callback = refresh_callback

        self.setWindowTitle("Update Password")
        self.setFixedSize(500, 790)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(30, 25, 30, 25)
        
        title_label = QLabel("🔐 Update Password")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Modify your stored password securely")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_frame.setLayout(header_layout)
        
        # Content section
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(25)

        # Description field (read-only)
        desc_label = QLabel("DESCRIPTION")
        desc_label.setObjectName("inputLabel")
        
        desc_container = QFrame()
        desc_container.setObjectName("readOnlyContainer")
        desc_inner_layout = QVBoxLayout()
        desc_inner_layout.setContentsMargins(20, 12, 20, 12)
        
        self.desc_input = QLineEdit()
        self.desc_input.setText(self.description)
        self.desc_input.setObjectName("readOnlyInput")
        self.desc_input.setReadOnly(True)
        
        desc_inner_layout.addWidget(self.desc_input)
        desc_container.setLayout(desc_inner_layout)

        # Current Password field (read-only with toggle)
        current_label = QLabel("CURRENT PASSWORD")
        current_label.setObjectName("inputLabel")
        
        current_container = QFrame()
        current_container.setObjectName("readOnlyContainer")
        current_inner_layout = QHBoxLayout()
        current_inner_layout.setContentsMargins(20, 12, 20, 12)
        current_inner_layout.setSpacing(10)
        
        fernet = get_fernet()
        decrypted = fernet.decrypt(self.encrypted_password.encode()).decode()
        
        self.old_pw_input = QLineEdit()
        self.old_pw_input.setText(decrypted)
        self.old_pw_input.setObjectName("readOnlyInput")
        self.old_pw_input.setEchoMode(QLineEdit.Password)
        self.old_pw_input.setReadOnly(True)
        
        self.old_pw_toggle = QPushButton("Show")
        self.old_pw_toggle.setObjectName("toggleButton")
        self.old_pw_toggle.clicked.connect(self.toggle_old_pw)
        
        current_inner_layout.addWidget(self.old_pw_input)
        current_inner_layout.addWidget(self.old_pw_toggle)
        current_container.setLayout(current_inner_layout)

        # New Password field
        new_label = QLabel("NEW PASSWORD")
        new_label.setObjectName("inputLabel")
        
        new_container = QFrame()
        new_container.setObjectName("inputContainer")
        new_inner_layout = QHBoxLayout()
        new_inner_layout.setContentsMargins(20, 12, 20, 12)
        new_inner_layout.setSpacing(10)
        
        self.new_pw_input = QLineEdit()
        self.new_pw_input.setObjectName("modernInput")
        self.new_pw_input.setEchoMode(QLineEdit.Password)
        self.new_pw_input.setPlaceholderText("Enter new password")
        
        self.new_pw_toggle = QPushButton("Show")
        self.new_pw_toggle.setObjectName("toggleButton")
        self.new_pw_toggle.clicked.connect(self.toggle_new_pw)
        
        new_inner_layout.addWidget(self.new_pw_input)
        new_inner_layout.addWidget(self.new_pw_toggle)
        new_container.setLayout(new_inner_layout)

        # Confirm Password field
        confirm_label = QLabel("CONFIRM NEW PASSWORD")
        confirm_label.setObjectName("inputLabel")
        
        confirm_container = QFrame()
        confirm_container.setObjectName("inputContainer")
        confirm_inner_layout = QHBoxLayout()
        confirm_inner_layout.setContentsMargins(20, 12, 20, 12)
        confirm_inner_layout.setSpacing(10)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setObjectName("modernInput")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setPlaceholderText("Confirm new password")
        
        self.confirm_toggle = QPushButton("Show")
        self.confirm_toggle.setObjectName("toggleButton")
        self.confirm_toggle.clicked.connect(self.toggle_confirm_pw)
        
        confirm_inner_layout.addWidget(self.confirm_input)
        confirm_inner_layout.addWidget(self.confirm_toggle)
        confirm_container.setLayout(confirm_inner_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)
        
        update_btn = QPushButton("Update Password")
        update_btn.setObjectName("primaryButton")
        update_btn.clicked.connect(self.update_password)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(update_btn)

        # Add to content layout
        content_layout.addWidget(desc_label)
        content_layout.addWidget(desc_container)
        content_layout.addWidget(current_label)
        content_layout.addWidget(current_container)
        content_layout.addWidget(new_label)
        content_layout.addWidget(new_container)
        content_layout.addWidget(confirm_label)
        content_layout.addWidget(confirm_container)
        content_layout.addLayout(btn_layout)
        content_frame.setLayout(content_layout)

        # Add to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)

    def toggle_old_pw(self):
        if self.old_pw_input.echoMode() == QLineEdit.Password:
            self.old_pw_input.setEchoMode(QLineEdit.Normal)
            self.old_pw_toggle.setText("Hide")
        else:
            self.old_pw_input.setEchoMode(QLineEdit.Password)
            self.old_pw_toggle.setText("Show")

    def toggle_new_pw(self):
        if self.new_pw_input.echoMode() == QLineEdit.Password:
            self.new_pw_input.setEchoMode(QLineEdit.Normal)
            self.new_pw_toggle.setText("Hide")
        else:
            self.new_pw_input.setEchoMode(QLineEdit.Password)
            self.new_pw_toggle.setText("Show")

    def toggle_confirm_pw(self):
        if self.confirm_input.echoMode() == QLineEdit.Password:
            self.confirm_input.setEchoMode(QLineEdit.Normal)
            self.confirm_toggle.setText("Hide")
        else:
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_toggle.setText("Show")

    def update_password(self):
        new_pw = self.new_pw_input.text().strip()
        confirm_pw = self.confirm_input.text().strip()

        if not new_pw or not confirm_pw:
            QMessageBox.warning(self, "Missing Info", "Please fill in both password fields.")
            return

        if new_pw != confirm_pw:
            QMessageBox.warning(self, "Mismatch", "New passwords do not match.")
            return

        if len(new_pw) < 8 or not any(c.isdigit() for c in new_pw) or not any(c.isupper() for c in new_pw):
            QMessageBox.warning(self, "Weak Password", "Use at least 8 characters, 1 number, 1 uppercase.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            fernet = get_fernet()
            encrypted = fernet.encrypt(new_pw.encode()).decode()
            cursor.execute(
                "UPDATE passwords SET encrypted_password = %s WHERE id = %s AND user_id = %s",
                (encrypted, self.password_id, self.user_id)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "Password updated successfully.")
            self.refresh_callback()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update password:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()

    def apply_styles(self):
        self.setStyleSheet("""
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
                font-size: 24px;
                font-weight: bold;
                color: #000000;
                margin-bottom: 2px;
            }
            
            #subtitleLabel {
                font-size: 14px;
                color: #00cec9; 
                font-weight: 500;
            }
            
            /* Content Frame */
            #contentFrame {
                background-color: #f8f9fa;
            }
            
            /* Input Labels */
            #inputLabel {
                font-size: 12px;
                font-weight: 600;
                color: #2c3e50;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 5px;
                background-color: transparent;
            }
            
            /* Input Containers */
            #inputContainer {
                background-color: #ffffff;
                border-radius: 12px;
                border: 2px solid #dee2e6;
            }
            
            #inputContainer:hover {
                border-color: #00cec9;
            }
            
            /* Read-only Containers */
            #readOnlyContainer {
                background-color: #e9ecef;
                border-radius: 12px;
                border: 2px solid #dee2e6;
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
            
            #modernInput::placeholder {
                color: #adb5bd;
            }
            
            /* Read-only Input Fields */
            #readOnlyInput {
                background-color: transparent;
                border: none;
                font-size: 16px;
                color: #495057;
                padding: 8px 5px;
                outline: none;
                min-height: 21px;
                font-weight: 500;
            }
            
            /* Toggle Button */
            #toggleButton {
                background-color: #e9ecef;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
                color: #000000;
                min-width: 50px;
            }
            
            #toggleButton:hover {
                background-color: #00cec9;
                color: #ffffff;
            }
            
            /* Primary Button */
            #primaryButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00cec9, stop: 1 #00b894);
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                min-width: 140px;
            }
            
            #primaryButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1dd1cc, stop: 1 #00d2a4);
            }
            
            /* Secondary Button */
            #secondaryButton {
                background-color: transparent;
                border: 2px solid #00cec9;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                color: #00cec9;
                min-width: 100px;
            }
            
            #secondaryButton:hover {
                background-color: #00cec9;
                color: #ffffff;
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
