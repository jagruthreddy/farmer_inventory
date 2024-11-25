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

from farmer import FarmerMainWindow

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
    
    def create_table(self, database, table_name, columns):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"USE {database}")
                
                # Create column definitions
                column_defs = ", ".join([f"{name} {type}" for name, type in columns])
                query = f"CREATE TABLE {table_name} ({column_defs})"
                
                cursor.execute(query)
                self.connection.commit()
                return True
            except Error as e:
                print(f"Error creating table: {e}")
                return False
        return False

    def delete_table(self, database, table_name):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"USE {database}")
                cursor.execute(f"DROP TABLE {table_name}")
                self.connection.commit()
                return True
            except Error as e:
                print(f"Error deleting table: {e}")
                return False
        return False

    def add_column(self, database, table, column_name, column_type):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"USE {database}")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_type}")
                self.connection.commit()
                return True
            except Error as e:
                print(f"Error adding column: {e}")
                return False
        return False

    def delete_column(self, database, table, column_name):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"USE {database}")
                cursor.execute(f"ALTER TABLE {table} DROP COLUMN {column_name}")
                self.connection.commit()
                return True
            except Error as e:
                print(f"Error deleting column: {e}")
                return False
        return False

    def add_row(self, database, table, values, columns=None):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"USE {database}")
                
                # Get column names
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                table_columns = [column[0] for column in cursor.fetchall()]
                
                if columns is None:
                    columns = table_columns
                else:
                    # Ensure the provided columns match the table columns
                    if set(columns) != set(table_columns):
                        raise ValueError("Provided columns do not match the table columns.")
                
                # Debug print to check columns and values
                print(f"Columns: {columns}")
                print(f"Values: {values}")
                
                # Ensure the number of columns matches the number of values
                if len(columns) != len(values):
                    raise ValueError("Column count doesn't match value count.")
                
                # Create the INSERT query
                placeholders = ", ".join(["%s"] * len(values))
                columns_str = ", ".join(columns)
                query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                
                cursor.execute(query, values)
                self.connection.commit()  # Corrected this line
                return True
            except Error as e:
                print(f"Error adding row: {e}")
                return False
        return False
        
    def delete_row(self, database, table, condition_column, condition_value):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"USE {database}")
                cursor.execute(f"DELETE FROM {table} WHERE {condition_column} = %s", (condition_value,))
                self.connection.commit()
                return True
            except Error as e:
                print(f"Error deleting row: {e}")
                return False
        return False
    
    def get_product_by_id(self, product_id):
        if self.connection:
            try:
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute("USE farmer_schema")
                cursor.execute("SELECT * FROM Product WHERE ProductID = %s", (product_id,))
                return cursor.fetchone()
            except Error as e:
                print(f"Error fetching product by ID: {e}")
                return None
        return None

    def get_inventory_by_id(self, inventory_id):
        if self.connection:
            try:
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute("USE farmer_schema")
                cursor.execute("SELECT * FROM Inventory WHERE InventoryID = %s", (inventory_id,))
                return cursor.fetchone()
            except Error as e:
                print(f"Error fetching inventory by ID: {e}")
                return None
        return None

class CreateTableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = []
        self.setup_ui()

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
            QWidget {
                background-color: #1e1e1e;
            }
        """)

        # Create main central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Top toolbar for CRUD operations
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout.setSpacing(5)

        # Create CRUD buttons
        self.create_table_btn = QPushButton("Create Table")
        self.delete_table_btn = QPushButton("Delete Table")
        self.add_column_btn = QPushButton("Add Column")
        self.delete_column_btn = QPushButton("Delete Column")
        self.add_row_btn = QPushButton("Add Row")
        self.delete_row_btn = QPushButton("Delete Row")

        # Style buttons
        button_style = """
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3EB489;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3EB489;
                color: #1e1e1e;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                border: 2px solid #666666;
                color: #666666;
            }
        """
        
        for btn in [self.create_table_btn, self.delete_table_btn, 
                   self.add_column_btn, self.delete_column_btn,
                   self.add_row_btn, self.delete_row_btn]:
            btn.setStyleSheet(button_style)
            toolbar_layout.addWidget(btn)

        # Add toolbar to main layout
        main_layout.addWidget(toolbar_widget)

        # Content area with all three sections in a horizontal layout
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(5, 5, 5, 5)

        # Left panel for databases
        left_panel = QWidget()
        left_panel.setFixedWidth(200)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        db_label = QLabel("Databases")
        db_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        left_layout.addWidget(db_label)
        
        self.db_scroll = QScrollArea()
        self.db_scroll.setWidgetResizable(True)
        self.db_widget = QWidget()
        self.db_layout = QVBoxLayout(self.db_widget)
        self.db_layout.setSpacing(5)
        self.db_layout.setContentsMargins(0, 0, 0, 0)
        self.db_scroll.setWidget(self.db_widget)
        left_layout.addWidget(self.db_scroll)

        # Middle panel for tables
        middle_panel = QWidget()
        middle_panel.setFixedWidth(200)
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.setContentsMargins(5, 5, 5, 5)
        
        table_label = QLabel("Tables")
        table_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        middle_layout.addWidget(table_label)
        
        self.table_scroll = QScrollArea()
        self.table_scroll.setWidgetResizable(True)
        self.table_widget = QWidget()
        self.table_layout = QVBoxLayout(self.table_widget)
        self.table_layout.setSpacing(5)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        self.table_scroll.setWidget(self.table_widget)
        middle_layout.addWidget(self.table_scroll)

        # Right panel for table contents
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(5, 5, 5, 5)

        # Add all panels to content layout
        content_layout.addWidget(left_panel)
        content_layout.addWidget(middle_panel)
        content_layout.addWidget(self.right_panel)

        # Add content widget to main layout
        main_layout.addWidget(content_widget)

        # Style scroll areas
        scroll_style = """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
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
        """
        self.db_scroll.setStyleSheet(scroll_style)
        self.table_scroll.setStyleSheet(scroll_style)

        # Connect button signals
        self.create_table_btn.clicked.connect(self.create_table)
        self.delete_table_btn.clicked.connect(self.delete_table)
        self.add_column_btn.clicked.connect(self.add_column)
        self.delete_column_btn.clicked.connect(self.delete_column)
        self.add_row_btn.clicked.connect(self.add_row)
        self.delete_row_btn.clicked.connect(self.delete_row)

        # Set initial button states
        self.update_button_states()

        # Load initial data
        self.load_databases()

    def add_column_fields(self):
        column_widget = QWidget()
        column_layout = QHBoxLayout(column_widget)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Column Name")
        
        type_combo = QComboBox()
        type_combo.addItems(["INT", "VARCHAR(255)", "TEXT", "DATE", "DECIMAL(10,2)", "BOOLEAN"])
        
        column_layout.addWidget(name_input)
        column_layout.addWidget(type_combo)
        
        self.columns_layout.addWidget(column_widget)

    def get_table_info(self):
        table_name = self.table_name_input.text()
        columns = []
        
        for i in range(self.columns_layout.count()):
            widget = self.columns_layout.itemAt(i).widget()
            if widget:
                column_layout = widget.layout()
                name_input = column_layout.itemAt(0).widget()
                type_combo = column_layout.itemAt(1).widget()
                if name_input.text():
                    columns.append((name_input.text(), type_combo.currentText()))
        
        return table_name, columns
    
    def get_product_by_id(self, product_id):
        if self.connection:
            try:
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Product WHERE ProductID = %s", (product_id,))
                return cursor.fetchone()
            except Error as e:
                print(f"Error fetching product by ID: {e}")
                return None
        return None

    def get_inventory_by_id(self, inventory_id):
        if self.connection:
            try:
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Inventory WHERE InventoryID = %s", (inventory_id,))
                return cursor.fetchone()
            except Error as e:
                print(f"Error fetching inventory by ID: {e}")
                return None
        return None

    def delete_product(self, product_id):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM Inventory WHERE ProductID = %s", (product_id,))
                cursor.execute("DELETE FROM Product WHERE ProductID = %s", (product_id,))
                self.connection.commit()
                return True
            except Error as e:
                print(f"Error deleting product: {e}")
                return False
        return False

    def delete_inventory(self, inventory_id):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM Inventory WHERE InventoryID = %s", (inventory_id,))
                self.connection.commit()
                return True
            except Error as e:
                print(f"Error deleting inventory: {e}")
                return False
        return False
    
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_connection = None
        self.user_type = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Database Login")
        self.setFixedSize(500, 600)
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

        # User Type Selection
        self.user_type_label = QLabel("Login as:", self)
        self.user_type_combo = QComboBox(self)
        self.user_type_combo.addItems(["Admin", "Farmer"])
        self.user_type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                background-color: #3d3d3d;
                color: white;
                border: 2px solid #3EB489;
                border-radius: 5px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                background-color: #252525; 
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox:focus {
                border: 2px solid #4ec49a;
            }
            QComboBox QAbstractItemView {  /* Style for dropdown menu */
                background-color: black;  /* Background of dropdown items */
                color: white;             /* Text color of dropdown items */
                selection-background-color: #3EB489; /* Highlight color */
                selection-color: #1e1e1e; /* Text color when highlighted */
                border: 1px solid #3EB489; /* Border for dropdown list */
            }
        """)
        
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
        layout.addWidget(self.user_type_label)
        layout.addWidget(self.user_type_combo)
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
        self.user_type = self.user_type_combo.currentText()
        
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
        
        # Create main central widget with vertical layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Top toolbar for CRUD operations with icons
        toolbar = QWidget()
        toolbar.setFixedHeight(100)
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-bottom: 2px solid #3d3d3d;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(15)

        # CRUD operation buttons with icons and text
        crud_actions = [
            ("Create Table", "📋➕"),   # Emoji for create table
            ("Delete Table", "📋❌"),   # Emoji for delete table
            ("Add Column", "📊➕"),     # Emoji for add column
            ("Delete Column", "📊❌"),  # Emoji for delete column
            ("Add Row", "📝➕"),  # Emoji for add row (custom choice)
            ("Delete Row", "📝❌")  # Emoji for delete row
        ]

        for text, emoji_text in crud_actions:
            btn_widget = QWidget()
            btn_layout = QVBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)

            btn = QPushButton(emoji_text)
            btn.setFixedSize(60, 60)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 24px;  /* Larger font for emoji */
                    background-color: #2d2d2d;
                    border: 2px solid #3EB489;
                    border-radius: 5px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #3EB489;
                    color: #1e1e1e;
                }
                QPushButton:disabled {
                    background-color: #2d2d2d;
                    border: 2px solid #666666;
                    color: #666666;
                }
            """)

            label = QLabel(text)
            label.setStyleSheet("color: white; font-size: 10px;")
            label.setAlignment(Qt.AlignCenter)

            btn_layout.addWidget(btn, alignment=Qt.AlignCenter)
            btn_layout.addWidget(label, alignment=Qt.AlignCenter)
            toolbar_layout.addWidget(btn_widget)
            
            # Assign button variables for later use
            if text == "Create Table":
                self.create_table_btn = btn
            elif text == "Delete Table":
                self.delete_table_btn = btn
            elif text == "Add Column":
                self.add_column_btn = btn
            elif text == "Delete Column":
                self.delete_column_btn = btn
            elif text == "Add Row":
                self.add_row_btn = btn
            else:
                self.delete_row_btn = btn

        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)

        # Content area contains databases, tables, and data view
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Left panel for databases
        db_panel = QWidget()
        db_panel.setFixedWidth(200)
        db_panel.setStyleSheet("background-color: #1e1e1e;")
        db_layout = QVBoxLayout(db_panel)
        db_layout.setContentsMargins(10, 10, 10, 10)
        
        db_label = QLabel("Databases")
        db_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding: 5px;")
        db_layout.addWidget(db_label)
        
        self.db_scroll = QScrollArea()
        self.db_scroll.setWidgetResizable(True)
        self.db_widget = QWidget()
        self.db_layout = QVBoxLayout(self.db_widget)
        self.db_scroll.setWidget(self.db_widget)
        db_layout.addWidget(self.db_scroll)

        # Middle panel for tables
        table_panel = QWidget()
        table_panel.setFixedWidth(200)
        table_panel.setStyleSheet("background-color: #1e1e1e;")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(10, 10, 10, 10)
        
        table_label = QLabel("Tables")
        table_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding: 5px;")
        table_layout.addWidget(table_label)
        
        self.table_scroll = QScrollArea()
        self.table_scroll.setWidgetResizable(True)
        self.table_widget = QWidget()
        self.table_layout = QVBoxLayout(self.table_widget)
        self.table_scroll.setWidget(self.table_widget)
        table_layout.addWidget(self.table_scroll)

        # Right panel for table contents
        self.right_panel = QWidget()
        self.right_panel.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-left: 2px solid #3d3d3d;
            }
        """)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(10, 10, 10, 10)

        # Add panels to content layout
        content_layout.addWidget(db_panel)
        content_layout.addWidget(table_panel)
        content_layout.addWidget(self.right_panel)

        # Add content widget to main layout
        main_layout.addWidget(content_widget)

        # Style scrollbars
        scroll_style = """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
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
        """
        self.db_scroll.setStyleSheet(scroll_style)
        self.table_scroll.setStyleSheet(scroll_style)

        # Connect button signals
        self.create_table_btn.clicked.connect(self.create_table)
        self.delete_table_btn.clicked.connect(self.delete_table)
        self.add_column_btn.clicked.connect(self.add_column)
        self.delete_column_btn.clicked.connect(self.delete_column)
        self.add_row_btn.clicked.connect(self.add_row)
        self.delete_row_btn.clicked.connect(self.delete_row)

        # Set initial button states
        self.update_button_states()

        # Load initial data
        self.load_databases()

    def update_button_states(self):
        has_database = self.current_database is not None
        has_table = self.current_table is not None

        self.create_table_btn.setEnabled(has_database)
        self.delete_table_btn.setEnabled(has_table)
        self.add_column_btn.setEnabled(has_table)
        self.delete_column_btn.setEnabled(has_table)
        self.add_row_btn.setEnabled(has_table)
        self.delete_row_btn.setEnabled(has_table)

    def select_database(self, db):
        self.current_database = db
        self.current_table = None
        self.update_button_states()
        self.load_tables()

    def select_table(self, table):
        self.current_table = table
        self.update_button_states()
        self.display_table(table)

    def create_table(self):
        dialog = CreateTableDialog(self)
        if dialog.exec_():
            table_name, columns = dialog.get_table_info()
            if table_name and columns:
                if self.db_connection.create_table(self.current_database, table_name, columns):
                    self.load_tables()
                    QMessageBox.information(self, "Success", f"Table '{table_name}' created successfully")
                else:
                    QMessageBox.warning(self, "Error", "Failed to create table")

    def delete_table(self):
        if not self.current_table:
            return

        reply = QMessageBox.question(self, 'Confirm Delete', 
                                   f"Are you sure you want to delete table '{self.current_table}'?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.db_connection.delete_table(self.current_database, self.current_table):
                self.current_table = None
                self.load_tables()
                self.update_button_states()
                QMessageBox.information(self, "Success", "Table deleted successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete table")

    def add_column(self):
        if not self.current_table:
            return

        column_name, ok = QInputDialog.getText(self, "Add Column", "Enter column name:")
        if ok and column_name:
            type_dialog = QInputDialog(self)
            type_dialog.setComboBoxItems(["INT", "VARCHAR(255)", "TEXT", "DATE", "DECIMAL(10,2)", "BOOLEAN"])
            type_dialog.setWindowTitle("Select Column Type")
            type_dialog.setLabelText("Select column type:")
            
            if type_dialog.exec_():
                column_type = type_dialog.textValue()
                if self.db_connection.add_column(self.current_database, self.current_table, 
                                              column_name, column_type):
                    self.display_table(self.current_table)
                    QMessageBox.information(self, "Success", "Column added successfully")
                else:
                    QMessageBox.warning(self, "Error", "Failed to add column")

    def delete_column(self):
        if not self.current_table:
            return

        # Get current columns
        _, columns = self.db_connection.get_table_contents(self.current_database, self.current_table)
        column_names = [col[0] for col in columns]

        column_name, ok = QInputDialog.getItem(self, "Delete Column", 
                                             "Select column to delete:", 
                                             column_names, 0, False)
        if ok and column_name:
            reply = QMessageBox.question(self, 'Confirm Delete', 
                                       f"Are you sure you want to delete column '{column_name}'?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                if self.db_connection.delete_column(self.current_database, self.current_table, 
                                                  column_name):
                    self.display_table(self.current_table)
                    QMessageBox.information(self, "Success", "Column deleted successfully")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete column")

    def add_row(self):
        if not self.current_table:
            return

        # Get current columns
        _, columns = self.db_connection.get_table_contents(self.current_database, self.current_table)
        
        # Create input dialog for each column
        values = []
        for col in columns:
            value, ok = QInputDialog.getText(self, "Add Row", 
                                           f"Enter value for {col[0]}:")
            if ok:
                values.append(value)
            else:
                return

        if self.db_connection.add_row(self.current_database, self.current_table, values):
            self.display_table(self.current_table)
            QMessageBox.information(self, "Success", "Row added successfully")
        else:
            QMessageBox.warning(self, "Error", "Failed to add row")
    
    def delete_row(self):
        if not self.current_table:
            return

        # Get current table data
        rows, columns = self.db_connection.get_table_contents(self.current_database, self.current_table)
        if not rows or not columns:
            QMessageBox.warning(self, "Error", "No data to delete")
            return

        # Let user select which column to use as condition for deletion
        column_names = [col[0] for col in columns]
        column, ok = QInputDialog.getItem(self, "Delete Row", 
                                        "Select column to use as condition:", 
                                        column_names, 0, False)
        if not ok:
            return

        # Get the value to match for deletion
        value, ok = QInputDialog.getText(self, "Delete Row", 
                                    f"Enter the {column} value of the row to delete:")
        if not ok:
            return

        # Confirm deletion
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                f"Are you sure you want to delete row(s) where {column} = {value}?",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.db_connection.delete_row(self.current_database, self.current_table, 
                                        column, value):
                self.display_table(self.current_table)
                QMessageBox.information(self, "Success", "Row(s) deleted successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete row(s)")

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
                QPushButton:checked {
                    background-color: #3EB489;
                    color: #1e1e1e;
                }
            """)
            db_button.setCheckable(True)
            db_button.clicked.connect(lambda checked, db=db: self.select_database(db))
            self.db_layout.addWidget(db_button)
        
        self.db_layout.addStretch()

    def load_tables(self):
        # Clear existing tables
        while self.table_layout.count():
            item = self.table_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if self.current_database:
            tables = self.db_connection.get_tables(self.current_database)
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
                    QPushButton:checked {
                        background-color: #3EB489;
                        color: #1e1e1e;
                    }
                """)
                table_button.setCheckable(True)
                table_button.clicked.connect(lambda checked, table=table: self.select_table(table))
                self.table_layout.addWidget(table_button)
        
        self.table_layout.addStretch()
        
    def select_database(self, db):
        # Uncheck all database buttons except the selected one
        for i in range(self.db_layout.count() - 1):  # -1 to exclude the stretch
            widget = self.db_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setChecked(widget.text() == db)
        
        self.current_database = db
        self.current_table = None
        self.update_button_states()
        self.load_tables()
        
        # Clear the table view when selecting a new database
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def select_table(self, table):
        # Uncheck all table buttons except the selected one
        for i in range(self.table_layout.count() - 1):  # -1 to exclude the stretch
            widget = self.table_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setChecked(widget.text() == table)
        
        self.current_table = table
        self.update_button_states()
        self.display_table(table)

    def display_table(self, table):
        # Clear existing content in right panel
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.current_database or not table:
            return
        
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
                item.setTextAlignment(Qt.AlignCenter)  # Center-align the text
                table_widget.setItem(i, j, item)
        
        # Set table properties
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_widget.verticalHeader().setVisible(False)
        table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: white;
                gridline-color: #3d3d3d;
                border: none;
                border-radius: 5px;
            }
            QTableWidget QHeaderView::section {
                background-color: #252525;
                color: white;
                padding: 8px;
                border: 1px solid #3d3d3d;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3EB489;
                color: #1e1e1e;
            }
        """)
        
        # Add table widget to right panel
        self.right_layout.addWidget(table_widget)  

class CreateTableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = []
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Create New Table")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: 2px solid #3EB489;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3EB489;
                color: #1e1e1e;
            }
            QLineEdit {
                padding: 8px;
                background-color: #3d3d3d;
                color: white;
                border: 2px solid #3EB489;
                border-radius: 5px;
            }
            QComboBox {
                padding: 8px;
                background-color: #3d3d3d;
                color: white;
                border: 2px solid #3EB489;
                border-radius: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                margin-right: 15px;
            }
            QComboBox QAbstractItemView {  /* Style for dropdown menu */
                background-color: #2b2b2b;  /* Background of dropdown items */
                color: white;               /* Text color of dropdown items */
                selection-background-color: #3EB489; /* Highlight color */
                selection-color: #1e1e1e;   /* Text color when highlighted */
                border: 1px solid #3EB489;  /* Border for dropdown list */
            }
            QScrollArea {
                border: none;
                background-color: transparent;
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
            QWidget#columnWidget {
                background-color: #2b2b2b;
            }
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Table name input
        name_label = QLabel("Table Name:")
        self.table_name_input = QLineEdit()
        layout.addWidget(name_label)
        layout.addWidget(self.table_name_input)

        # Columns section
        columns_label = QLabel("Columns:")
        layout.addWidget(columns_label)

        # Scrollable area for columns
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        columns_widget = QWidget()
        columns_widget.setObjectName("columnWidget")  # Assigning an ID for custom styling
        self.columns_layout = QVBoxLayout(columns_widget)
        scroll.setWidget(columns_widget)
        layout.addWidget(scroll)

        # Add initial column field
        self.add_column_fields()

        # Add Column button
        add_column_btn = QPushButton("Add Another Column")
        add_column_btn.clicked.connect(self.add_column_fields)
        layout.addWidget(add_column_btn)

        # Button box for OK/Cancel
        button_box = QHBoxLayout()
        ok_button = QPushButton("Create Table")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

    def add_column_fields(self):
        column_widget = QWidget()
        column_widget.setObjectName("columnWidget")  # Assigning an ID for custom styling

        column_layout = QHBoxLayout(column_widget)
        column_layout.setContentsMargins(0, 0, 0, 0)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Column Name")
        
        type_combo = QComboBox()
        type_combo.addItems(["INT", "VARCHAR(255)", "TEXT", "DATE", "DECIMAL(10,2)", "BOOLEAN"])
        
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(30, 30)
        delete_btn.clicked.connect(lambda: self.delete_column_fields(column_widget))
        
        column_layout.addWidget(name_input)
        column_layout.addWidget(type_combo)
        column_layout.addWidget(delete_btn)
        
        self.columns_layout.addWidget(column_widget)

    def delete_column_fields(self, widget):
        widget.deleteLater()

    def get_table_info(self):
        table_name = self.table_name_input.text()
        columns = []
        
        for i in range(self.columns_layout.count()):
            widget = self.columns_layout.itemAt(i).widget()
            if widget:
                column_layout = widget.layout()
                name_input = column_layout.itemAt(0).widget()
                type_combo = column_layout.itemAt(1).widget()
                if name_input.text():  # Only add if name is not empty
                    columns.append((name_input.text(), type_combo.currentText()))
        
        return table_name, columns
    
if __name__ == "__main__":
        app = QApplication(sys.argv)
        
        # Set application-wide style
        app.setStyle('Fusion')
        
        # Show login dialog
        login_dialog = LoginDialog()

        if login_dialog.exec_() == QDialog.Accepted:
            print("Login accepted, creating main window")
            db_connection = login_dialog.db_connection
            user_type = login_dialog.user_type
            
            if user_type == "Admin":
                main_window = MainWindow(db_connection)
            elif user_type == "Farmer":
                main_window = FarmerMainWindow(db_connection)
            
            main_window.show()
            sys.exit(app.exec_())

        else:
            print("Login cancelled or failed")
            sys.exit
