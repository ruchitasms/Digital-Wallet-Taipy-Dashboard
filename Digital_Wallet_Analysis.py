#!/usr/bin/env python
# coding: utf-8

# In[1]:


import warnings
warnings.filterwarnings('ignore')
from taipy.gui import Gui
import pandas as pd
import datetime


# In[3]:


#Reading and preparing raw data
try:
    rd = pd.read_csv('digital_wallet_transactions.csv', parse_dates=["transaction_date"], low_memory=False)
    if "paid_amt" not in rd.columns:
        rd["paid_amt"]=rd["product_amount"]+rd["transaction_fee"]-rd["cashback"]
    print (f"Digital Payments Transactions Loaded Successully! {rd.shape[0]} rows")
except Exception as e:
    print(f"Error Loading Raw data: {e}")
    rd = pd.DataFrame()

#Defining Payment Methods Filter
pay_opt = ["All Methods"]+rd["payment_method"].dropna().unique().tolist()

#Defining Visualizations as List
charts = ["Total Revenue over time", "Revenue by Payment Method", "Top Merchant Names", "Location Demographics"]


# In[4]:


#Preparing Default State by assigning default values to variables being used
st_dt = rd["transaction_date"].min()
ed_dt = rd["transaction_date"].max()
pt_method_sel = "All Methods"
sel_tab = "Revenue by Payment Method"
tot_rev = "INR 0.0"
tot_txn = 0
avg_pay = "INR 0.0"
top_dev = "--"
rev_ts_data = pd.DataFrame(columns=["transaction_date","paid_amt"])
method_data = pd.DataFrame(columns=["payment_method","paid_amt"])
top_merch = pd.DataFrame(columns=["merchant_name", "paid_amt"])
loc_data = pd.DataFrame(columns=["location", "paid_amt"])


# In[ ]:


#Defining Functions for various usage states of the dashboard
def apply_changes(state):
    fil_data = rd[(rd["transaction_date"]>=pd.to_datetime(state.st_dt))&(rd["transaction_date"]<=pd.to_datetime(state.ed_dt))]
    if state.pt_method_sel != "All Methods":
        fil_data = fil_data[fil_data["payment_method"]==state.pt_method_sel]
    state.rev_ts_data = fil_data.groupby("transaction_date")["paid_amt"].sum().reset_index()
    state.rev_ts_data.columns = ["transaction_date","paid_amt"]
    print ("Revenue Over Time:")
    print(state.rev_ts_data.head())

    state.method_data=fil_data.groupby("payment_method")["paid_amt"].sum().reset_index()
    state.method_data.columns=["payment_method","paid_amt"]
    print ("Payment Method wise:")
    print(state.method_data.head())

    state.top_merch=(fil_data.groupby("merchant_name")["paid_amt"].sum().sort_values(ascending=False).head(15).reset_index())
    state.top_merch.columns=["merchant_name","paid_amt"]
    print("Top Performing Merchants:")
    print(state.top_merch.head())

    state.loc_data=fil_data.groupby("location")["paid_amt"].sum().reset_index()
    state.loc_data.columns=["location","paid_amt"]
    print ("Location Wise Payments Made:")
    print(state.loc_data.head())

    state.rd = fil_data
    state.tot_rev = f"INR{fil_data["paid_amt"].sum():,.2f}"
    state.tot_txn = fil_data["transaction_id"].nunique()
    state.avg_pay = f"INR{fil_data["paid_amt"].sum()/max(fil_data["transaction_id"].nunique(),1):,.2f}"
    state.top_dev = (fil_data.groupby("device_type")["paid_amt"].sum().idxmax()
                     if not fil_data.empty else "--")
    
def on_change(state, var_name, var_value):
    if var_name in {"st_dt", "ed_dt", "pt_method_sel","sel_tab"}:
        print(f"State Modification: {var_name} = {var_value}")
        apply_changes(state)

def on_init(state):
    apply_changes(state)

import taipy.gui.builder as tgb

def get_partial_visibility(tab_name, sel_tab):
    return "block" if tab_name == sel_tab else "none"
    


# In[ ]:


#Laying out our Dashboard
with tgb.Page() as pg:
    tgb.text("# Digital Wallet Transactions Dashboard", mode = "md")
    tgb.text("#### By: Ruchita Shah", mode = "md")

    #Filters Arena
    with tgb.part(class_name = "card"):
        with tgb.layout(columns="1 1 2"):
            with tgb.part():
                tgb.text("Starting:")
                tgb.date("{st_dt}")
            with tgb.part():
                tgb.text("Ending:")
                tgb.date("{ed_dt}")
            with tgb.part():
                tgb.text("Select Payment Method:")
                tgb.selector(
                    value="{pt_method_sel}",
                    lov=pay_opt,
                    dropdown=True,
                    width="250px")
    #KPIs Display
    tgb.text("## Key KPI and Metrics", mode="md")
    with tgb.layout(columns='1 1 1 1'):
        with tgb.part(class_name="metric-card"):
            tgb.text("### Total Revenue", mode="md")
            tgb.text("{tot_rev}")
        with tgb.part(class_name="metric-card"):
            tgb.text("### Total Txns", mode="md")
            tgb.text("{tot_txn}")
        with tgb.part(class_name="metric-card"):
            tgb.text("### Avg Payment", mode="md")
            tgb.text("{avg_pay}")
        with tgb.part(class_name="metric-card"):
            tgb.text("### Top Device Type", mode="md")
            tgb.text("{top_dev}")

    tgb.text("## Exploratory Data Analysis", mode="md")
    with tgb.part(style="width:50%;"):
        tgb.selector(value="{sel_tab}", lov=["Total Revenue over time", "Revenue by Payment Method", "Top Merchant Names", "Location Demographics"], dropdown=True, width="360px")
    #Rendering on choice
    with tgb.part(render="{sel_tab=='Total Revenue over time'}"):
        tgb.chart(data="{rev_ts_data}", x="transaction_date", y="paid_amt", type="line", title="Total Revenue over time",)
    with tgb.part(render="{sel_tab=='Revenue by Payment Method'}"):
        tgb.chart(data="{method_data}", x="payment_method", y="paid_amt", type="bar", title="Revenue by Payment Method",)
    with tgb.part(render="{sel_tab=='Top Merchant Names'}"):
        tgb.chart(data="{top_merch}", x="merchant_name", y="paid_amt", type="bubble", title="Top Merchant Names",)
    with tgb.part(render="{sel_tab=='Location Demographics'}"):
        tgb.chart(data="{loc_data}", labels="location", values="paid_amt", type="pie", title="Location Demographics",)

    #Details Table
    tgb.text("## Details Table", mode="md")
    tgb.table(data="{rd}")           
    


# In[ ]:


#Building App
Gui(pg).run(title="Digital Wallet Dashboard", dark_mode=True, debug=True, port="auto", allow_unsafe_werkzeung=True, async_mode="threading")

