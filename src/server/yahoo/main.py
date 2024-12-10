import os
import sys
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.server.yahoo.dataProcesing import DataProcessor

if __name__ == '__main__':

    ticker = 'AAPL'
    processor = DataProcessor(ticker)
    processor.process_data()
    processor.plot_data()
