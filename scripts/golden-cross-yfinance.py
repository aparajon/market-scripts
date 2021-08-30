import yfinance as yf
import numpy as np
import hvplot
import hvplot.pandas  # noqa

# Source code inspiration: https://medium.com/analytics-vidhya/trading-dashboard-with-yfinance-python-56fa471f881d

# Parameters
STOCK_SYMBOL = "AMC"
SHORT_WINDOW = 50
LONG_WINDOW = 100

stock_ticker = yf.Ticker(STOCK_SYMBOL)
stock_history = stock_ticker.history(start="2019-09-01", end="2021-08-29", interval="1d")
signals_df = stock_history.drop(columns=['Open', 'High', 'Low', 'Volume','Dividends', 'Stock Splits'])

short_window_column = f"SMA{SHORT_WINDOW}"
long_window_column = f"SMA{LONG_WINDOW}"

signals_df[short_window_column] = signals_df['Close'].rolling(window=SHORT_WINDOW).mean()
signals_df[long_window_column] = signals_df['Close'].rolling(window=LONG_WINDOW).mean()
signals_df['Signal'] = 0.0

# Generate the trading signal 0 or 1,
# where 0 is when the short window is under the longer window, and
# where 1 is when the short window is higher (or crosses over) the long window

signals_df['Signal'][SHORT_WINDOW:] = np.where(
    signals_df[short_window_column][SHORT_WINDOW:] > signals_df[long_window_column][SHORT_WINDOW:], 
    1.0, 
    0.0
) 

'''
Explanation of above:

The condition of np.where(signals_df[short_window_column][SHORT_WINDOW:] > signals_df[long_window_column][SHORT_WINDOW:])
gives the rows indices where short window is greater than the long window. Output is for example:

(array([ 49,  50,  51,  52,  53,  54,  55,  56,  57,  58,  59,  60,  61,
        62,  63,  64,  65,  66,  67,  68,  69,  70,  71,  72,  73,  74,
        75,  76,  77,  78,  79,  80,  81,  82,  83,  84,  85,  86,  87,
        88,  89,  90,  91,  92,  93,  94,  95,  96,  97,  98,  99, 100,
       101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113,
       114]),)

The index range "SHORT_WINDOW:" means every row after SHORT_WINDOW. If SHORT_WINDOW = 50, this means all rows after the 50th element (inclusive) to the end.
All the rows before element 50 remain 0, whereas the rows after will be set according to whether they match the condition (see below). This is because
the SMA is does not have enough data before the short window and is treated as a "NaN" value. In other words, when calculating the M days SMA, 
the first M-1 days  are not valid, as M prices are required for the first moving average data point. 
Source: https://www.learndatasci.com/tutorials/python-finance-part-3-moving-average-trading-strategy/

Adding 1.0 (x= param) and 0.0 (y = param) at the end of np.where results in:

[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.
 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.
 0. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.
 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.
 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.]

Including the x and y param results in a full size array, where as omitting only returns the array with the indices that match the condition.
The x parameter means (set to 1.0) means replace all indices where the condition is met with a 1.0. The y parameter (set to 0.0) means replace all indices
where the condition is not matched. 
Source: https://note.nkmk.me/en/python-numpy-where/#:~:text=numpy.where(condition%5B%2C%20x%2C%20y%5D)&text=v1.14%20Manual-,np.,are%20omitted%2C%20index%20is%20returned.
'''


# e.g. when the SMA50 crosses above the SMA100 or resistance level, this is a bullish breakout signal

# Calculate the points in time at which a position should be taken, 1 or -1
signals_df['Entry/Exit'] = signals_df['Signal'].diff()

# Uncomment below line to print the DataFrame
# signals_df.tail(10) # last 10 dates

# Visualize exit position relative to close price
exit = signals_df[signals_df['Entry/Exit'] == -1.0]['Close'].hvplot.scatter(
    color='red',
    legend=False,
    ylabel='Price in $',
    width=1000,
    height=400
)
# Visualize entry position relative to close price
entry = signals_df[signals_df['Entry/Exit'] == 1.0]['Close'].hvplot.scatter(
    color='green',
    legend=False,
    ylabel='Price in $',
    width=1000,
    height=400
)
# Visualize close price for the investment
security_close = signals_df[['Close']].hvplot(
    line_color='lightgray',
    ylabel='Price in $',
    width=1000,
    height=400
)
# Visualize moving averages
moving_avgs = signals_df[[short_window_column, long_window_column]].hvplot(
    ylabel='Price in $',
    width=1000,
    height=400
)
# Overlay plots
entry_exit_plot = security_close * moving_avgs * entry * exit

hvplot.show(entry_exit_plot)
