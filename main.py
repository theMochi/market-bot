import os
import schedule
import time
import requests
from keep_alive import keep_alive

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SP500_SYMBOLS = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA', 'BRK.B', 'JPM', 'JNJ', 'V', 'PG', 'XOM', 'UNH', 'MA', 'HD', 'CVX', 'ABBV', 'LLY', 'PEP', 'KO', 'MRK', 'AVGO', 'BAC', 'TMO', 'DIS', 'PFE', 'CSCO', 'ADBE', 'WMT', 'CRM', 'CMCSA', 'ABT', 'MCD', 'NFLX', 'ACN', 'DHR', 'NKE', 'INTC', 'COST', 'VZ', 'TXN', 'NEE', 'LIN', 'BMY', 'MDT', 'UNP', 'HON', 'AMGN', 'LOW', 'QCOM', 'BA', 'UPS', 'PM', 'AMAT', 'SBUX', 'ISRG', 'RTX', 'IBM', 'INTU', 'CAT', 'GE', 'LMT', 'MDLZ', 'GILD', 'NOW', 'SPGI', 'CVS', 'EL', 'BLK', 'DE', 'SYK', 'ADI', 'CI', 'VRTX', 'TGT', 'ZTS', 'MO', 'TFC', 'MU', 'BDX', 'SCHW', 'ADP', 'MMC', 'TJX', 'PNC', 'BKNG', 'CL', 'CB', 'C', 'REGN', 'GM', 'ICE', 'FDX', 'HCA', 'APD', 'SO', 'PLD', 'DUK', 'AON', 'NSC', 'SHW', 'ITW', 'BSX', 'D', 'EW', 'FISV', 'PSA', 'SLB', 'EMR', 'PGR', 'EOG', 'MCK', 'WM', 'ETN', 'GD', 'MNST', 'AZO', 'AIG', 'AEP', 'CSX', 'ADI', 'ORLY', 'MCO', 'IDXX', 'ADSK', 'ROST', 'TRV', 'CDNS', 'FTNT', 'MS', 'KHC', 'COF', 'DXCM', 'SRE', 'ATVI', 'AFL', 'CTSH', 'ILMN', 'KLAC', 'WBA', 'ROK', 'A', 'PCAR', 'WELL', 'OTIS', 'MAR', 'HSY', 'DLR', 'WMB', 'EA', 'ANSS', 'PH', 'CHTR', 'BIIB', 'VRSK', 'CTAS', 'HUM', 'XEL', 'MTD', 'F', 'ECL', 'CMG', 'DOW', 'HAL', 'WST', 'PRU', 'CNC', 'PAYX', 'KEYS', 'NOC', 'PPL', 'PEG', 'LHX', 'ALL', 'XYL', 'RMD', 'HIG', 'SBAC', 'STZ', 'EFX', 'AVB', 'BKR', 'DLTR', 'TSCO', 'AMP', 'NUE', 'HPQ', 'FRC', 'APA', 'ALB', 'LEN', 'GPN', 'ZBRA', 'VLO', 'CF', 'CAG', 'MTB', 'INCY', 'GLW', 'MLM', 'STT', 'EXR', 'FAST', 'BAX', 'TEL', 'PKI', 'TSN', 'EXPD', 'CNP', 'FMC', 'TTWO', 'VTRS', 'NDAQ', 'NTRS', 'CAH', 'CINF', 'AES', 'AKAM', 'IFF', 'SWKS', 'VFC', 'MOS', 'HOLX', 'IRM', 'WRB', 'MKTX', 'KEY', 'NTAP', 'FLT', 'ZION', 'L', 'WRK', 'PTC', 'NRG', 'HPE', 'DXC', 'TECH', 'BEN', 'UHS', 'AIZ', 'TAP', 'NWL', 'BBWI', 'KIM', 'RCL', 'GNRC', 'BXP', 'MAS', 'NWS', 'AAL', 'ALK', 'HAS', 'DVA', 'FRT', 'LNC', 'ROL', 'ALLE', 'BIO', 'LW', 'TPR', 'FOX', 'FOXA', 'CPB', 'PNW', 'SEE', 'APA', 'NWSA', 'XRAY', 'PVH', 'HBAN', 'DXC', 'CMA', 'RHI', 'WHR', 'IPG', 'IVZ', 'NRG', 'OGN', 'JBHT', 'CHRW', 'NI', 'PARA', 'K', 'REG', 'AOS', 'PBCT', 'MHK', 'RE', 'RL']


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def send_market_open_message():
    send_telegram_message("🟢 Market Open!")
    send_sp500_top_movers()

def send_market_close_message():
    send_telegram_message("🔴 Market Close!")
    send_sp500_top_movers()

def get_batch_stock_data(symbols):
    stock_data = []
    batch_size = 100
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        url = f"https://financialmodelingprep.com/api/v3/quote/{','.join(batch)}?apikey=demo"
        response = requests.get(url)
        if response.status_code == 200:
            stock_data.extend(response.json())
    return stock_data

def get_top_movers(stock_data):
    for stock in stock_data:
        previous_close = stock.get('previousClose')
        price = stock.get('price')
        if previous_close and price:
            change_percent = ((price - previous_close) / previous_close) * 100
            stock['changePercent'] = change_percent
        else:
            stock['changePercent'] = 0

    sorted_data = sorted(stock_data, key=lambda x: x['changePercent'], reverse=True)
    top_gainers = sorted_data[:5]
    top_losers = sorted_data[-5:]
    return top_gainers, top_losers

def format_movers_message(title, movers, emoji):
    message = f"{emoji} {title}\n"
    for stock in movers:
        symbol = stock.get('symbol')
        name = stock.get('name', 'N/A')
        change_percent = stock.get('changePercent', 0)
        message += f"{symbol} ({name}): {change_percent:.2f}%\n"
    return message

def send_sp500_top_movers():
    stock_data = get_batch_stock_data(SP500_SYMBOLS)
    if not stock_data:
        send_telegram_message("⚠️ Failed to load stock data.")
        return

    gainers, losers = get_top_movers(stock_data)
    gainers_message = format_movers_message("Top 5 Gainers", gainers, "📈")
    losers_message = format_movers_message("Top 5 Losers", losers, "📉")

    send_telegram_message(gainers_message)
    send_telegram_message(losers_message)

schedule.every().monday.at("17:30").do(send_market_open_message)
schedule.every().tuesday.at("17:30").do(send_market_open_message)
schedule.every().wednesday.at("17:30").do(send_market_open_message)
schedule.every().thursday.at("17:30").do(send_market_open_message)
schedule.every().friday.at("17:30").do(send_market_open_message)

schedule.every().monday.at("00:00").do(send_market_close_message)
schedule.every().tuesday.at("00:00").do(send_market_close_message)
schedule.every().wednesday.at("00:00").do(send_market_close_message)
schedule.every().thursday.at("00:00").do(send_market_close_message)
schedule.every().friday.at("00:00").do(send_market_close_message)

keep_alive()

while True:
    schedule.run_pending()
    time.sleep(30)
