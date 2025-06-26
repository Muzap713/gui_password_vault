import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QStackedLayout, QMessageBox,
    QHeaderView, QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt
from encryption import get_fernet
from db_config import get_connection
from update_password_window import UpdatePasswordWindow


class Dashboard(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Password Vault - Dashboard")
        self.setFixedSize(900, 720)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(40, 30, 40, 15)
        
        # Top row with logout button
        top_row_layout = QHBoxLayout()
        top_row_layout.setContentsMargins(0, 0, 0, 10)
        
        logout_btn = QPushButton("👤 Logout")
        logout_btn.setObjectName("logoutButton")
        logout_btn.clicked.connect(self.handle_logout)
        
        # Store logout button reference for enabling/disabling
        self.logout_btn = logout_btn
        
        top_row_layout.addStretch()
        top_row_layout.addWidget(logout_btn)
        
        # App title
        title_label = QLabel("🔐 Password Vault")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Secure • Private • Reliable")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addLayout(top_row_layout)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_frame.setLayout(header_layout)
        
        # Navigation section - Tab style
        nav_frame = QFrame()
        nav_frame.setObjectName("navFrame")
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        
        self.btn_list = QPushButton("My Passwords")
        self.btn_list.setObjectName("tabButtonActive")
        self.btn_list.clicked.connect(self.on_switch_to_list_page)
        
        self.btn_new = QPushButton("Add New Password")
        self.btn_new.setObjectName("tabButton")
        self.btn_new.clicked.connect(lambda: self.switch_to_new_page())
        
        nav_layout.addWidget(self.btn_list)
        nav_layout.addWidget(self.btn_new)
        nav_frame.setLayout(nav_layout)
        
        # Content section
        self.content_frame = QFrame()
        self.content_frame.setObjectName("contentFrame")
        
        self.pages = QStackedLayout()
        self.pages.addWidget(self.build_list_page())
        self.pages.addWidget(self.build_new_password_page())
        self.content_frame.setLayout(self.pages)
        
        # Add to main layout
        self.main_layout.addWidget(header_frame)
        self.main_layout.addWidget(nav_frame)
        self.main_layout.addWidget(self.content_frame)
        self.setLayout(self.main_layout)
        
        # Install event filter to detect clicks outside password cards
        self.installEventFilter(self)

    def handle_logout(self):
        reply = QMessageBox.question(
            self, "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Import here to avoid circular imports
            from login_register import LoginRegisterWindow
            
            # Create and show login window
            self.login_window = LoginRegisterWindow()
            self.login_window.show()
            
            # Close dashboard
            self.close()

    def switch_to_new_page(self):
        self.btn_list.setObjectName("tabButton")
        self.btn_new.setObjectName("tabButtonActive")
        self.apply_styles()  # Refresh styles
        self.pages.setCurrentIndex(1)

    def on_switch_to_list_page(self):
        # Only check if we're on new password page
        if self.pages.currentIndex() == 1:
            desc_filled = self.description_input.text().strip()
            pw_filled = self.password_input.text().strip()

            if desc_filled or pw_filled:
                reply = QMessageBox.question(
                    self, "Unsaved Data",
                    "You have unsaved password data.\nDo you want to discard it and go to the password list?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return  # stay on current page
                else:
                    self.description_input.clear()
                    self.password_input.clear()
                    self.btn_cancel.setEnabled(False)
                    # Re-enable logout when form is cleared
                    self.logout_btn.setEnabled(True)

        self.btn_list.setObjectName("tabButtonActive")
        self.btn_new.setObjectName("tabButton")
        self.apply_styles()  # Refresh styles
        self.pages.setCurrentIndex(0)

    def build_list_page(self):
        frame = QFrame()
        frame.setObjectName("pageFrame")
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Page title and stats
        header_layout = QHBoxLayout()
        
        page_title = QLabel("My Passwords")
        page_title.setObjectName("pageTitle")
        
        self.stats_label = QLabel("0 passwords stored")
        self.stats_label.setObjectName("statsLabel")
        
        header_layout.addWidget(page_title)
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)
        layout.addLayout(header_layout)

        # Passwords container with scroll
        scroll_area = QScrollArea()
        scroll_area.setObjectName("scrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.passwords_container = QWidget()
        self.passwords_layout = QVBoxLayout()
        self.passwords_layout.setSpacing(15)
        self.passwords_container.setLayout(self.passwords_layout)
        
        # Make container clickable to deselect cards
        self.passwords_container.mousePressEvent = lambda event: self.deselect_all_cards()
        
        scroll_area.setWidget(self.passwords_container)
        
        # Make scroll area clickable to deselect cards
        scroll_area.mousePressEvent = lambda event: self.deselect_all_cards()
        layout.addWidget(scroll_area)

        # Action buttons - Always visible
        self.action_frame = QFrame()
        self.action_frame.setObjectName("actionFrame")
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 15, 0, 0)
        action_layout.setSpacing(15)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.handle_delete)
        
        self.update_btn = QPushButton("Edit Selected")
        self.update_btn.setObjectName("secondaryButton")
        self.update_btn.setEnabled(False)
        self.update_btn.clicked.connect(self.open_update_window)
        
        action_layout.addStretch()
        action_layout.addWidget(self.update_btn)
        action_layout.addWidget(self.delete_btn)
        self.action_frame.setLayout(action_layout)
        
        layout.addWidget(self.action_frame)

        frame.setLayout(layout)
        
        # Make page frame clickable to deselect cards
        frame.mousePressEvent = lambda event: self.deselect_all_cards()
        
        self.load_passwords()
        return frame

    def create_password_card(self, password_data, row_idx):
        card = QFrame()
        card.setObjectName("passwordCard")
        card.setProperty("selected", False)
        
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(20, 15, 20, 15)
        card_layout.setSpacing(10)
        
        # Header with description and ID
        header_layout = QHBoxLayout()
        
        description_label = QLabel(password_data["description"])
        description_label.setObjectName("cardDescription")
        
        id_label = QLabel(f"#{row_idx + 1}")
        id_label.setObjectName("cardId")
        
        header_layout.addWidget(description_label)
        header_layout.addStretch()
        header_layout.addWidget(id_label)
        
        # Password display
        password_layout = QHBoxLayout()
        
        password_label = QLabel("••••••••")
        password_label.setObjectName("cardPassword")
        
        toggle_btn = QPushButton("Show")
        toggle_btn.setObjectName("toggleButton")
        decrypted_pw = password_data["decrypted_password"]
        toggle_btn.clicked.connect(lambda checked, lbl=password_label, btn=toggle_btn, pw=decrypted_pw: self.toggle_card_password(lbl, btn, pw))
        
        password_layout.addWidget(password_label)
        password_layout.addStretch()
        password_layout.addWidget(toggle_btn)
        
        card_layout.addLayout(header_layout)
        card_layout.addLayout(password_layout)
        card.setLayout(card_layout)
        
        # Store data for selection
        card.password_id = password_data["id"]
        card.description = password_data["description"]
        card.row_idx = row_idx
        
        # Make card clickable
        card.mousePressEvent = lambda event: self.select_card(card)
        
        return card

    def eventFilter(self, obj, event):
        """Handle clicks outside password cards to deselect"""
        if event.type() == event.MouseButtonPress:
            # Check if click is on the main dashboard window
            if obj == self:
                self.deselect_all_cards()
        return super().eventFilter(obj, event)

    def deselect_all_cards(self):
        """Deselect all password cards and disable action buttons"""
        # Deselect all cards
        for i in range(self.passwords_layout.count()):
            item = self.passwords_layout.itemAt(i)
            if item and item.widget():
                card = item.widget()
                if hasattr(card, 'password_id'):
                    card.setProperty("selected", False)
        
        # Clear selected data
        if hasattr(self, 'selected_password_id'):
            delattr(self, 'selected_password_id')
        if hasattr(self, 'selected_description'):
            delattr(self, 'selected_description')
        if hasattr(self, 'selected_row'):
            delattr(self, 'selected_row')
        
        # Disable action buttons
        self.delete_btn.setEnabled(False)
        self.update_btn.setEnabled(False)
        
        # Refresh styles
        self.apply_styles()

    def select_card(self, selected_card):
        # Deselect all cards
        for i in range(self.passwords_layout.count()):
            item = self.passwords_layout.itemAt(i)
            if item and item.widget():
                card = item.widget()
                if hasattr(card, 'password_id'):
                    card.setProperty("selected", False)
                    card.setStyleSheet("")  # Reset style
        
        # Select this card
        selected_card.setProperty("selected", True)
        self.apply_styles()  # Refresh styles
        
        # Store selected data
        self.selected_password_id = selected_card.password_id
        self.selected_description = selected_card.description
        self.selected_row = selected_card.row_idx
        
        # Enable action buttons
        self.delete_btn.setEnabled(True)
        self.update_btn.setEnabled(True)

    def toggle_card_password(self, label, button, real_password):
        if label.text() == "••••••••":
            # Show this password
            label.setText(real_password)
            button.setText("Hide")
            
            # Hide all other passwords
            self.hide_all_other_passwords(label)
        else:
            # Hide this password
            label.setText("••••••••")
            button.setText("Show")

    def hide_all_other_passwords(self, current_label):
        """Hide all password labels except the current one"""
        for i in range(self.passwords_layout.count()):
            item = self.passwords_layout.itemAt(i)
            if item and item.widget():
                card = item.widget()
                if hasattr(card, 'password_id'):
                    # Navigate through the card layout to find password components
                    card_layout = card.layout()
                    if card_layout and card_layout.count() >= 2:
                        password_layout_item = card_layout.itemAt(1)
                        if password_layout_item and password_layout_item.layout():
                            password_layout = password_layout_item.layout()
                            if password_layout.count() >= 3:
                                password_label = password_layout.itemAt(0).widget()
                                toggle_button = password_layout.itemAt(2).widget()
                                
                                # Only hide if it's not the current label and it's showing a password
                                if (password_label and toggle_button and 
                                    password_label != current_label and 
                                    password_label.text() != "••••••••"):
                                    password_label.setText("••••••••")
                                    toggle_button.setText("Show")

    def handle_delete(self):
        if not hasattr(self, 'selected_password_id'):
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the password for:\n\n'{self.selected_description}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM passwords WHERE id = %s AND user_id = %s", 
                             (self.selected_password_id, self.user_id))
                conn.commit()
                QMessageBox.information(self, "Deleted", "Password deleted successfully.")
                self.load_passwords()
                # Disable action buttons after delete
                self.delete_btn.setEnabled(False)
                self.update_btn.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete:\n{str(e)}")
            finally:
                cursor.close()
                conn.close()

    def load_passwords(self):
        # Clear existing cards
        for i in reversed(range(self.passwords_layout.count())):
            item = self.passwords_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM passwords WHERE user_id = %s", (self.user_id,))
            rows = cursor.fetchall()
            fernet = get_fernet()

            # Update stats
            count = len(rows)
            self.stats_label.setText(f"{count} password{'s' if count != 1 else ''} stored")

            if count == 0:
                # Show empty state
                empty_label = QLabel("No passwords saved yet.\nClick 'Add New Password' to get started!")
                empty_label.setObjectName("emptyState")
                empty_label.setAlignment(Qt.AlignCenter)
                self.passwords_layout.addWidget(empty_label)
            else:
                # Add password cards
                for row_idx, row in enumerate(rows):
                    decrypted_pw = fernet.decrypt(row["encrypted_password"].encode()).decode()
                    password_data = {
                        "id": row["id"],
                        "description": row["description"],
                        "decrypted_password": decrypted_pw
                    }
                    
                    card = self.create_password_card(password_data, row_idx)
                    self.passwords_layout.addWidget(card)

            # Add stretch to push cards to top
            self.passwords_layout.addStretch()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load passwords:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()

    def build_new_password_page(self):
        frame = QFrame()
        frame.setObjectName("pageFrame")
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(40, 30, 40, 30)
        outer_layout.setSpacing(30)

        # Page title
        page_title = QLabel("Add New Password")
        page_title.setObjectName("pageTitle")
        page_title.setAlignment(Qt.AlignCenter)
        outer_layout.addWidget(page_title)

        # Form container
        form_container = QFrame()
        form_container.setObjectName("formContainer")
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(60, 40, 60, 40)
        form_layout.setSpacing(25)

        # Description field
        desc_label = QLabel("Description")
        desc_label.setObjectName("inputLabel")
        
        desc_container = QFrame()
        desc_container.setObjectName("inputContainer")
        desc_inner_layout = QVBoxLayout()
        desc_inner_layout.setContentsMargins(20, 10, 20, 10)
        
        self.description_input = QLineEdit()
        self.description_input.setObjectName("modernInput")
        self.description_input.setPlaceholderText("e.g., Gmail Account, Facebook, Instagram...")
        self.description_input.textChanged.connect(self.check_cancel_enabled)
        
        desc_inner_layout.addWidget(self.description_input)
        desc_container.setLayout(desc_inner_layout)

        # Password field
        pw_label = QLabel("Password")
        pw_label.setObjectName("inputLabel")
        
        pw_container = QFrame()
        pw_container.setObjectName("inputContainer")
        pw_inner_layout = QHBoxLayout()
        pw_inner_layout.setContentsMargins(20, 10, 20, 10)
        pw_inner_layout.setSpacing(10)
        
        self.password_input = QLineEdit()
        self.password_input.setObjectName("modernInput")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.textChanged.connect(self.check_cancel_enabled)
        
        self.password_toggle = QPushButton("Show")
        self.password_toggle.setObjectName("toggleButton")
        self.password_toggle.clicked.connect(self.toggle_password_visibility)
        
        pw_inner_layout.addWidget(self.password_input)
        pw_inner_layout.addWidget(self.password_toggle)
        pw_container.setLayout(pw_inner_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_cancel = QPushButton("Clear Form")
        self.btn_cancel.setObjectName("textButton")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.clear_inputs)
        
        self.btn_register = QPushButton("Save Password")
        self.btn_register.setObjectName("primaryButton")
        self.btn_register.clicked.connect(self.add_password)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_register)

        # Add to form layout
        form_layout.addWidget(desc_label)
        form_layout.addWidget(desc_container)
        form_layout.addWidget(pw_label)
        form_layout.addWidget(pw_container)
        form_layout.addLayout(btn_layout)
        form_container.setLayout(form_layout)

        outer_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        outer_layout.addStretch()
        frame.setLayout(outer_layout)
        return frame

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.password_toggle.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_toggle.setText("Show")

    def check_cancel_enabled(self):
        has_text = bool(self.description_input.text().strip() or self.password_input.text().strip())
        
        # Enable/disable Clear Form button
        self.btn_cancel.setEnabled(has_text)
        
        # Enable/disable Logout button (opposite of Clear Form)
        self.logout_btn.setEnabled(not has_text)

    def clear_inputs(self):
        self.description_input.clear()
        self.password_input.clear()
        self.btn_cancel.setEnabled(False)
        # Re-enable logout button when form is cleared
        self.logout_btn.setEnabled(True)

    def add_password(self):
        desc = self.description_input.text().strip()
        pw = self.password_input.text().strip()

        if not desc or not pw:
            QMessageBox.warning(self, "Input Error", "Both fields are required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            fernet = get_fernet()
            encrypted = fernet.encrypt(pw.encode()).decode()

            cursor.execute(
                "INSERT INTO passwords (user_id, description, encrypted_password) VALUES (%s, %s, %s)",
                (self.user_id, desc, encrypted)
            )
            conn.commit()

            self.description_input.clear()
            self.password_input.clear()
            self.btn_cancel.setEnabled(False)
            # Re-enable logout button after successful save
            self.logout_btn.setEnabled(True)
            
            # Switch to list page and update nav
            self.btn_list.setObjectName("tabButtonActive")
            self.btn_new.setObjectName("tabButton")
            self.apply_styles()
            self.pages.setCurrentIndex(0)
            self.load_passwords()
            QMessageBox.information(self, "Success", "Password added successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()

    def open_update_window(self):
        if not hasattr(self, 'selected_password_id'):
            return

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT encrypted_password FROM passwords WHERE id = %s AND user_id = %s", 
                         (self.selected_password_id, self.user_id))
            result = cursor.fetchone()
            if result:
                encrypted_password = result['encrypted_password']
                self.update_win = UpdatePasswordWindow(
                    user_id=self.user_id,
                    password_id=self.selected_password_id,
                    description=self.selected_description,
                    encrypted_password=encrypted_password,
                    refresh_callback=self.load_passwords
                )
                self.update_win.exec_()
            else:
                QMessageBox.warning(self, "Not Found", "Password record not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch password:\n{str(e)}")
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
            
            /* Logout Button */
            #logoutButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
                color: #ffffff;
                min-width: 70px;
            }
            
            #logoutButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }
            
            #logoutButton:disabled {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.2);
                color: rgba(255, 255, 255, 0.5);
            }
            
            /* Navigation Section - Bottom Border Accent */
            #navFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
            }
            
            #tabButton {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 4px solid #dee2e6;
                padding: 16px 20px;
                font-size: 15px;
                font-weight: 600;
                color: #6c757d;
                text-align: center;
            }
            
            #tabButton:hover {
                background-color: #e9ecef;
                color: #000000;
                border-bottom: 4px solid #adb5bd;
            }
            
            #tabButtonActive {
                background-color: #ffffff;
                border: none;
                border-bottom: 4px solid #000000;
                padding: 16px 20px;
                font-size: 15px;
                font-weight: 600;
                color: #000000;
                text-align: center;
            }
            
            /* Page Frames */
            #pageFrame {
                background-color: #ffffff;
            }
            
            #pageTitle {
                font-size: 24px;
                font-weight: 600;
                color: #000000;
                margin-bottom: 5px;
            }
            
            #statsLabel {
                font-size: 14px;
                color: #000000;
                font-weight: 500;
            }
            
            /* Scroll Area */
            #scrollArea {
                border: none;
                background-color: transparent;
            }
            
            #scrollArea QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 8px;
                border-radius: 4px;
            }
            
            #scrollArea QScrollBar::handle:vertical {
                background-color: #00cec9;
                border-radius: 4px;
                min-height: 30px;
            }
            
            #scrollArea QScrollBar::handle:vertical:hover {
                background-color: #1dd1cc;
            }
            
            /* Password Cards */
            #passwordCard {
                background-color: #ffffff;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                margin-bottom: 5px;
            }
            
            #passwordCard:hover {
                border-color: #00cec9;
            }
            
            #passwordCard[selected="true"] {
                border-color: #00cec9;
                background-color: #f0fdfc;
            }
            
            #cardDescription {
                font-size: 16px;
                font-weight: 600;
                color: #000000;
            }
            
            #cardId {
                font-size: 12px;
                font-weight: 500;
                color: #000000;
                background-color: #f8f9fa;
                padding: 4px 8px;
                border-radius: 12px;
            }
            
            #cardPassword {
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 16px;
                font-weight: bold;
                color: #000000;
                background-color: #ffffff;
                padding: 12px 16px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                letter-spacing: 1px;
            }
            
            /* Empty State */
            #emptyState {
                font-size: 16px;
                color: #6c757d;
                margin: 60px 0;
                line-height: 1.6;
            }
            
            /* Form Container */
            #formContainer {
                background-color: #e9ecef;
                border-radius: 16px;
                border: 1px solid #dee2e6;
                max-width: 500px;
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
            
            #inputLabel {
                font-size: 12px;
                font-weight: 600;
                color: #2c3e50;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 5px;
                background-color: transparent;
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
                min-width: 120px;
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
            
            #secondaryButton:disabled {
                border-color: #dee2e6;
                color: #6c757d;
                background-color: transparent;
            }
            
            /* Danger Button */
            #dangerButton {
                background-color: #495057;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                color: #ffffff;
                min-width: 100px;
            }
            
            #dangerButton:hover {
                background-color: #343a40;
            }
            
            #dangerButton:disabled {
                background-color: #6c757d;
            }
            
            /* Text Button */
            #textButton {
                background-color: transparent;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                color: #6c757d;
                text-decoration: none;
            }
            
            #textButton:hover {
                color: #00cec9;
                text-decoration: none;
            }
            
            #textButton:disabled {
                color: #adb5bd;
                text-decoration: none;
            }
            
            /* Action Frame */
            #actionFrame {
                border-top: 1px solid #e9ecef;
                padding-top: 15px;
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Dashboard(user_id=1)
    demo.show()
    sys.exit(app.exec_())
