import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from googletrans import Translator

translator = Translator()

st.set_page_config(page_title="AI Beginner Stock Mentor", layout="wide")

# ---------- UI STYLE ----------

st.markdown("""
<style>

.main-title{
font-size:42px;
font-weight:bold;
color:white;
text-align:center;
}

.header-box{
background: linear-gradient(90deg,#1E90FF,#00C9A7);
padding:20px;
border-radius:12px;
margin-bottom:20px;
}

.card{
background:white;
padding:15px;
border-radius:10px;
box-shadow:0px 4px 10px rgba(0,0,0,0.1);
margin-bottom:15px;
}

.explain-box{
background:#F4F6F7;
border-left:6px solid #1E90FF;
padding:15px;
border-radius:8px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
<div class="main-title">📊 AI Beginner Stock Mentor</div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------

menu = st.sidebar.selectbox(
"Select Option",
["Stock Analysis","Practice Trading"]
)

language = st.sidebar.selectbox(
"Language",
["English","Hindi","Telugu"]
)

# ---------- TRANSLATION ----------

def translate_text(text):

    if language == "English":
        return text

    if language == "Hindi":
        return translator.translate(text,dest="hi").text

    if language == "Telugu":
        return translator.translate(text,dest="te").text

# ---------- TRADE EXPLANATION ----------

def smart_trade_explanation(profit,investment,balance):

    if profit < 0:

        text = """
You are currently facing a loss because the price of the stock
became lower than the price at which you bought it.

This usually happens when more people start selling the stock
than buying it.

Suggestion for beginners:
Try not to panic when prices drop. Always study the stock and
invest in multiple companies instead of putting all your money
in one stock.
"""

    elif profit > 0:

        text = """
You are currently making a profit because the stock price
became higher than the price you bought it for.

This usually happens when more investors are buying the stock,
which increases demand and pushes the price upward.

Suggestion for beginners:
Even when you make profit, do not invest all your money in
one company. Diversifying your investment helps reduce risk.
"""

    else:

        text = "The stock price has not changed since you bought it."

    return translate_text(text)

# ---------- STOCK ANALYSIS ----------

if menu == "Stock Analysis":

    stock = st.text_input("Enter Stock Symbol","AAPL")

    if st.button("Analyze Stock"):

        data = yf.download(stock,period="6mo")

        if data.empty:
            st.error("Invalid stock symbol")
            st.stop()

        current_price = float(data["Close"].iloc[-1])

        data["MA20"] = data["Close"].rolling(20).mean()
        data["MA50"] = data["Close"].rolling(50).mean()

        ma20_last = float(data["MA20"].iloc[-1])
        ma50_last = float(data["MA50"].iloc[-1])

        trend = "Bullish" if ma20_last > ma50_last else "Bearish"

        volatility = float(data["Close"].pct_change().std())

        if volatility > 0.03:
            risk="High Risk"
        elif volatility >0.015:
            risk="Medium Risk"
        else:
            risk="Low Risk"

        recommendation = "BUY" if trend=="Bullish" else "SELL"

        confidence = max(0,round((1-volatility)*100))

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("💰 Price",round(current_price,2))
        col2.metric("📈 Trend",trend)
        col3.metric("⚠ Risk",risk)
        col4.metric("🤖 Confidence",f"{confidence}%")

        # ----- CANDLESTICK CHART -----

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Price"
        ))

        fig.add_trace(go.Scatter(
        x=data.index,
        y=data["MA20"],
        line=dict(color="blue"),
        name="MA20"
        ))

        fig.add_trace(go.Scatter(
        x=data.index,
        y=data["MA50"],
        line=dict(color="orange"),
        name="MA50"
        ))

        fig.add_annotation(
        x=data.index[-1],
        y=current_price,
        text=recommendation,
        showarrow=True,
        arrowhead=2,
        font=dict(size=16,color="green" if recommendation=="BUY" else "red")
        )

        fig.update_layout(
        title="Stock Price Chart",
        height=500
        )

        st.plotly_chart(fig,use_container_width=True)

        # ----- RSI -----

        delta = data["Close"].diff()

        gain = (delta.where(delta>0,0)).rolling(14).mean()
        loss = (-delta.where(delta<0,0)).rolling(14).mean()

        rs = gain/loss

        data["RSI"] = 100 - (100/(1+rs))

        st.subheader("RSI Indicator")

        st.line_chart(data["RSI"])

        # ----- VOLUME -----

        st.subheader("Volume Analysis")

        st.bar_chart(data["Volume"])

        # ----- SIMPLE EXPLANATION -----

        if trend == "Bullish":

            explanation = """
The system looked at how this stock price has been moving recently.

Right now the price has been increasing slowly and steadily.
This usually means more people are buying the stock.

When more investors buy a stock, the demand increases
and the price usually moves upward.

Because of this positive movement, the system suggests
that this stock currently looks like a buying opportunity.

However beginners should never invest all their money
in one stock. It is always safer to divide your money
between multiple companies.
"""

        else:

            explanation = """
The system analyzed the recent movement of this stock.

Currently the price has been moving downward or showing
weaker growth. This usually means more investors are selling
the stock rather than buying it.

When selling pressure increases, prices tend to fall.

Because of this weaker movement, the system suggests
waiting before buying this stock.

Beginners should wait until the stock shows a stable
or upward movement before investing.
"""

        st.markdown('<div class="card">',unsafe_allow_html=True)

        st.subheader("🧠 Simple Explanation")

        st.markdown('<div class="explain-box">',unsafe_allow_html=True)

        st.write(translate_text(explanation))

        st.markdown('</div>',unsafe_allow_html=True)

        st.markdown('</div>',unsafe_allow_html=True)

# ---------- PRACTICE TRADING ----------

if menu=="Practice Trading":

    if "balance" not in st.session_state:
        st.session_state.balance=10000

    if "portfolio" not in st.session_state:
        st.session_state.portfolio={}

    st.subheader("💰 Virtual Trading Simulator")

    st.metric("Virtual Balance",st.session_state.balance)

    stock=st.text_input("Stock to Trade","AAPL")

    if st.button("Buy 1 Share"):

        data=yf.download(stock,period="1d")

        price=float(data["Close"].iloc[-1])

        if st.session_state.balance>=price:

            st.session_state.balance-=price

            if stock in st.session_state.portfolio:

                st.session_state.portfolio[stock]["shares"]+=1

            else:

                st.session_state.portfolio[stock]={
                "shares":1,
                "buy_price":price
                }

            st.success(f"Bought 1 share of {stock} at {price}")

        else:

            st.error("Not enough balance")

    if st.button("Sell 1 Share"):

        if stock in st.session_state.portfolio and st.session_state.portfolio[stock]["shares"]>0:

            data=yf.download(stock,period="1d")

            price=float(data["Close"].iloc[-1])

            buy_price=st.session_state.portfolio[stock]["buy_price"]

            profit=price-buy_price

            st.session_state.balance+=price

            st.session_state.portfolio[stock]["shares"]-=1

            if profit>0:
                st.metric("Profit",round(profit,2))
            else:
                st.metric("Loss",round(profit,2))

    st.subheader("📂 Portfolio")

    total_value=0

    for s,info in st.session_state.portfolio.items():

        shares=info["shares"]
        buy_price=info["buy_price"]

        data=yf.download(s,period="1d")

        current_price=float(data["Close"].iloc[-1])

        value=shares*current_price

        profit_loss=(current_price-buy_price)*shares

        total_value+=value

        col1,col2,col3=st.columns(3)

        col1.metric("Stock",s)
        col2.metric("Shares",shares)

        if profit_loss>0:
            col3.metric("Profit",round(profit_loss,2))
        else:
            col3.metric("Loss",round(profit_loss,2))

        st.write(
        smart_trade_explanation(
        profit_loss,
        buy_price*shares,
        st.session_state.balance
        )
        )

        st.write("---")

    st.subheader("Portfolio Value")

    st.write(total_value)

    st.subheader("Remaining Balance")

    st.write(st.session_state.balance)

    st.subheader("Total Account Value")

    st.write(total_value+st.session_state.balance)