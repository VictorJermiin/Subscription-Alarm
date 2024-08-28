import sys
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
                               QLineEdit, QDialog, QLabel, QDateEdit, QMessageBox, 
                               QSpinBox, QCheckBox, QSystemTrayIcon, QMenu, QFrame, QStyle,
                               QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QDate, QTimer, Signal
from PySide6.QtGui import QIcon, QColor, QPalette, QFont
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    cost = Column(Float)
    renewal_date = Column(Date)

class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    days_before = Column(Integer)
    run_at_startup = Column(Boolean)

engine = create_engine('sqlite:///subscriptions.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class ModernSubscriptionDialog(QDialog):
    def __init__(self, parent=None, subscription=None):
        super().__init__(parent)
        self.setWindowTitle("Add Subscription" if subscription is None else "Edit Subscription")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QLineEdit, QDateEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)

        layout = QVBoxLayout()

        self.name_input = QLineEdit(subscription.name if subscription else "")
        self.cost_input = QLineEdit(str(subscription.cost) if subscription else "")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        if subscription and subscription.renewal_date:
            self.date_input.setDate(QDate(subscription.renewal_date))
        else:
            self.date_input.setDate(QDate.currentDate())

        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Cost:"))
        layout.addWidget(self.cost_input)
        layout.addWidget(QLabel("Renewal Date:"))
        layout.addWidget(self.date_input)

        buttons = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def get_subscription(self):
        return Subscription(
            name=self.name_input.text(),
            cost=float(self.cost_input.text()),
            renewal_date=self.date_input.date().toPython()
        )

class ModernSettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QSpinBox, QCheckBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)

        layout = QVBoxLayout()

        self.days_before = QSpinBox()
        self.days_before.setRange(1, 30)
        self.days_before.setValue(settings.days_before if settings else 7)

        self.startup = QCheckBox("Run at startup")
        self.startup.setChecked(settings.run_at_startup if settings else False)

        layout.addWidget(QLabel("Notify days before renewal:"))
        layout.addWidget(self.days_before)
        layout.addWidget(self.startup)

        buttons = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def get_settings(self):
        return Settings(
            days_before=self.days_before.value(),
            run_at_startup=self.startup.isChecked()
        )

class ModernMainWindow(QMainWindow):
    check_renewals = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Subscription Alarm")
        self.setGeometry(100, 100, 800, 600)

        self.session = Session()

        # Set the color theme
        self.set_theme()

        # Main layout
        main_layout = QHBoxLayout()

        # Left panel (subscription table)
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search subscriptions...")
        self.search_bar.setObjectName("searchBar")
        self.search_bar.textChanged.connect(self.filter_subscriptions)

        self.subscription_table = QTableWidget()
        self.subscription_table.setColumnCount(3)
        self.subscription_table.setHorizontalHeaderLabels(["Name", "Cost", "Days Until Renewal"])
        self.subscription_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.subscription_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.subscription_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.subscription_table.setObjectName("subscriptionTable")

        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.subscription_table)

        # Right panel (buttons)
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)

        buttons = [
            ("Add Subscription", self.add_subscription),
            ("Edit Subscription", self.edit_subscription),
            ("Delete Subscription", self.delete_subscription),
            ("Settings", self.open_settings),
            ("Test", self.test_notifications)
        ]

        for text, slot in buttons:
            button = QPushButton(text)
            button.setObjectName("actionButton")
            button.clicked.connect(slot)
            right_layout.addWidget(button)

        right_layout.addStretch()

        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)

        # Set the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Initialize subscriptions
        self.load_subscriptions()

        # Set up system tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_menu = QMenu()
        self.tray_menu.addAction("Show", self.show)
        self.tray_menu.addAction("Exit", self.close)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

        # Set up timer for checking renewals
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_renewals)
        self.timer.start(86400000)  # Check every 24 hours

        self.check_renewals.connect(self.notify_renewals)

        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            #leftPanel, #rightPanel {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
            #searchBar {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            #subscriptionTable {
                border: none;
                background-color: transparent;
            }
            #subscriptionTable::item {
                padding: 5px;
            }
            #subscriptionTable QHeaderView::section {
                background-color: #4a90e2;
                color: white;
                padding: 5px;
                border: 1px solid #357abd;
            }
            #actionButton {
                padding: 10px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            #actionButton:hover {
                background-color: #357abd;
            }
        """)

    def set_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(74, 144, 226))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)

    def update_subscription_list(self):
        self.subscription_table.setRowCount(0)
        subscriptions = self.session.query(Subscription).all()
        settings = self.session.query(Settings).first()
        notification_days = settings.days_before if settings else 7
        today = datetime.now().date()

        for row, subscription in enumerate(subscriptions):
            self.subscription_table.insertRow(row)
            
            name_item = QTableWidgetItem(subscription.name)
            cost_item = QTableWidgetItem(f"${subscription.cost:.2f}")
            
            days_until_renewal = (subscription.renewal_date - today).days
            days_item = QTableWidgetItem(f"{days_until_renewal} day{'s' if days_until_renewal != 1 else ''}")
            
            if days_until_renewal <= notification_days:
                days_item.setForeground(QColor("#FF6B6B"))  # Red
            elif days_until_renewal <= 2 * notification_days:
                days_item.setForeground(QColor("#FFD93D"))  # Yellow
            else:
                days_item.setForeground(QColor("#6BCB77"))  # Green

            self.subscription_table.setItem(row, 0, name_item)
            self.subscription_table.setItem(row, 1, cost_item)
            self.subscription_table.setItem(row, 2, days_item)

            # Store the subscription ID in the first column's item
            name_item.setData(Qt.UserRole, subscription.id)

    def filter_subscriptions(self, text):
        for row in range(self.subscription_table.rowCount()):
            name_item = self.subscription_table.item(row, 0)
            if name_item:
                self.subscription_table.setRowHidden(row, text.lower() not in name_item.text().lower())

    def add_subscription(self):
        dialog = ModernSubscriptionDialog(self)
        if dialog.exec():
            new_subscription = dialog.get_subscription()
            self.session.add(new_subscription)
            self.session.commit()
            self.update_subscription_list()

    def edit_subscription(self):
        selected_rows = self.subscription_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a subscription to edit.")
            return

        row = selected_rows[0].row()
        subscription_id = self.subscription_table.item(row, 0).data(Qt.UserRole)
        subscription = self.session.query(Subscription).get(subscription_id)
        dialog = ModernSubscriptionDialog(self, subscription)
        if dialog.exec():
            updated_subscription = dialog.get_subscription()
            subscription.name = updated_subscription.name
            subscription.cost = updated_subscription.cost
            subscription.renewal_date = updated_subscription.renewal_date
            self.session.commit()
            self.update_subscription_list()

    def delete_subscription(self):
        selected_rows = self.subscription_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a subscription to delete.")
            return

        row = selected_rows[0].row()
        subscription_id = self.subscription_table.item(row, 0).data(Qt.UserRole)
        subscription = self.session.query(Subscription).get(subscription_id)
        confirmed = QMessageBox.question(self, "Confirm Deletion", 
                                         f"Are you sure you want to delete {subscription.name}?",
                                         QMessageBox.Yes | QMessageBox.No)
        if confirmed == QMessageBox.Yes:
            self.session.delete(subscription)
            self.session.commit()
            self.update_subscription_list()

    def open_settings(self):
        settings = self.session.query(Settings).first()
        if not settings:
            settings = Settings(days_before=7, run_at_startup=False)
            self.session.add(settings)
            self.session.commit()

        dialog = ModernSettingsDialog(self, settings)
        if dialog.exec():
            updated_settings = dialog.get_settings()
            settings.days_before = updated_settings.days_before
            settings.run_at_startup = updated_settings.run_at_startup
            self.session.commit()
            self.update_subscription_list()

    def load_subscriptions(self):
        self.update_subscription_list()

    def notify_renewals(self):
        settings = self.session.query(Settings).first()
        if not settings:
            return

        days_before = settings.days_before
        today = datetime.now().date()
        subscriptions = self.session.query(Subscription).all()
        for sub in subscriptions:
            days_until_renewal = (sub.renewal_date - today).days
            if 0 <= days_until_renewal <= days_before:
                self.tray_icon.showMessage(
                    "Subscription Renewal",
                    f"{sub.name} will renew in {days_until_renewal} days.",
                    QSystemTrayIcon.Information,
                    10000
                )

    def test_notifications(self):
        subscriptions = self.session.query(Subscription).all()
        today = datetime.now().date()
        settings = self.session.query(Settings).first()
        notification_days = settings.days_before if settings else 7
        
        if not subscriptions:
            QMessageBox.information(self, "No Subscriptions", "There are no subscriptions to test.")
            return

        message = "Subscription Renewals:\n\n"
        for sub in subscriptions:
            days_until_renewal = (sub.renewal_date - today).days
            if days_until_renewal <= notification_days:
                color = "red"
            elif days_until_renewal <= 2 * notification_days:
                color = "yellow"
            else:
                color = "green"
            
            renewal_info = f"{days_until_renewal} day{'s' if days_until_renewal != 1 else ''}"
            message += f"{sub.name}: {renewal_info} ({color})\n"
            
            self.tray_icon.showMessage(
                "Test: Subscription Renewal",
                f"{sub.name}: {renewal_info}",
                QSystemTrayIcon.Information,
                5000
            )
        
        QMessageBox.information(self, "Test Results", message)

    def closeEvent(self, event):
        self.session.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernMainWindow()
    window.show()
    sys.exit(app.exec())