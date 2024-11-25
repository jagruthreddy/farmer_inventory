import mysql.connector
from mysql.connector import Error
import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap, QFont
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QToolButton, QVBoxLayout, QWidget, QMainWindow, QScrollArea,
                             QLineEdit, QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
                             QInputDialog, QComboBox)


from PyQt5.QtWidgets import QApplication

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        
    def connect(self, host, username, password, database=None):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=username,
                password=password,
                database=database
            )
            print("Successfully connected to database server")
            return True
        except Error as e:
            print(f"Error: {e}")
            return False
            
    def close(self):
        if self.connection:
            self.connection.close()

    def get_databases(self):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SHOW DATABASES")
            return [db[0] for db in cursor.fetchall()]
        return []

    def get_tables(self, database):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {database}")
            cursor.execute("SHOW TABLES")
            return [table[0] for table in cursor.fetchall()]
        return []

    def get_table_contents(self, database, table):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {database}")
            cursor.execute(f"SELECT * FROM {table}")
            return cursor.fetchall(), cursor.description
        return [], []

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_connection = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Database Login")
        self.setFixedSize(500, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
                font-family: Consolas;
            }
            QLabel {
                color: white;
                font-size: 16px;
                margin-bottom: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("MySQL Database Login", self)
        title_label.setStyleSheet("font-size: 24px; color: #3EB489; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Host input
        self.host_label = QLabel("Host:", self)
        self.host_input = QLineEdit(self)
        self.host_input.setText("localhost")
        self.host_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #3d3d3d;
                color: white;
                border: 2px solid #3EB489;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4ec49a;
            }
        """)
        
        # Username input
        self.username_label = QLabel("Username:", self)
        self.username_input = QLineEdit(self)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #3d3d3d;
                color: white;
                border: 2px solid #3EB489;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4ec49a;
            }
        """)
        
        # Password input
        self.password_label = QLabel("Password:", self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #3d3d3d;
                color: white;
                border: 2px solid #3EB489;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4ec49a;
            }
        """)
        
        # Login button
        self.login_button = QPushButton("Connect", self)
        self.login_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #3EB489;
                color: white;
                font-size: 20px;
                padding: 10px;
                border-radius: 10px;
                background-color: transparent;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #3EB489;
                color: #1e1e1e;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(self.host_label)
        layout.addWidget(self.host_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        
        self.login_button.clicked.connect(self.try_login)

    def try_login(self):
        host = self.host_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        
        self.db_connection = DatabaseConnection()
        if self.db_connection.connect(host, username, password):
            print("Login successful")
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Failed to connect to database')
            self.db_connection = None

class MainWindow(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.current_database = None
        self.current_table = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Database Manager")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: white;
                gridline-color: #3d3d3d;
                border: none;
            }
            QTableWidget QHeaderView::section {
                background-color: #252525;
                color: white;
                padding: 5px;
                border: 1px solid #3d3d3d;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3EB489;
                color: #1e1e1e;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3d3d3d;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4d4d4d;
            }
        """)
        
        # Create main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create left panel for databases and tables
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(300)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setSpacing(10)
        self.left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Database section
        self.db_label = QLabel("Databases")
        self.db_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.left_layout.addWidget(self.db_label)
        
        self.db_scroll = QScrollArea()
        self.db_scroll.setWidgetResizable(True)
        self.db_widget = QWidget()
        self.db_layout = QVBoxLayout(self.db_widget)
        self.db_scroll.setWidget(self.db_widget)
        self.left_layout.addWidget(self.db_scroll)
        
        # Tables section
        self.table_label = QLabel("Tables")
        self.table_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.left_layout.addWidget(self.table_label)
        
        self.table_scroll = QScrollArea()
        self.table_scroll.setWidgetResizable(True)
        self.table_scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        self.table_widget = QWidget()
        self.table_layout = QVBoxLayout(self.table_widget)
        self.table_scroll.setWidget(self.table_widget)
        self.left_layout.addWidget(self.table_scroll)
        
        # Create right panel for table contents
        self.right_panel = QWidget()
        self.right_panel.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-radius: 10px;
            }
        """)
        self.right_layout = QVBoxLayout(self.right_panel)
        
        # Add panels to main layout
        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addWidget(self.right_panel)
        
        # Load databases
        self.load_databases()

    def load_databases(self):
        # Clear existing items
        while self.db_layout.count():
            item = self.db_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        databases = self.db_connection.get_databases()
        for db in databases:
            db_button = QPushButton(db)
            db_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid #3EB489;
                    color: #d4d4d4;
                    font-size: 14px;
                    padding: 8px;
                    border-radius: 5px;
                    background-color: #2d2d2d;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3EB489;
                    color: #1e1e1e;
                }
            """)
            db_button.clicked.connect(lambda checked, db=db: self.select_database(db))
            self.db_layout.addWidget(db_button)
        
        self.db_layout.addStretch()

    def select_database(self, db):
        self.current_database = db
        print(f"Selected database: {db}")
        
        # Clear existing tables
        while self.table_layout.count():
            item = self.table_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get tables for the selected database
        tables = self.db_connection.get_tables(db)
        for table in tables:
            table_button = QPushButton(table)
            table_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid #3EB489;
                    color: #d4d4d4;
                    font-size: 14px;
                    padding: 8px;
                    border-radius: 5px;
                    background-color: #2d2d2d;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3EB489;
                    color: #1e1e1e;
                }
            """)
            table_button.clicked.connect(lambda checked, table=table: self.display_table(table))
            self.table_layout.addWidget(table_button)
        
        self.table_layout.addStretch()

    def display_table(self, table):
        self.current_table = table
        print(f"Selected table: {table}")
        
        # Clear existing content in right panel
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Table title
        title_label = QLabel(f"Table: {table}")
        title_label.setStyleSheet("""
            color: #d4d4d4;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        self.right_layout.addWidget(title_label)
        
        # Get table contents
        rows, columns = self.db_connection.get_table_contents(self.current_database, table)
        
        # Create table widget
        table_widget = QTableWidget()
        table_widget.setRowCount(len(rows))
        table_widget.setColumnCount(len(columns))
        table_widget.setHorizontalHeaderLabels([col[0] for col in columns])
        
        # Populate table
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make cells read-only
                table_widget.setItem(i, j, item)
        
        # Set table properties
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_widget.verticalHeader().setVisible(False)
        
        # Add table widget to right panel
        self.right_layout.addWidget(table_widget)

if __name__ == "__main__":
        app = QApplication(sys.argv)
        
        # Set application-wide style
        app.setStyle('Fusion')
        
        # Show login dialog
        login_dialog = LoginDialog()
        result = login_dialog.exec_()
        
        if result == QDialog.Accepted and login_dialog.db_connection:
            print("Login accepted, creating main window")
            window = MainWindow(login_dialog.db_connection)
            window.show()
            sys.exit(app.exec_())
        else:
            print("Login cancelled or failed")
            sys.exit