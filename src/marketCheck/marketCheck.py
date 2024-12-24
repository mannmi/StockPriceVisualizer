#Stock Market Data: For real-time stock market data, it’s best to fetch data during market hours. For the U.S. stock market, this is typically from 9:30 AM to 4:00 PM Eastern Time (ET). Adjust this based on your local time zone.
#Historical Data: If you’re fetching historical data, you can do this at any time since the data is static and not affected by market hours.
#News and Updates: For the latest financial news and updates, it’s good to check during market hours or just before the market opens, as significant news often breaks around these times.
import pytz
from datetime import datetime


class Markettimechecker:

    def __init__(self, local_tz='Asia/Seoul', market_tz='America/New_York'):

        self.local_tz = pytz.timezone(local_tz)
        self.market_tz = pytz.timezone(market_tz)

    def get_current_time(self):
        """
        get the curent time for the curently set time zone. The time zone is curently set to Soul Asia
        #todo implment beter locaisation
        :return: localized time
        """
        return datetime.now(self.local_tz)

    def convert_to_market_time(self, local_time):
        """
        yahoo is based in the usa the stock prices will be based on the us market
        :param local_time: provide your curent time (curently set in Seoul time)
        :return: the yahooo time zone based time stamp
        """
        return local_time.astimezone(self.market_tz)

    def is_market_open(self):
        """
        check if market is up. Historical Data schould not be fetched if its up
        :return:
        """
        now_local = self.get_current_time()
        now_market = self.convert_to_market_time(now_local)

        market_open = now_market.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_market.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= now_market <= market_close
