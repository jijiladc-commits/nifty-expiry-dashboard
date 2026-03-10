import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")

st.title("NIFTY Expiry Options Scanner")

st_autorefresh(interval=30000)

def fetch_data():

    url="https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

    headers={"User-Agent":"Mozilla/5.0"}

    s=requests.Session()
    s.get("https://www.nseindia.com",headers=headers)

    data=s.get(url,headers=headers).json()

    spot=data["records"]["underlyingValue"]

    rows=[]

    for d in data["records"]["data"]:

        if "CE" in d:

            ce=d["CE"]

            rows.append({
                "strike":d["strikePrice"],
                "price":ce["lastPrice"],
                "volume":ce["totalTradedVolume"],
                "oi":ce["openInterest"],
                "oi_change":ce["changeinOpenInterest"]
            })

    df=pd.DataFrame(rows)

    return df,spot


df,spot=fetch_data()

st.metric("NIFTY Spot",spot)

atm=round(spot/50)*50

st.write("ATM Strike:",atm)

df["distance"]=abs(df["strike"]-spot)

df["gamma"]=df["oi"]/(df["distance"]+1)

df["vol_score"]=df["volume"]/df["volume"].max()

df["oi_score"]=df["oi_change"].abs()/df["oi_change"].abs().max()

df["gamma_score"]=df["gamma"]/df["gamma"].max()

df["score"]=df["vol_score"]*0.4+df["oi_score"]*0.3+df["gamma_score"]*0.3

cheap=df[(df["price"]>=0.5)&(df["price"]<=3)]

candidates=cheap[cheap["distance"]<=100]

top=candidates.sort_values("score",ascending=False).head(10)

st.subheader("Explosion Candidates")

st.dataframe(top)

fig=px.bar(top,x="strike",y="score")

st.plotly_chart(fig)

st.subheader("OI Walls")

oi_walls=df.sort_values("oi",ascending=False).head(5)

st.dataframe(oi_walls)

fig2=px.bar(df,x="strike",y="gamma")

st.plotly_chart(fig2)
