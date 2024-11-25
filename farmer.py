import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QMessageBox, QInputDialog, QLineEdit,
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import datetime

class GraphWindow(QDialog):
    def __init__(self, title, rows, columns, graph_func):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 1200, 600)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add padding around the widgets
        self.setLayout(main_layout)
        
        # Table
        table_widget = QTableWidget()
        table_widget.setRowCount(len(rows))
        table_widget.setColumnCount(len(columns))
        table_widget.setHorizontalHeaderLabels([col[0] for col in columns])
        
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignCenter)
                table_widget.setItem(i, j, item)
        
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_widget.verticalHeader().setVisible(False)
        table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: white;
                gridline-color: #3d3d3d;
                border: none;
            }
            QTableWidget QHeaderView::section {
                background-color: #252525;
                color: white;
                padding: 20px;
                border: None;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(table_widget)
        
        # Graph
        fig, ax = plt.subplots()
        graph_func(ax, rows)
        canvas = FigureCanvas(fig)
        main_layout.addWidget(canvas)

class FarmerMainWindow(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.current_database = "farmer_schema"
        self.current_table = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Farmer Database Manager")
        self.setGeometry(100, 100, 1400, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(220)
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-bottom: 2px solid #3d3d3d;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
        toolbar_layout.setSpacing(20)

        crud_actions = [
            ("Product Management", "📦", "Manage products, categories, and pricing"),
            ("Inventory Control", "📊", "Track stock levels and manage inventory"),
            ("Sales Records", "💰", "Record and manage sales transactions"),
            ("Customer Data", "👥", "Manage customer information and preferences"),
            ("Analytics", "📈", "View reports and sales performance"),
            ("Seasonal Trends", "🗓️", "Track seasonal demands and trends")
        ]

        for text, emoji_text, description in crud_actions:
            btn_widget = QWidget()
            btn_layout = QVBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)

            btn = QPushButton(f"{emoji_text}\n{text}")
            btn.setFixedSize(200, 120)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    background-color: #2d2d2d;
                    border: 2px solid #3EB489;
                    border-radius: 8px;
                    color: white;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #3EB489;
                    color: #1e1e1e;
                }
            """)

            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                color: #d4d4d4;
                font-size: 13px;
                padding: 5px;
            """)
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setWordWrap(True)

            btn_layout.addWidget(btn, alignment=Qt.AlignCenter)
            btn_layout.addWidget(desc_label, alignment=Qt.AlignCenter)
            toolbar_layout.addWidget(btn_widget)
            
            # Assign buttons to instance variables and create menus
            if text == "Product Management":
                self.product_btn = btn
                self.product_btn.setMenu(self.create_product_menu())
            elif text == "Inventory Control":
                self.inventory_btn = btn
                self.inventory_btn.setMenu(self.create_inventory_menu())
            elif text == "Sales Records":
                self.sales_btn = btn
                self.sales_btn.setMenu(self.create_sales_menu())
            elif text == "Customer Data":
                self.customer_btn = btn
                self.customer_btn.setMenu(self.create_customer_menu())
            elif text == "Analytics":
                self.analytics_btn = btn
                self.analytics_btn.setMenu(self.create_analytics_menu())
            elif text == "Seasonal Trends":
                self.seasonal_btn = btn
                self.seasonal_btn.setMenu(self.create_seasonal_menu())

        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar)

        # Content area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Table panel
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

        # Right panel
        self.right_panel = QWidget()
        self.right_panel.setStyleSheet("""
            QWidget {
                background-color: #252525;
                border-left: 2px solid #3d3d3d;
            }
        """)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(10, 10, 10, 10)

        content_layout.addWidget(table_panel)
        content_layout.addWidget(self.right_panel)
        main_layout.addWidget(content_widget)

        # Load initial data
        self.load_tables()

    def create_product_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self._get_menu_style())
        menu.addAction("Add New Product", self.create_product_dialog)
        menu.addAction("View Products", self.view_products)
        menu.addAction("Update Product", self.update_product_dialog)
        menu.addAction("Remove Product", self.delete_product_dialog)
        return menu

    def create_inventory_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self._get_menu_style())
        menu.addAction("Add Stock", self.add_inventory_dialog)
        menu.addAction("Check Stock Levels", self.view_inventory)
        menu.addAction("Update Stock", self.update_inventory_dialog)
        menu.addAction("Remove Stock Entry", self.delete_inventory_dialog)
        return menu

    def create_sales_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self._get_menu_style())
        menu.addAction("New Sale", self.create_sale)
        menu.addAction("View Sales", self.view_sales)
        return menu

    def create_customer_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self._get_menu_style())
        menu.addAction("Add Customer", self.add_customer)
        menu.addAction("View Customers", self.view_customers)
        return menu

    def create_analytics_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self._get_menu_style())
        menu.addAction("Sales Analytics", self.view_sales_analytics)
        menu.addAction("Inventory Analytics", self.view_inventory_analytics)
        return menu

    def create_seasonal_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self._get_menu_style())
        menu.addAction("Seasonal Patterns", self.view_seasonal_patterns)
        menu.addAction("Forecast Demand", self.forecast_demand)
        return menu

    def _get_menu_style(self):
        return """
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #3EB489;
                color: white;
            }
            QMenu::item:selected {
                background-color: #3EB489;
                color: #1e1e1e;
            }
        """

    def load_tables(self):
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
                """)
                table_button.clicked.connect(lambda checked, t=table: self.select_table(t))
                self.table_layout.addWidget(table_button)
        
        self.table_layout.addStretch()

    def select_table(self, table):
        self.current_table = table
        self.display_table(table)

    def display_table(self, table):
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.current_database or not table:
            return
        
        title_label = QLabel(f"Table: {table}")
        title_label.setStyleSheet("""
            color: #d4d4d4;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        self.right_layout.addWidget(title_label)
        
        rows, columns = self.db_connection.get_table_contents(self.current_database, table)
        
        table_widget = QTableWidget()
        table_widget.setRowCount(len(rows))
        table_widget.setColumnCount(len(columns))
        table_widget.setHorizontalHeaderLabels([col[0] for col in columns])
        
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignCenter)
                table_widget.setItem(i, j, item)
        
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_widget.verticalHeader().setVisible(False)
        table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #2d2d2d;
                color: white;
                gridline-color: #3d3d3d;
                border: none;
            }
            QTableWidget QHeaderView::section {
                background-color: #252525;
                color: white;
                padding: 8px;
                border: 1px solid #3d3d3d;
                font-weight: bold;
            }
        """)
        
        self.right_layout.addWidget(table_widget)


    # Implement all the necessary methods to handle menu actions
    def create_product_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Product")
        dialog.setGeometry(100, 100, 400, 300)
        
        layout = QFormLayout(dialog)
        
        product_id_input = QLineEdit()
        name_input = QLineEdit()
        category_input = QLineEdit()
        price_input = QLineEdit()
        seasonal_availability_input = QLineEdit()
        
        layout.addRow("Product ID:", product_id_input)
        layout.addRow("Name:", name_input)
        layout.addRow("Category:", category_input)
        layout.addRow("Price:", price_input)
        layout.addRow("Seasonal Availability:", seasonal_availability_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_product(product_id_input.text(), name_input.text(), category_input.text(), price_input.text(), seasonal_availability_input.text(), dialog))
        button_box.rejected.connect(dialog.reject)
        
        layout.addRow(button_box)
        
        dialog.exec_()

    def add_product(self, product_id, name, category, price, seasonal_availability, dialog):
        try:
            values = (int(product_id), name, category, float(price), seasonal_availability)
            columns = ["ProductID", "Name", "Category", "Price", "SeasonalAvailability"]
            success = self.db_connection.add_row(self.current_database, "Product", values, columns)
            if success:
                self.show_success("Product added successfully!")
                dialog.accept()
            else:
                self.show_error("Failed to add product.")
        except Exception as e:
            self.show_error(str(e))


    def view_products(self):
        self.current_table = "Product"
        self.display_table("Product")

    def update_product_dialog(self):
        product_id, ok = QInputDialog.getInt(self, "Update Product", "Enter Product ID:")
        if ok:
            product = self.db_connection.get_product_by_id(product_id)
            if product:
                dialog = QDialog(self)
                dialog.setWindowTitle("Update Product")
                dialog.setGeometry(100, 100, 400, 300)
                
                layout = QFormLayout(dialog)
                
                name_input = QLineEdit(product['Name'])
                category_input = QLineEdit(product['Category'])
                price_input = QLineEdit(str(product['Price']))
                seasonal_availability_input = QLineEdit(product['SeasonalAvailability'])
                
                layout.addRow("Name:", name_input)
                layout.addRow("Category:", category_input)
                layout.addRow("Price:", price_input)
                layout.addRow("Seasonal Availability:", seasonal_availability_input)
                
                button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                button_box.accepted.connect(lambda: self.update_product(product_id, name_input.text(), category_input.text(), price_input.text(), seasonal_availability_input.text(), dialog))
                button_box.rejected.connect(dialog.reject)
                
                layout.addRow(button_box)
                
                dialog.exec_()
            else:
                self.show_error("Product not found!")

    def update_product(self, product_id, name, category, price, seasonal_availability, dialog):
        try:
            values = (name, category, float(price), seasonal_availability, product_id)
            sql = f"UPDATE Product SET Name = %s, Category = %s, Price = %s, SeasonalAvailability = %s WHERE ProductID = %s"
            cursor = self.db_connection.connection.cursor()
            cursor.execute(sql, values)
            self.db_connection.connection.commit()
            self.show_success("Product updated successfully!")
            dialog.accept()
        except Exception as e:
            self.show_error(str(e))

    def delete_product_dialog(self):
        product_id, ok = QInputDialog.getInt(self, "Delete Product", "Enter Product ID:")
        if ok:
            if self.confirm_action("Are you sure you want to delete this product?"):
                try:
                    success = self.db_connection.delete_row(self.current_database, "Product", "ProductID", product_id)
                    if success:
                        self.show_success("Product deleted successfully!")
                    else:
                        self.show_error("Failed to delete product.")
                except Exception as e:
                    self.show_error(str(e))

    def add_inventory_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Stock")
        dialog.setGeometry(100, 100, 400, 300)
        
        layout = QFormLayout(dialog)
        
        inventory_id_input = QLineEdit()
        product_id_input = QLineEdit()
        vendor_id_input = QLineEdit()
        quantity_input = QLineEdit()
        restock_threshold_input = QLineEdit()
        
        layout.addRow("Inventory ID:", inventory_id_input)
        layout.addRow("Product ID:", product_id_input)
        layout.addRow("Vendor ID:", vendor_id_input)
        layout.addRow("Quantity:", quantity_input)
        layout.addRow("Restock Threshold:", restock_threshold_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_inventory(inventory_id_input.text(), product_id_input.text(), vendor_id_input.text(), quantity_input.text(), restock_threshold_input.text(), dialog))
        button_box.rejected.connect(dialog.reject)
        
        layout.addRow(button_box)
        
        dialog.exec_()

    def add_inventory(self, inventory_id, product_id, vendor_id, quantity, restock_threshold, dialog):
        try:
            values = (int(inventory_id), int(product_id), int(vendor_id), int(quantity), int(restock_threshold))
            columns = ["InventoryID", "ProductID", "VendorID", "QuantityInStock", "RestockThreshold"]
            success = self.db_connection.add_row(self.current_database, "Inventory", values, columns)
            if success:
                self.show_success("Stock added successfully!")
                dialog.accept()
            else:
                self.show_error("Failed to add stock.")
        except Exception as e:
            self.show_error(str(e))
    
    def view_inventory(self):
        self.current_table = "Inventory"
        self.display_table("Inventory")

    def update_inventory_dialog(self):
        inventory_id, ok = QInputDialog.getInt(self, "Update Inventory", "Enter Inventory ID:")
        if ok:
            inventory = self.db_connection.get_inventory_by_id(inventory_id)
            if inventory:
                dialog = QDialog(self)
                dialog.setWindowTitle("Update Inventory")
                dialog.setGeometry(100, 100, 400, 300)
                
                layout = QFormLayout(dialog)
                
                product_id_input = QLineEdit(str(inventory['ProductID']))
                vendor_id_input = QLineEdit(str(inventory['VendorID']))
                quantity_input = QLineEdit(str(inventory['QuantityInStock']))
                restock_threshold_input = QLineEdit(str(inventory['RestockThreshold']))
                
                layout.addRow("Product ID:", product_id_input)
                layout.addRow("Vendor ID:", vendor_id_input)
                layout.addRow("Quantity:", quantity_input)
                layout.addRow("Restock Threshold:", restock_threshold_input)
                
                button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                button_box.accepted.connect(lambda: self.update_inventory(inventory_id, product_id_input.text(), vendor_id_input.text(), quantity_input.text(), restock_threshold_input.text(), dialog))
                button_box.rejected.connect(dialog.reject)
                
                layout.addRow(button_box)
                
                dialog.exec_()
            else:
                self.show_error("Inventory not found!")

    def update_inventory(self, inventory_id, product_id, vendor_id, quantity, restock_threshold, dialog):
        try:
            values = (int(product_id), int(vendor_id), int(quantity), int(restock_threshold), inventory_id)
            sql = f"UPDATE Inventory SET ProductID = %s, VendorID = %s, QuantityInStock = %s, RestockThreshold = %s WHERE InventoryID = %s"
            cursor = self.db_connection.connection.cursor()
            cursor.execute(sql, values)
            self.db_connection.connection.commit()
            self.show_success("Inventory updated successfully!")
            dialog.accept()
        except Exception as e:
            self.show_error(str(e))

    def delete_inventory_dialog(self):
        inventory_id, ok = QInputDialog.getInt(self, "Delete Inventory", "Enter Inventory ID:")
        if ok:
            if self.confirm_action("Are you sure you want to delete this inventory entry?"):
                try:
                    success = self.db_connection.delete_row(self.current_database, "Inventory", "InventoryID", inventory_id)
                    if success:
                        self.show_success("Inventory entry deleted successfully!")
                    else:
                        self.show_error("Failed to delete inventory entry.")
                except Exception as e:
                    self.show_error(str(e))

    def create_sale(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("New Sale")
        dialog.setGeometry(100, 100, 400, 300)
        
        layout = QFormLayout(dialog)
        
        sale_id_input = QLineEdit()
        vendor_id_input = QLineEdit()
        product_id_input = QLineEdit()
        customer_id_input = QLineEdit()
        sale_date_input = QLineEdit()
        quantity_sold_input = QLineEdit()
        total_price_input = QLineEdit()
        
        layout.addRow("Sale ID:", sale_id_input)
        layout.addRow("Vendor ID:", vendor_id_input)
        layout.addRow("Product ID:", product_id_input)
        layout.addRow("Customer ID:", customer_id_input)
        layout.addRow("Sale Date (YYYY-MM-DD):", sale_date_input)
        layout.addRow("Quantity Sold:", quantity_sold_input)
        layout.addRow("Total Price:", total_price_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_sale(sale_id_input.text(), vendor_id_input.text(), product_id_input.text(), customer_id_input.text(), sale_date_input.text(), quantity_sold_input.text(), total_price_input.text(), dialog))
        button_box.rejected.connect(dialog.reject)
        
        layout.addRow(button_box)
        
        dialog.exec_()

    def add_sale(self, sale_id, vendor_id, product_id, customer_id, sale_date, quantity_sold, total_price, dialog):
        try:
            # Validate and format the sale date
            try:
                sale_date = datetime.datetime.strptime(sale_date, "%Y-%m-%d").date()
                if sale_date.year == 0 or sale_date.month == 0 or sale_date.day == 0:
                    raise ValueError("Invalid date: '0000-00-00' is not a valid date.")
            except ValueError as e:
                self.show_error(f"Invalid date format: {e}. Please use YYYY-MM-DD.")
                return

            values = (int(sale_id), int(vendor_id), int(product_id), int(customer_id), sale_date, int(quantity_sold), float(total_price))
            columns = ["SaleID", "VendorID", "ProductID", "CustomerID", "SaleDate", "QuantitySold", "TotalPrice"]
            success = self.db_connection.add_row(self.current_database, "Sale", values, columns)
            if success:
                self.show_success("Sale recorded successfully!")
                dialog.accept()
            else:
                self.show_error("Failed to record sale.")
        except Exception as e:
            self.show_error(str(e))

    def view_sales(self):
        self.current_table = "Sale"
        self.display_table("Sale")

    def add_customer(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Customer")
        dialog.setGeometry(100, 100, 400, 300)
        
        layout = QFormLayout(dialog)
        
        customer_id_input = QLineEdit()
        name_input = QLineEdit()
        contact_info_input = QLineEdit()
        preferences_input = QLineEdit()
        
        layout.addRow("Customer ID:", customer_id_input)
        layout.addRow("Name:", name_input)
        layout.addRow("Contact Info:", contact_info_input)
        layout.addRow("Preferences:", preferences_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_customer_to_db(customer_id_input.text(), name_input.text(), contact_info_input.text(), preferences_input.text(), dialog))
        button_box.rejected.connect(dialog.reject)
        
        layout.addRow(button_box)
        
        dialog.exec_()

    def add_customer_to_db(self, customer_id, name, contact_info, preferences, dialog):
        try:
            columns = ['CustomerID', 'Name', 'ContactInfo', 'Preferences']
            values = (int(customer_id), name, contact_info, preferences)
            success = self.db_connection.add_row(self.current_database, "Customer", values, columns)
            if success:
                self.show_success("Customer added successfully!")
                dialog.accept()
            else:
                self.show_error("Failed to add customer.")
        except Exception as e:
            self.show_error(str(e))


    def view_customers(self):
        self.current_table = "Customer"
        self.display_table("Customer")

    def view_sales_analytics(self):
        try:
            sql = """
            SELECT p.Name, SUM(s.QuantitySold) AS TotalUnitsSold, SUM(s.TotalPrice) AS TotalRevenue
            FROM Sale s
            JOIN Product p ON s.ProductID = p.ProductID
            GROUP BY p.ProductID;
            """
            cursor = self.db_connection.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = cursor.description
            self.open_graph_window("Sales Analytics", rows, columns, self.display_sales_analytics_graph)
        except Exception as e:
            self.show_error(str(e))

    def display_sales_analytics_graph(self, ax, rows):
        products = [row[0] for row in rows]
        total_units_sold = [row[1] for row in rows]
        total_revenue = [row[2] for row in rows]

        ax.set_xlabel('Products')
        ax.set_ylabel('Total Units Sold', color='tab:blue')
        ax.bar(products, total_units_sold, color='tab:blue')
        ax.tick_params(axis='y', labelcolor='tab:blue')

        ax2 = ax.twinx()
        ax2.set_ylabel('Total Revenue', color='tab:red')
        ax2.plot(products, total_revenue, color='tab:red', marker='o')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        ax.set_xticks(range(len(products)))
        ax.set_xticklabels(products, rotation=45, ha='right')

    def view_inventory_analytics(self):
        try:
            sql = """
            SELECT p.Name, i.QuantityInStock, i.RestockThreshold
            FROM Inventory i
            JOIN Product p ON i.ProductID = p.ProductID;
            """
            cursor = self.db_connection.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = cursor.description
            self.open_graph_window("Inventory Analytics", rows, columns, self.display_inventory_analytics_graph)
        except Exception as e:
            self.show_error(str(e))

    def display_inventory_analytics_graph(self, ax, rows):
        products = [row[0] for row in rows]
        quantity_in_stock = [row[1] for row in rows]
        restock_threshold = [row[2] for row in rows]

        ax.set_xlabel('Products')
        ax.set_ylabel('Quantity')
        ax.bar(products, quantity_in_stock, color='tab:blue', label='Quantity In Stock')
        ax.plot(products, restock_threshold, color='tab:red', marker='o', label='Restock Threshold')
        ax.legend()

        ax.set_xticks(range(len(products)))
        ax.set_xticklabels(products, rotation=45, ha='right')

    def view_seasonal_patterns(self):
        try:
            sql = """
            SELECT p.Name, sa.DemandTrend, sa.SeasonalPeakPeriod
            FROM SeasonalAnalysis sa
            JOIN Product p ON sa.ProductID = p.ProductID;
            """
            cursor = self.db_connection.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = cursor.description
            self.open_graph_window("Seasonal Patterns", rows, columns, self.display_seasonal_patterns_graph)
        except Exception as e:
            self.show_error(str(e))

    def display_seasonal_patterns_graph(self, ax, rows):
        products = [row[0] for row in rows]
        demand_trends = [row[1] for row in rows]
        seasonal_peak_periods = [row[2] for row in rows]

        ax.set_xlabel('Products')
        ax.set_ylabel('Demand Trend')
        ax.bar(products, demand_trends, color='tab:blue')

        for i, txt in enumerate(seasonal_peak_periods):
            ax.annotate(txt, (products[i], demand_trends[i]), textcoords="offset points", xytext=(0,10), ha='center')

        ax.set_xticks(range(len(products)))
        ax.set_xticklabels(products, rotation=45, ha='right')

    def forecast_demand(self):
        try:
            sql = """
            SELECT p.Name, SUM(s.QuantitySold) AS TotalUnitsSold, sa.DemandTrend
            FROM Sale s
            JOIN Product p ON s.ProductID = p.ProductID
            JOIN SeasonalAnalysis sa ON p.ProductID = sa.ProductID
            GROUP BY p.ProductID, sa.DemandTrend;
            """
            cursor = self.db_connection.connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = cursor.description
            self.open_graph_window("Demand Forecast", rows, columns, self.display_forecast_demand_graph)
        except Exception as e:
            self.show_error(str(e))

    def display_forecast_demand_graph(self, ax, rows):
        products = [row[0] for row in rows]
        total_units_sold = [row[1] for row in rows]
        demand_trends = [row[2] for row in rows]

        ax.set_xlabel('Products')
        ax.set_ylabel('Total Units Sold')
        ax.bar(products, total_units_sold, color='tab:blue')

        for i, txt in enumerate(demand_trends):
            ax.annotate(txt, (products[i], total_units_sold[i]), textcoords="offset points", xytext=(0,10), ha='center')

        ax.set_xticks(range(len(products)))
        ax.set_xticklabels(products, rotation=45, ha='right')

    def open_graph_window(self, title, rows, columns, graph_func):
        graph_window = GraphWindow(title, rows, columns, graph_func)
        graph_window.exec_()

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_success(self, message):
        QMessageBox.information(self, "Success", message)

    def confirm_action(self, message):
        return QMessageBox.question(
            self, "Confirm Action", message,
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes
