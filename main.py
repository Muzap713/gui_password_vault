#!/usr/bin/env python3
"""
Password Vault Application
Main entry point for the GUI Password Manager
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

def main():
    """Main application entry point"""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Password Vault")
    app.setApplicationVersion("1.0")
    
    # Import and create the login window
    from login_register import LoginRegisterWindow
    
    # Create and show the main login window
    login_window = LoginRegisterWindow()
    login_window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
