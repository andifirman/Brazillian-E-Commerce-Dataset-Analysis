import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.ticker as mtick
import seaborn as sns

import streamlit as st 
from babel.numbers import format_currency

sns.set(style='dark')

# -------------------------------------------------------------------------------- #
def create_daily_orders(df):
  daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
    "order_id": "nunique",
    "payment_value": "sum"
  })
  daily_orders_df = daily_orders_df.reset_index()
  daily_orders_df.rename(columns={
    "order_id": "order_count",
    "payment_value": "revenue"
  }, inplace=True)

  return daily_orders_df


def create_customer_spent(df):
  customer_spent_df = df.resample(rule='D', on='order_approved_at').agg({
    "payment_value": "sum"
  })
  customer_spent_df = customer_spent_df.reset_index()
  customer_spent_df.rename(columns={
    "payment_value": "total_spent"
  }, inplace=True)

  return customer_spent_df


def create_sum_order_items(df):
  sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
  sum_order_items_df.rename(columns={
      "product_id": "product_count"
  }, inplace=True)
  sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

  return sum_order_items_df


def create_bystate(df):
  bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
  bystate_df.rename(columns={
      "customer_id": "customer_count"
  }, inplace=True)
  most_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
  bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

  return bystate_df, most_state


def create_bycity(df):
  bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
  bycity_df.rename(columns={
      "customer_id": "customer_count"
  }, inplace=True)
  most_city = bycity_df.loc[bycity_df['customer_count'].idxmax(), 'customer_city']
  bycity_df = bycity_df.sort_values(by='customer_count', ascending=False)

  return bycity_df, most_city


def create_order_status(df):
  order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
  most_status = order_status_df.idxmax()

  return order_status_df, most_status


# -------------------------------------------------------------------------------- #

# Melakukan import dataset yang dibutuhkan untuk melakukan visualisasi data pada dashboard
all_df = pd.read_csv('https://raw.githubusercontent.com/andifirman/Brazillian-E-Commerce-Dataset-Analysis/main/dashboard/all_data.csv')

datetime_columns = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]

all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
  all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()


with st.sidebar:
  # Menambahkan logo perusahaan pada dashboard
  # <a href="https://www.freepik.com/free-vector/gradient-mobile-store-logo-design_31818468.htm#fromView=keyword&page=1&position=0&uuid=b0f09087-f828-4157-9e21-b8933e9f4665">Image by freepik</a>

  st.image("https://github.com/andifirman/Brazillian-E-Commerce-Dataset-Analysis/raw/main/assets/new-logo-by-freepik.png")

  # Mengambil start_date dan end_date dari date_input
  start_date, end_date = st.date_input(
    label='Rentang Waktu', 
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
  )

# start_date dan end_date di atas akan digunakan untuk memfilter all_df. 
# Data yang telah difilter ini selanjutnya akan disimpan dalam main_df
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

daily_orders_df = create_daily_orders(main_df)
sum_spent_df = create_customer_spent(main_df)
sum_order_items_df = create_sum_order_items(main_df)
by_state, most_state = create_bystate(main_df)
by_city, most_city = create_bycity(main_df)
order_status, most_status = create_order_status(main_df)


# MELENGKAPI DASHBOARD DENGAN BERBAGAI VISUALISASI DATA
st.header('Sales Performance Dashboard :fire:')

# Tahap berikutnya adalah menambahkan informasi terkait daily orders 
# pada dashboard yang akan kita buat. Pada proyek ini, kita akan menampilkan 
# tiga informasi terkait daily orders, yaitu jumlah order harian serta 
# total order dan revenue dalam range waktu tertentu. Pada contoh proyek ini
# kita menampilkan informasi total order dan revenue dalam bentuk metric() 
# yang ditampilkan menggunakan layout columns().

# DAILY ORDERS
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
  total_orders = daily_orders_df.order_count.sum()
  st.metric("Total orders", value=total_orders)

with col2:
  total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR')
  st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
  daily_orders_df["order_approved_at"],
  daily_orders_df["order_count"],
  marker='o',
  linewidth=2,
  color="#90CAF9"
)

ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# CUSTOMERS SPENT
st.subheader("Tren Bakar Uang")
col1, col2 = st.columns(2)

with col1:
  total_spent = format_currency(sum_spent_df.total_spent.sum(), "BRL", locale="pt_BR")
  st.metric("Total Uang Dibelanjakan", value=total_spent)

with col2:
  avg_spent = format_currency(sum_spent_df.total_spent.mean(), "BRL", locale="pt_BR")
  st.metric("Rata-Rata Uang Dibakar", value=avg_spent)

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
  sum_spent_df["order_approved_at"],
  sum_spent_df["total_spent"],
  marker="o",
  linewidth=2,
  color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# ORDER ITEMS
st.subheader("Tren Barang Yang Terjual")
col1, col2 = st.columns(2)

with col1:
  total_items = sum_order_items_df.product_count.sum()
  st.metric("Total Barang Terjual", value=total_items)

with col2:
  avg_items = round(sum_order_items_df.product_count.mean(), 2)
  st.metric("Rata-Rata Barang Terjual", value=avg_items)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=50)
ax[0].tick_params(axis ='y', labelsize=35)
ax[0].tick_params(axis ='x', labelsize=30)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)


# CUSTOMERS DEMOGRAPHIC
# 1. Berdasarkan Customer State
st.subheader("Persebaran Pelanggan Berdasarkan State")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count", 
    y="customer_state",
    data=by_state.sort_values(by="customer_count", ascending=False).head(8),
    palette=colors,
    ax=ax
)
ax.set_title("Jumlah Pelanggan Berdasarkan State", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# 2. Berdasarkan Customer City
st.subheader("Persebaran Pelanggan Berdasarkan City")

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count", 
    y="customer_city",
    data=by_city.sort_values(by="customer_count", ascending=False).head(8),
    palette=colors,
    ax=ax
)
ax.set_title("Jumlah Pelanggan Berdasarkan city", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.caption('Copyright (C) Andi Firmansyah 2024')
