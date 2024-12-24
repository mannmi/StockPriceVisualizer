import html
import json
import os
import sys
import asyncio
import requests
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QPushButton, QHBoxLayout, QLineEdit, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt
from qasync import QEventLoop, asyncSlot, QtGui
from src.logging.logging_config import logger
import src.os_calls.basic_os_calls as os_calls
from src.os_calls.basic_os_calls import get_root_path
from src.ui.PlotWindow import PlotWindow, has_render_failed, open_in_browser


# todo implement a loading bar
# class RenderThread(QThread):
#
#     update_progress = pyqtSignal(int)
#     render_complete = pyqtSignal(object)
#
#     def __init__(self, filters, watcher=True, fetch_from_file=False):
#         super().__init__()
#         self.fetchFromFile = fetch_from_file
#         # self.runner = runner
#         self.filters = filters
#         self.watcher = watcher
#
#     def run(self):
#         if self.watcher:
#             tickers_list = self.runner.get_tickers()
#         else:
#             if self.fetchFromFile:
#                 tickers_list = self.runner.get_tickers(False)
#             else:
#                 tickers_list = self.runner.get_tickers_from_variable()
#
#         # Apply filters
#         total_filters = len(self.filters)
#         for i, (filter_column, filter_value) in enumerate(self.filters):
#             if filter_value:
#                 # Convert wildcard * to regex .*
#                 filter_value = filter_value.replace('*', '.*')
#                 tickers_list = tickers_list[
#                     tickers_list[filter_column.lower()].str.contains(filter_value, case=False, regex=True)]
#             progress = int(((i + 1) / total_filters) * 100)
#             self.update_progress.emit(progress)  # Update progress bar
#
#         self.render_complete.emit(tickers_list)


# class ProgressDialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Loading")
#         self.setModal(True)
#         self.setGeometry(300, 300, 300, 100)
#
#         layout = QVBoxLayout()
#         self.progress_bar = QProgressBar(self)
#         layout.addWidget(self.progress_bar)
#         self.setLayout(layout)
#
#     def set_progress(self, value):
#         self.progress_bar.setValue(value)


def create_read_only_item(text):
    """
    Marks The object as read-only.
    Text field are no longer modifiable by user.
    Args:
        text: Text that is supposed to be read-only.

    Returns: Return the text as a QTableWidgetItem

    """
    item = QTableWidgetItem(text)
    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
    return item


def store_html(fig_html):
    """
    @brief store html for debugging purpose
    Args:
        fig_html: the html to be stored

    """
    try:
        with open("./tmp_html/fig_debug.html", "w", encoding="utf-8") as file:
            file.write(fig_html)
    except Exception as e:
        print(f"Error writing to file: {e}")


class AppDemo(QWidget):
    def __init__(self):
        """
        Constructor of AppDemo
        """
        super().__init__()
        self.setWindowTitle('Yahoo Async Runner')
        self.setGeometry(100, 100, 600, 400)
        self.plot_windows = []  # Keep track of plot windows

        cpath_root = os_calls.get_root_path()
        print(cpath_root)
        api_key_load = "Test key to load"
        docker_config = cpath_root + "/docker-compose.yml"
        config_path = cpath_root + "/config_loader/config.yml"
        ticker_file_path = cpath_root + "/src/server/listing_status.csv"
        # self.runner = Yahoorunner(api_key_load, docker_config, config_path, ticker_file_path)

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
        """
        @brief add filter row
        Returns:

        """
        filter_row = QHBoxLayout()
        filter_input = QLineEdit(self)
        filter_row.addWidget(filter_input)

        btn_add_filter = QPushButton('Add Filter', self)
        btn_add_filter.clicked.connect(self.add_filter_row)
        filter_row.addWidget(btn_add_filter)

        self.filter_layout.addLayout(filter_row)

    @asyncSlot()
    async def apply_filter(self):
        """
        @brief apply filter to the data
        Returns: None

        """
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
        """
        @brief Toggles the visibility of the table.

        Args:
            visible (bool):
                - True: Sets the table as visible.
                - False: Sets the table as not visible.

        Returns: None
        """
        self.table.setVisible(visible)
        logger.info(f"Table visibility set to {visible}")

    def add_filter_row(self):
        """
        @brief Add a filter to the table.
        Returns: None

        """
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
        """
        @brief Remove a filter from the table.
        Args:
            filter_row: the filter row to remove.

        Returns: None

        """
        for i in reversed(range(filter_row.count())):
            widget = filter_row.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.filter_layout.removeItem(filter_row)

    def get_filters(self):
        """
        @brief Get all the filters in the table.
        Returns: the filters list

        """
        filters = []
        for i in range(self.filter_layout.count()):
            filter_row = self.filter_layout.itemAt(i).layout()
            filter_dropdown = filter_row.itemAt(0).widget()
            filter_input = filter_row.itemAt(1).widget()
            filters.append((filter_dropdown.currentText(), filter_input.text()))
        return filters

    @asyncSlot()
    async def get_watched_list(self):
        """
        @brief Get all the tickers that are on the watched lists. And populate the table with the tickers

        Returns: None

        """
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
        """
        @brief Get all the tickers From the File. And populate the table with the tickers.

        Returns: None

        """
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
        """
        Get all the tickers From the DB. And populate the table with the tickers.

        Returns: None

        """
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
        """
        Get all the tickers From the Variable. And populate the table with the tickers.

        Returns: None

        """
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
        """
        @brief Populate the table with the tickers.
        Args:

            tickers_list (Pandas Series): List of tickers To populate table with Format
                (Pandas Series) See docs/ticker_list to see an example.


        Returns: None

        """
        self.output.append(f"Watched List: {tickers_list}")
        self.table.setRowCount(len(tickers_list))

        for row_index, row in tickers_list.iterrows():
            self.table.setItem(row_index, 0, create_read_only_item(row['symbol']))
            self.table.setItem(row_index, 1, create_read_only_item(row['name']))
            self.table.setItem(row_index, 2, create_read_only_item(row['exchange']))
            self.table.setItem(row_index, 3, create_read_only_item(row['assetType']))
            self.table.setItem(row_index, 4, create_read_only_item(str(row['ipoDate'])))
            self.table.setItem(row_index, 5, create_read_only_item(str(row['delistingDate'])))
            self.table.setItem(row_index, 6, create_read_only_item(row['status']))

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

    @asyncSlot()
    async def update_watching_status(self, row, index):
        """
        @brief Tell the server to update watch status in the database.
        Args:
            row: the ticker that is affected by the update.
            index: 1 add to watch list any other value remove from watch list.

        Returns: None

        """
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
        """
        @brief Tell the server to update watch list in the database.
        Returns: None

        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, requests.post, 'http://127.0.0.1:8000/api/update_watch_list/',
                                   {'tickers': "A"})
        logger.info("Watch list updated")

    @asyncSlot()
    async def update_ticker_list(self):
        """
        @brief Tell the server to update ticker list in the file
        Returns: None

        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, requests.post, 'http://127.0.0.1:8000/api/update_ticker_list/')
        self.output.append("Ticker list updated.")

    @asyncSlot()
    async def store_ticker_list(self):
        """
        @brief Tell the server to store ticker list (file) in the database.
        Returns:
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, requests.post, 'http://127.0.0.1:8000/api/store_ticker_list/',
                                   {'tickers': "A"})
        self.output.append("Ticker list stored.")

    # todo rewrtite all functions to use a api_call handler instead
    async def api_call(self, endpoint, payload, expect_html=False):
        """
        Handles API calls.

        Args:
            endpoint (str): Defines which endpoint to be called.
            payload (dict): Defines the payload to be sent.
            expect_html (bool): Indicates if the return value is expected to be HTML.

        Returns:
            Response: A valid response object if successful.
            None: If the API call fails.

        The return type can be either a Series or HTML, depending on the requested format.
        The format is determined by the API endpoint called.
        """
        url = f'http://127.0.0.1:8000/{endpoint}'

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: requests.post(url, json=payload))

        if response.status_code == 200:
            if expect_html:
                # Print the raw response content for debugging
                logger.info("Raw HTML response content:", response.content)
                logger.info("Decoded HTML response content:", response.text)
            else:
                # Print the raw JSON response for debugging
                logger.info("Raw JSON response content:", response.content)
            return response
        else:
            logger.error(f"Error: Received status code {response.status_code}")
            return None

    @asyncSlot()
    async def visualize_row(self, row):
        """
        Instructs the server to send and plot the data in an HTML visualization.

        Args:
            row (Series): The row of data to be plotted.

        Returns:
            None
        """
        logger.info("Visualization Started")

        # Convert Series to dictionary and serialize using TickerSerializer
        payload = {'tickers': row.to_dict()}

        logger.info("Serialized JSON:")
        logger.info(json.dumps(payload))

        # Asynchronous call to load_data API
        all_data_bytes = await self.api_call('api/load_data/', payload)

        # Decode byte strings and parse JSON data
        json_str = ''.join([data.decode('utf-8') for data in all_data_bytes])
        all_data = pd.DataFrame(json.loads(json_str))

        if all_data.empty:
            logger.info("No data returned")
            return

        # Asynchronous call to plot_graph API
        fig_html_response = await self.api_call(
            'api/plot_graph/',
            {'all_data': all_data.to_dict(orient='records'), 'chunk_size': 10}
        )

        if fig_html_response.status_code != 200:
            logger.error(f"Error: Received status code {fig_html_response.status_code}")
            return

        fig_html = html.unescape(fig_html_response.text)

        # Debug HTML content (optional)
        store_html(fig_html)

        # Check if Qt rendering has previously failed
        if has_render_failed():
            open_in_browser(fig_html, row["symbol"])
            return

        # Initialize Qt application if not already running
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        plot_window = PlotWindow(fig_html, row["symbol"])
        plot_window.show()
        self.plot_windows.append(plot_window)  # Keep a reference

        if not has_render_failed():
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
