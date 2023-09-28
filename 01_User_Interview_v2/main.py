import streamlit as st
from streamlit_gsheets import GSheetsConnection

url = "https://docs.google.com/spreadsheets/d/1Oz2xLwohcOCBj3ECk3HQ3MUiO8oiJz5HIj11Bqgj22U/edit#gid=0"

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

data = conn.read(spreadsheet=url, usecols=[0, 1])
st.dataframe(data)