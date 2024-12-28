import concurrent
import html
import json
import multiprocessing
import re
import sys
import asyncio
import threading

import pandas
import requests
import pandas as pd
import websockets
from PyQt6.QtWebSockets import QWebSocket
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QPushButton, QHBoxLayout, QLineEdit, QMenuBar, QMenu, QAbstractItemView, QLabel
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QUrl, QTimer
from qasync import QEventLoop, asyncSlot, QtGui
from src.logging.logging_config import logger
import src.os_calls.basic_os_calls as os_calls
from src.ui.PlotWindow import PlotWindow, has_render_failed, open_in_browser


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
        with open("../../tmp_data/tmp_html/fig_debug.html", "w", encoding="utf-8") as file:
            file.write(fig_html)
    except Exception as e:
        print(f"Error writing to file: {e}")


def start_websocket_client(main_window):
    app = QApplication([])
    client = WebSocketClient()
    client.message_received.connect(main_window.on_message_received)
    app.exec()


class WebSocketClient(QObject):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.websocket = QWebSocket()
        self.websocket.connected.connect(self.on_connected)
        self.websocket.disconnected.connect(self.on_disconnected)
        self.websocket.error.connect(self.on_error)
        self.websocket.textMessageReceived.connect(self.on_message_received)
        self.open_connection()

    def open_connection(self):
        self.websocket.open(QUrl('ws://172.20.0.3:8000/ws/message/'))

    def on_connected(self):
        logger.info("WebSocket connected")

    def on_disconnected(self):
        logger.info("WebSocket disconnected")
        self.reconnect()

    def on_error(self, error):
        logger.error(f"WebSocket Error: {error}")
        self.reconnect()

    def on_message_received(self, message):
        data = json.loads(message)
        logger.info("Message received:", data)
        self.message_received.emit(json.dumps(data))

    def reconnect(self):
        QTimer.singleShot(5000, self.open_connection)  # Reconnect after 5 seconds


class AppDemo(QWidget):
    def __init__(self):
        """
        Constructor of AppDemo
        """
        super().__init__()

        # ui start
        self.setWindowTitle('Yahoo Async Runner')
        screen = QApplication.primaryScreen()
        size = screen.size()
        self.setGeometry(0, 0, size.width(), size.height())
        self.plot_windows = []  # Keep track of plot windows

        # Find the absolute Path of Files
        cpath_root = os_calls.get_root_path()
        print(cpath_root)
        api_key_load = "Test key to load"
        docker_config = cpath_root + "/docker-compose.yml"
        config_path = cpath_root + "/config_loader/config.yml"
        ticker_file_path = cpath_root + "/src/server/listing_status.csv"

        # gernerate Layout for qt
        layout = QVBoxLayout()

        # Add table widget to layout
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.table = QTableWidget(self)
        # self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Symbol", "Name", "Exchange", "Asset Type", "IPO Date", "Delisting Date", "Status", "Watching", "Visualize"
        ])
        layout.addWidget(self.table)
        # Initially hide the table (will only be shwon once data to show")
        self.table.setVisible(False)

        # Find the mapping for the fields
        tmp_df = pandas.read_csv(ticker_file_path)
        # Filter object
        self.column_names = tmp_df.columns
        # Create a mapping from column names to indices
        self.column_mapping = {name: index for index, name in enumerate(self.column_names)}

        # Add filter section layout
        self.filter_layout = QVBoxLayout()
        layout.addLayout(self.filter_layout)

        # Add Apply button to layout
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

        # Add menus to ui layout
        layout.setMenuBar(menu_bar)
        # Set the defined layout as layout for Window
        self.setLayout(layout)

        # setup Socket Client
        self.websocket_client = WebSocketClient()
        self.websocket_client.message_received.connect(self.on_message_received)

        # add table state to check what window user is in
        self.table_state = None

    def on_message_received(self, message):
        try:
            # Parse the JSON string into a Python dictionary
            data = json.loads(message)

            # Log the received message
            logger.info(f"UI received message: {data}")

            if data["type"] == "send_event_update":
                if not data['event_data']:
                    return
                event_data = data['event_data']
                # affected_data = data['affected_data']
                if event_data['event_type'] == 'ticker_update':
                    log_out_event = json.dumps(event_data)

                    self.output.append(f"Event: {log_out_event}")
                    if self.table_state is None:
                        return
                    elif self.table_state == "Watch_List":
                        self.get_watched_list()
                    elif self.table_state == "all_tickers_file":
                        print("all_tickers_file")
                        #self.get_all_tickers_file()
                    elif self.table_state == "all_tickers_variable":
                        print("all_tickers_variable")
                        #self.get_all_tickers_variable()
                    elif self.table_state == "all_tickers_db":
                        print("all_tickers_db")
                        #self.get_all_tickers_db()

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON message: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

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

    @asyncSlot()
    async def get_watched_list(self):
        """
        @brief Get all the tickers that are on the watched lists. And populate the table with the tickers

        Returns: None

        """
        self.table_state = "Watch_List"
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
        self.table_state = "all_tickers_file"
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
        self.table_state = "all_tickers_db"
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
        self.table_state = "all_tickers_variable"
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
            watching_combobox.setObjectName("watching_combobox")
            watching_combobox.currentIndexChanged.connect(
                lambda index, row=row: self.update_watching_status(row, index))
            self.table.setCellWidget(row_index, 7, watching_combobox)

            btn_visualize = QPushButton('Visualize', self)
            btn_visualize.clicked.connect(lambda _, row=row: self.visualize_row(row))
            self.table.setCellWidget(row_index, 8, btn_visualize)

        if not tickers_list.empty:
            self.toggle_table_visibility(True)
            self.show()

    def get_row_data(self, table, row_index):
        return [table.item(row_index, col).text() if table.item(row_index, col) is not None else ''
                for col in range(table.columnCount())]

    def filter_row(self, row_data, filters):
        if not filters:
            return True  # No filters, show the row

        result = None  # Initial result is undefined

        # Debug print to show the current row data being checked
        print(f"Checking row data: {row_data}")
        print(f"column_mapping {self.column_mapping}")

        for criterion, value, condition in filters:
            if not value:  # Skip empty filter values
                continue

            if criterion == "Watching Status":
                for row_index in range(self.table.rowCount()):
                    cell_widget = self.table.cellWidget(row_index, 7)
                    print(cell_widget.objectName() + "object name")
                    if isinstance(cell_widget, QComboBox) and cell_widget.objectName() == f"watching_combobox":
                        watching_status = cell_widget.currentText()
                        match = bool(watching_status == value)

            else:
                col_index = self.column_mapping.get(criterion)
                if col_index is not None:
                    pattern = re.compile(re.escape(value), re.IGNORECASE)
                    match = bool(pattern.search(row_data[col_index]))
                else:
                    match = False  # No match if the column is not found

            # Debug print to show the filter being applied and the result
            print(f"Applying filter: {criterion} {condition} {value}, Match: {match}")

            if result is None:
                result = match  # First filter result
            elif condition == "AND":
                result = result and match
            elif condition == "OR":
                result = result or match

        # Debug print to show the final result for this row
        print(f"Result for row: {result}")

        return result

    def apply_filter(self):
        """
        @brief Apply filter to the data within the table.
        Returns: None
        """
        filters = self.get_filters()

        # Make all rows visible initially
        for row_index in range(self.table.rowCount()):
            self.table.setRowHidden(row_index, False)

        # Check if there are any filters
        if not any(value for _, value, _ in filters):
            return

        self.parallel_filter_table(self.table, filters)

    def parallel_filter_table(self, table, filters):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for row_index in range(table.rowCount()):
                row_data = self.get_row_data(table, row_index)
                # erow_watch_status = self.get_watched_list()
                futures.append(executor.submit(self.filter_row, row_data, filters))

            # Make all rows visible initially
            for row_index in range(table.rowCount()):
                table.setRowHidden(row_index, False)

            # Hide rows that don't match the filter criteria
            for row_index, future in enumerate(futures):
                table.setRowHidden(row_index, not future.result())

    def apply_filter(self):
        """
        @brief Apply filter to the data within the table.
        Returns: None
        """
        filters = self.get_filters()
        if filters:
            self.parallel_filter_table(self.table, filters)

    def get_filters(self):
        filters = []
        for i in range(self.filter_layout.count()):
            filter_row = self.filter_layout.itemAt(i).layout()
            filter_dropdown = filter_row.itemAt(0).widget()
            filter_input_container = filter_row.itemAt(1).layout()
            and_or_dropdown = filter_row.itemAt(2).widget()

            filter_input_widget = filter_input_container.itemAt(0).widget()
            if isinstance(filter_input_widget, QLineEdit):
                filter_value = filter_input_widget.text()
            elif isinstance(filter_input_widget, QComboBox):
                filter_value = filter_input_widget.currentText()

            filters.append((filter_dropdown.currentText(), filter_value, and_or_dropdown.currentText()))
        return filters

    def add_filter_row(self):
        """
        @brief Add a filter to the table.
        Returns: None
        """
        filter_row = QHBoxLayout()

        filter_dropdown = QComboBox(self)
        filter_dropdown.addItems(
            list(self.column_mapping.keys()) + ["Watching Status"])  # Add "Watching Status" to the options
        filter_row.addWidget(filter_dropdown)

        # Container for filter input or dropdown based on the selected criterion
        filter_input_container = QHBoxLayout()
        filter_row.addLayout(filter_input_container)

        # Dropdown for AND/OR condition
        and_or_dropdown = QComboBox(self)
        and_or_dropdown.addItems(["AND", "OR"])
        filter_row.addWidget(and_or_dropdown)

        btn_remove_filter = QPushButton('Remove', self)
        btn_remove_filter.clicked.connect(lambda: self.remove_filter_row(filter_row))
        filter_row.addWidget(btn_remove_filter)

        self.filter_layout.addLayout(filter_row)

        # Function to update the filter input based on the selected criterion
        def update_filter_input():
            # Remove existing widgets
            for i in reversed(range(filter_input_container.count())):
                widget = filter_input_container.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)

            if filter_dropdown.currentText() == "Watching Status":
                status_dropdown = QComboBox(self)
                status_dropdown.addItems(["True", "False"])
                filter_input_container.addWidget(status_dropdown)
            else:
                filter_input = QLineEdit(self)
                filter_input.setPlaceholderText("Enter filter value")
                filter_input_container.addWidget(filter_input)

        # Connect the update function to the filter dropdown selection change
        filter_dropdown.currentIndexChanged.connect(update_filter_input)

        # Initialize the input field based on the initial selection
        update_filter_input()

    def remove_widgets_recursively(self, layout):
        """
        Recursively remove all widgets from the given layout.
        Args:
            layout: The QLayout instance to clear.
        """
        while layout.count():
            item = layout.takeAt(0)
            if isinstance(item, QHBoxLayout) or isinstance(item, QVBoxLayout):
                self.remove_widgets_recursively(item)
            elif item.widget():
                widget = item.widget()
                widget.deleteLater()

    def remove_filter_row(self, filter_row):
        """
        @brief Remove a filter from the table.
        Args:
            filter_row: the filter row to remove.

        Returns: None
        """
        # Remove all nested widgets from the filter row using the recursive function
        self.remove_widgets_recursively(filter_row)

        self.filter_layout.removeItem(filter_row)

        # Unhide all rows before reapplying filters
        for row_index in range(self.table.rowCount()):
            self.table.setRowHidden(row_index, False)

        # Reapply the filters
        self.apply_filter()


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
