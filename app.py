# streamlit_app.py

import pandas as pd
import streamlit as st
import unicodedata

# Read in data from the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.

@st.cache_data(ttl=600)

def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

# load data from google sheet
hisotry = load_data(st.secrets["book_history"])
bookdata = load_data(st.secrets["book_data"])

st.title('一体誰が本を読んだのか？')

# show the csv as table
# st.table(hisotry)
# st.table(bookdata)

def normalize_unicode(text):
    return unicodedata.normalize("NFC", text)


def get_unique_names(history):
    names = set()
    for name_list in history['Name']:
        for name in name_list.split(','):
            names.add(name.strip())
    return sorted(list(names))

def get_unread_books(selected_names, history, bookdata):
    read_books = set()
    for index, row in history.iterrows():
        names = [normalize_unicode(name.strip()) for name in row['Name'].split(',')]
        if any(name in selected_names for name in names):
            read_books.add(normalize_unicode(row['Title']))

    all_books = bookdata.copy()
    all_books['Title'] = all_books['Title'].apply(normalize_unicode)
    unread_books = all_books[~all_books['Title'].isin(read_books)].sort_values('Title')
    return unread_books


# Get unique names from history
unique_names = get_unique_names(hisotry)

# Create a multiselect widget for users to choose names
selected_names = st.multiselect('名前を選択してください:', unique_names)

# Create a button for users to click and display the unread books
if st.button('未読の本を表示'):
    unread_books = get_unread_books(selected_names, hisotry, bookdata)
    st.write('未読の本:')
    for index, row in unread_books.iterrows():
        st.write(f"{row['Title']} - {row['author']}")
