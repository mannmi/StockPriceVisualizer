import sys
import asyncio
import requests
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QPushButton, QHBoxLayout, QLineEdit, QMenuBar, QMenu, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from qasync import QEventLoop, asyncSlot

from src.logging.logging_config import logger
from src.server.yahoo.yahooRunner import yahooRunner
from ui.PlotWindow import PlotWindow


# from src/ import yahooRunner


class RenderThread(QThread):
    update_progress = pyqtSignal(int)
    render_complete = pyqtSignal(object)

    def __init__(self, runner, filters, watcher=True, fetch_from_file=False):
        super().__init__()
        self.fetchFromFile = fetch_from_file
        self.runner = runner
        self.filters = filters
        self.watcher = watcher

    def run(self):
        if self.watcher:
            tickers_list = self.runner.get_tickers()
        else:
            if self.fetchFromFile:
                tickers_list = self.runner.get_tickers(False)
            else:
                tickers_list = self.runner.get_tickers_from_variable()

        # Apply filters
        total_filters = len(self.filters)
        for i, (filter_column, filter_value) in enumerate(self.filters):
            if filter_value:
                # Convert wildcard * to regex .*
                filter_value = filter_value.replace('*', '.*')
                tickers_list = tickers_list[
                    tickers_list[filter_column.lower()].str.contains(filter_value, case=False, regex=True)]
            progress = int(((i + 1) / total_filters) * 100)
            self.update_progress.emit(progress)  # Update progress bar

        self.render_complete.emit(tickers_list)


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading")
        self.setModal(True)
        self.setGeometry(300, 300, 300, 100)

        layout = QVBoxLayout()
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def set_progress(self, value):
        self.progress_bar.setValue(value)


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Yahoo Runner')
        self.setGeometry(100, 100, 600, 400)
        self.plot_windows = []  # Keep track of plot windows

        api_key_Load = "Test key to load"
        docker_config = r"C:\Users\mannnmi\CryptoPrediction\docker-compose.yml"
        config_path = r"C:\Users\mannnmi\CryptoPrediction\config_loader\config.yml"
        tickerFilePath = r"C:\Users\mannnmi\CryptoPrediction\src\server\listing_status.csv"
        self.runner = yahooRunner(api_key_Load, docker_config, config_path, tickerFilePath)

        layout = QVBoxLayout()

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.table = QTableWidget(self)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Symbol", "Name", "Exchange", "Asset Type", "IPO Date", "Delisting Date", "Status", "Watching", "Visualize"
        ])
        layout.addWidget(self.table)
        self.table.setVisible(False)  # Initially hide the table

        # Add filter section
        self.filter_layout = QVBoxLayout()
        layout.addLayout(self.filter_layout)

        # Add Apply button
        btn_apply_filter = QPushButton('Apply Filter', self)
        btn_apply_filter.clicked.connect(self.apply_filter)
        layout.addWidget(btn_apply_filter)

        # Create menu bar
        menu_bar = QMenuBar(self)

        # Create menus
        filter_menu = QMenu("Filter", self)
        watch_list_menu = QMenu("Watch List", self)
        ticker_list_menu = QMenu("Ticker List", self)
        tickers_file_menu = QMenu("Tickers File", self)

        # Add actions to menus
        filter_menu.addAction("Add Filter", self.add_filter_row)
        watch_list_menu.addAction("Get Watched List", self.get_watched_list)
        watch_list_menu.addAction("Update Watch List", self.update_watch_list)
        ticker_list_menu.addAction("Update Ticker List", self.update_ticker_list)
        ticker_list_menu.addAction("Store Ticker List", self.store_ticker_list)
        tickers_file_menu.addAction("Get All Tickers File", self.get_all_tickers_file)
        tickers_file_menu.addAction("Get All Tickers Variable", self.get_all_tickers_variable)
        tickers_file_menu.addAction("Get All Tickers Database", self.get_all_tickers_db)

        # Add menus to menu bar
        menu_bar.addMenu(filter_menu)
        menu_bar.addMenu(watch_list_menu)
        menu_bar.addMenu(ticker_list_menu)
        menu_bar.addMenu(tickers_file_menu)

        layout.setMenuBar(menu_bar)
        self.setLayout(layout)

    def add_filter_row(self):
        filter_row = QHBoxLayout()
        filter_input = QLineEdit(self)
        filter_row.addWidget(filter_input)

        btn_add_filter = QPushButton('Add Filter', self)
        btn_add_filter.clicked.connect(self.add_filter_row)
        filter_row.addWidget(btn_add_filter)

        self.filter_layout.addLayout(filter_row)

    @asyncSlot()
    async def apply_filter(self):
        filters = self.get_filters()
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.post, 'http://127.0.0.1:8000/api/apply_filters/',
                                              {'filters': filters})

        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            self.output.append("Error: Received invalid JSON response")
            return

        if not response_json:
            self.output.append("Error: Received empty response")
            return

        tickers_list = pd.DataFrame(response_json)

        # Replace NaN values with None
        tickers_list = tickers_list.where(pd.notnull(tickers_list), None)

        self.populate_table(tickers_list)

    def toggle_table_visibility(self, visible):
        self.table.setVisible(visible)
        logger.info(f"Table visibility set to {visible}")

    def add_filter_row(self):
        filter_row = QHBoxLayout()

        filter_dropdown = QComboBox(self)
        filter_dropdown.addItems(["Symbol", "Name", "Exchange", "Asset Type"])
        filter_row.addWidget(filter_dropdown)

        filter_input = QLineEdit(self)
        filter_input.setPlaceholderText("Enter filter value")
        filter_row.addWidget(filter_input)

        btn_remove_filter = QPushButton('Remove', self)
        btn_remove_filter.clicked.connect(lambda: self.remove_filter_row(filter_row))
        filter_row.addWidget(btn_remove_filter)

        self.filter_layout.addLayout(filter_row)

    def remove_filter_row(self, filter_row):
        for i in reversed(range(filter_row.count())):
            widget = filter_row.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.filter_layout.removeItem(filter_row)

    def get_filters(self):
        filters = []
        for i in range(self.filter_layout.count()):
            filter_row = self.filter_layout.itemAt(i).layout()
            filter_dropdown = filter_row.itemAt(0).widget()
            filter_input = filter_row.itemAt(1).widget()
            filters.append((filter_dropdown.currentText(), filter_input.text()))
        return filters

    @asyncSlot()
    async def get_watched_list(self):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get, 'http://127.0.0.1:8000/api/get_watched_list_all/')
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            self.output.append("Error: Received invalid JSON response")
            return

        if not response_json:
            self.output.append("Error: Received empty response")
            return

        tickers_list = pd.DataFrame(response_json)
        self.populate_table(tickers_list)

    @asyncSlot()
    async def get_all_tickers_file(self):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get, 'http://127.0.0.1:8000/api/get_all_tickers_file/')
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            self.output.append("Error: Received invalid JSON response")
            return

        if not response_json:
            self.output.append("Error: Received empty response")
            return

        tickers_list = pd.DataFrame(response_json)
        self.populate_table(tickers_list)

    @asyncSlot()
    async def get_all_tickers_db(self):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get,
                                              'http://127.0.0.1:8000/api/get_tickers_from_variable/')
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            self.output.append("Error: Received invalid JSON response")
            return

        if not response_json:
            self.output.append("Error: Received empty response")
            return

        tickers_list = pd.DataFrame(response_json)
        self.populate_table(tickers_list)

    @asyncSlot()
    async def get_all_tickers_variable(self):
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get,
                                              'http://127.0.0.1:8000/api/get_tickers_from_variable/')
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            self.output.append("Error: Received invalid JSON response")
            return

        if not response_json:
            self.output.append("Error: Received empty response")
            return

        tickers_list = pd.DataFrame(response_json)
        self.populate_table(tickers_list)

    def populate_table(self, tickers_list):
        self.output.append(f"Watched List: {tickers_list}")
        self.table.setRowCount(len(tickers_list))

        for row_index, row in tickers_list.iterrows():
            self.table.setItem(row_index, 0, self.create_read_only_item(row['symbol']))
            self.table.setItem(row_index, 1, self.create_read_only_item(row['name']))
            self.table.setItem(row_index, 2, self.create_read_only_item(row['exchange']))
            self.table.setItem(row_index, 3, self.create_read_only_item(row['assetType']))
            self.table.setItem(row_index, 4, self.create_read_only_item(str(row['ipoDate'])))
            self.table.setItem(row_index, 5, self.create_read_only_item(str(row['delistingDate'])))
            self.table.setItem(row_index, 6, self.create_read_only_item(row['status']))

            watching_combobox = QComboBox()
            watching_combobox.addItems(["False", "True"])
            watching_combobox.setCurrentText("True" if row['watching'] == 1 else "False")
            watching_combobox.currentIndexChanged.connect(
                lambda index, row=row: self.update_watching_status(row, index))
            self.table.setCellWidget(row_index, 7, watching_combobox)

            btn_visualize = QPushButton('Visualize', self)
            btn_visualize.clicked.connect(lambda _, row=row: self.visualize_row(row))
            self.table.setCellWidget(row_index, 8, btn_visualize)

        if not tickers_list.empty:
            self.toggle_table_visibility(True)
            self.show()

    def create_read_only_item(self, text):
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        return item

    @asyncSlot()
    async def update_watching_status(self, row, index):
        loop = asyncio.get_event_loop()
        if index == 1:
            await loop.run_in_executor(None, requests.post, 'http://127.0.0.1:8000/api/add_to_watch_list/',
                                       {'tickers': row["symbol"]})
            new_status = 1
        else:
            await loop.run_in_executor(None, requests.post, 'http://127.0.0.1:8000/api/remove_from_watch_list/',
                                       {'tickers': row["symbol"]})
            new_status = 0

        row['watching'] = new_status
        logger.info(f"Updated row {row['symbol']} watching status to {new_status}")

    @asyncSlot()
    async def update_watch_list(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, requests.post, 'http://127.0.0.1:8000/api/update_watch_list/',
                                   {'tickers': "A"})
        logger.info("Watch list updated")

    @asyncSlot()
    async def update_ticker_list(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, requests.post, 'http://127.0.0.1:8000/api/update_ticker_list/')
        self.output.append("Ticker list updated.")

    @asyncSlot()
    async def store_ticker_list(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, requests.post, 'http://127.0.0.1:8000/api/store_ticker_list/',
                                   {'tickers': "A"})
        self.output.append("Ticker list stored.")

    def visualize_row(self, row):
        logger.info("visulaisation Started")
        all_data = self.runner.load_data(row)
        fig, config = self.runner.plotGraph(all_data, chunk_size=1000)
        if fig is None:
            logger.info("No data to plot.")
            logger.debug(fig, config)
            return

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        plot_window = PlotWindow(fig, config)
        plot_window.show()
        self.plot_windows.append(plot_window)  # Keep a reference

        if not QApplication.instance():
            app.exec()


def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    demo = AppDemo()
    demo.show()

    with loop:
        loop.run_forever()


if __name__ == '__main__':
    main()
