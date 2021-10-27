# The script which is run. All Streamlit calls here. Acts a bit like view and controller combined. This is where the app is put together.

import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import os
import streamlit.components.v1 as components
import base64


API_URL = 'https://world.openfoodfacts.org/api/v0/product'
NUTRIMENTS_METRICS = ['fat_100g', 'salt_100g',
                      'proteins_100g', 'sugars_100g', 'carbohydrates_100g', 'energy_100g']

######## UTILS FUNCTION ########


def fetch(session, url):
    try:
        result = session.get(url)
        return result.json()
    except:
        return {}


def handle_form_sub(code: int):
    product_url = f'{API_URL}/{code}'
    full_data = fetch(session, product_url)
    if (full_data['status'] == 0):
        err_txt = full_data['status_verbose'].title() + '.'
        st.error(err_txt)
    else:
        data = extract_json(full_data)
        print_metrics(data)
        with st.expander("🔎 Expand data"):
            st.json(full_data)


def print_metrics(data):
    cols = st.columns(len(data))
    for i, x in enumerate(data):
        metric_name = x.split('_')[0].title()
        cols[i].metric(metric_name, data.get(x))


def extract_json(data):
    data = data['product']['nutriments']
    extracted_data = {}
    for x in NUTRIMENTS_METRICS:
        extracted_data[f'{x}'] = data[x]
    return extracted_data


######## LAYOUT FUNCTION ########

def form_txt():
    with st.form('form_ean13'):
        ean13 = st.text_input('⬇️ Enter an EAN13 code', value='', key='ean13')
        submitted_code = st.form_submit_button('Submit')

    if submitted_code:
        with st.spinner('Searching...'):
            time.sleep(2)
            cond_empty = ean13 == ' '
            cond_len = len(ean13) in [12, 13]
            cond_num = ean13.isnumeric()
            if (not cond_empty & cond_num & cond_len):
                handle_form_sub(ean13)
            else:
                if (cond_empty):
                    st.error('Please enter an ean13 code first.')
                elif (not cond_num):
                    st.error('Your code must be only composed of numeric values.')
                elif (not cond_len):
                    st.error('Your code must be 13 character long.')
                else:
                    st.error('Unknown error.')


##############
st.set_page_config(page_title='PoC Nutrition', page_icon='🤖')
h1 = st.title('Poc Nutrition')
session = requests.Session()

css_file = open(os.path.join(os.getcwd(), "style.css"), 'r').read()
css_txt = '<style>' + css_file + '</style>'

st.markdown(css_txt, unsafe_allow_html=True)
st.markdown('<script src="https://cdn.plot.ly/plotly-2.4.2.min.js"></script>',
            unsafe_allow_html=True)

st.markdown('> I concede that in the current state, this demo does not bring something new nor intersting. The main goal was to validate the corresponding proficiency modules.')
st.markdown(
    "This demo is based on the OpenFoodFact API. \nClick on `Expand data` to get the full JSON response.")

with st.expander("📊 Display EDA plots :"):
    st.markdown(
        'Because of a lack of time, the integration of dynamic plots are not available yet via `Streamlit`. However they are published [here.](https://poc-nutrition.herokuapp.com/charts)')

form_txt()
