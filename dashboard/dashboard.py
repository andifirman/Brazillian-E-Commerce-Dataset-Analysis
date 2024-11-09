import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.ticker as mtick
import seaborn as sns

import streamlit as st 
from babel.numbers import format_currency

sns.set(style='dark')

# -------------------------------------------------------------------------------- #
def create_daily_order(df):
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


def review_score_df(df):
  review_scores = df['review_score'].value_counts().sort_values(ascending=False)
  most_score = review_scores.idxmax()

  return review_scores, most_score


def create_bystate_df(df):
  bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
  bystate_df.rename(columns={
      "customer_id": "customer_count"
  }, inplace=True)
  most_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
  bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

  return bystate_df, most_state


def create_bycity_df(df):
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
all_df = pd.read_csv('all_data.csv')

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

  st.image("https://github.com/andifirman/Brazillian-E-Commerce-Dataset-Analysis/raw/main/assets/logo-by-freepik.png", width=100)

  # Mengambil start_date dan end_date dari date_input
  start_date, end_date = st.date_input(
    label='Rentang Waktu', 
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
  )