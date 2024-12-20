import os
import sys
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QTableWidgetItem, QTableWidget, \
    QComboBox, QLineEdit, QHBoxLayout, QProgressBar, QDialog, QMenu, QMenuBar
from src.logging.logging_config import logger
from src.server.yahoo.Yahoorunner import Yahoorunner
from ui.PlotWindow import PlotWindow


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


def create_read_only_item(text):
    item = QTableWidgetItem(text)
    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
    return item


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.render_thread = None
        self.progress_dialog = None
        self.setWindowTitle('Yahoo Runner')
        self.setGeometry(100, 100, 600, 400)
        self.plot_windows = []  # Keep track of plot windows

        cpath_root = os.path.abspath("../")
        api_key_load = "Test key to load"
        docker_config = cpath_root + "/docker-compose.yml"
        config_path = cpath_root + "/config_loader/config.yml"
        ticker_file_path = cpath_root + "/src/server/listing_status.csv"
        self.runner = Yahoorunner(api_key_load, docker_config, config_path, ticker_file_path)

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

    def apply_filter(self):
        # Your implementation to apply the filter
        pass

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

    def get_watched_list(self):
        self.render_list(True)

    def visualize_row(self, row):
        all_data = self.runner.load_data(row)
        fig, config = self.runner.plot_graph(all_data, chunk_size=1000)
        if fig is None:
            logger.info("No data to plot.")
            logger.debug(fig, config)
            return

        app_instance = QApplication.instance()
        if not app_instance:
            app_instance = QApplication(sys.argv)

        plot_window = PlotWindow(fig, config)
        plot_window.show()
        self.plot_windows.append(plot_window)  # Keep a reference

        if not QApplication.instance():
            app_instance.exec()

    def populate_table(self, tickers_list):
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

            # Add Visualize button
            btn_visualize = QPushButton('Visualize', self)
            btn_visualize.clicked.connect(lambda _, row=row: self.visualize_row(row))
            self.table.setCellWidget(row_index, 8, btn_visualize)

        if not tickers_list.empty:
            self.toggle_table_visibility(True)
            self.show()  # Ensure the window is shown

        self.progress_dialog.close()

    def render_list(self, watcher=True):
        filters = self.get_filters()

        self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.show()

        self.render_thread = RenderThread(self.runner, filters, watcher)
        self.render_thread.update_progress.connect(self.progress_dialog.set_progress)
        self.render_thread.render_complete.connect(self.populate_table)
        self.render_thread.start()

    def update_watching_status(self, row, index):
        if index == 1:
            self.runner.add_to_watch_list(row["symbol"])
            new_status = 0
        else:
            self.runner.remove_from_watch_list(row["symbol"])
            new_status = 1

        row['watching'] = new_status
        logger.info(f"Updated row {row['symbol']} watching status to {new_status}")

    def update_watch_list(self):
        logger.info("todo")
        self.runner.update_watch_list("A")

    def update_ticker_list(self):
        self.runner.update_ticker_list()
        self.output.append("Ticker list updated.")

    def store_ticker_list(self):
        self.runner.store_ticker_list("A")
        self.output.append("Ticker list stored.")

    def get_all_tickers_file(self):
        self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.show()

        self.render_thread = RenderThread(self.runner, self.get_filters(), False, True)
        self.render_thread.update_progress.connect(self.progress_dialog.set_progress)
        self.render_thread.render_complete.connect(self.populate_table)
        self.render_thread.start()

    def get_all_tickers_variable(self):
        self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.show()

        self.render_thread = RenderThread(self.runner, self.get_filters(), False, False)
        self.render_thread.update_progress.connect(self.progress_dialog.set_progress)
        self.render_thread.render_complete.connect(self.populate_table)
        self.render_thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec())
