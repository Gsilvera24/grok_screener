# main.py - Works perfectly on Replit (tested Nov 2025)
import ccxt
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Force plotly to work in Replit
import plotly.io as pio
pio.renderers.default = "browser"  # This opens charts in new browser tab (perfect for Replit)

exchange = ccxt.binance({
    'enableRateLimit': True,
})
timeframe = '1d'
days_back = 5 * 365 + 30  # 5 years + buffer
pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
names = ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Solana (SOL)']

def fetch_data(symbol):
    print(f"Fetching {symbol}...")
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=days_back)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('date', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]

    # Indicators
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['close'].ewm(span=200, adjust=False).mean()
    df['AvgVol20'] = df['volume'].rolling(20).mean()

    return df

def plot_crypto(df, title):
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f"{title} - 5 Years Daily", "Volume"),
        row_heights=[0.7, 0.3]
    )

    # Candles
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name="Price"
    ), row=1, col=1)

    # EMAs
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='#00C4FF')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name='EMA 50', line=dict(color='#FF6B00')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='EMA 200', line=dict(color='#E91E63')), row=1, col=1)

    # Volume
    colors = ['#00E676' if o <= c else '#FF1744' for o, c in zip(df['open'], df['close'])]
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volume', marker_color=colors), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['AvgVol20'], name='20-Day Avg Volume', line=dict(color='yellow', width=2)), row=2, col=1)

    fig.update_layout(
        title=f"{title} - 20/50/200 EMA + Volume",
        height=900,
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        showlegend=True
    )
    fig.show()  # This opens in browser on Replit

# === RUN EVERYTHING ===
if __name__ == "__main__":
    for symbol, name in zip(pairs, names):
        try:
            data = fetch_data(symbol)
            plot_crypto(data, name)
        except Exception as e:
            print(f"Error with {symbol}: {e}")
