# # streamlit_app.py

# import pandas as pd
# import streamlit as st
# import unicodedata

# # Read in data from the Google Sheet.
# # Uses st.cache_data to only rerun when the query changes or after 10 min.
# st.set_page_config(
#     page_title="誰が本を読んだのか？",
#     page_icon="Assets/icon.png",
#     layout="centered",
#     initial_sidebar_state="expanded",
#     menu_items={
#         'Get help': 'https://yomo-issyo.com',
#         'Report a bug': "https://yomo-issyo.com",
#         'About': "#This is trial comment sheet for YOMY!. This is an *super* cool app!"
#     }
# )

# @st.cache_data(ttl=600)
# def load_data(sheets_url):
#     csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
#     return pd.read_csv(csv_url)

# # load data from google sheet
# history = load_data(st.secrets["book_history"])
# bookdata = load_data(st.secrets["book_data"])

# st.title('一体誰が本を読んだのか？')

# def normalize_unicode(text):
#     # Ensure that the text is a string before normalizing
#     if isinstance(text, str):
#         return unicodedata.normalize("NFC", text)
#     else:
#         # Handle the case where text is not a string (e.g., None or float)
#         return unicodedata.normalize("NFC", str(text)) if text is not None else None

# def get_unique_names(history):
#     names = set()
#     for name_list in history['Name']:
#         for name in name_list.split(','):
#             names.add(name.strip())
#     return sorted(list(names))

# def get_unread_books(selected_names, history, bookdata):
#     read_books = set()
#     for index, row in history.iterrows():
#         names = [normalize_unicode(name.strip()) for name in row['Name'].split(',')]
#         if any(name in selected_names for name in names):
#             read_books.add(normalize_unicode(row['Title']))

#     all_books = bookdata.copy()
#     all_books['Title'] = all_books['Title'].apply(normalize_unicode)
#     unread_books = all_books[~all_books['Title'].isin(read_books)].sort_values('Title')
#     return unread_books

# # Get unique names from history
# unique_names = get_unique_names(history)

# # Create a multiselect widget for users to choose names
# selected_names = st.multiselect('名前を選択してください:', unique_names)

# # Create a button for users to click and display the unread books
# if st.button('まだ誰も読んでいない本を表示'):
#     st.balloons()
#     unread_books = get_unread_books(selected_names, history, bookdata)
#     st.header('未読の本(体験会を除く):')
#     for index, row in unread_books.iterrows():
#         st.write(f"{row['Title']} - {row['author']}")


import streamlit as st
import unicodedata
import numpy as np
import csv
import requests

# Set page configuration
st.set_page_config(
    page_title="誰が本を読んだのか？",
    page_icon="Assets/icon.png",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get help': 'https://yomo-issyo.com',
        'Report a bug': "https://yomo-issyo.com",
        'About': "#This is trial comment sheet for YOMY!. This is an *super* cool app!"
    }
)

@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    response = requests.get(csv_url)
    decoded_content = response.content.decode('utf-8')
    data = list(csv.reader(decoded_content.splitlines(), delimiter=','))
    headers = data[0]
    content = np.array(data[1:])
    return headers, content

# Load data from Google Sheets
history_headers, history_data = load_data(st.secrets["book_history"])
bookdata_headers, bookdata_data = load_data(st.secrets["book_data"])

st.title('一体誰が本を読んだのか？')

def normalize_unicode(text):
    if isinstance(text, str):
        return unicodedata.normalize("NFC", text)
    else:
        return unicodedata.normalize("NFC", str(text)) if text is not None else None

def get_unique_names(history_data, name_idx):
    names = set()
    for name_list in history_data[:, name_idx]:
        for name in name_list.split(','):
            names.add(name.strip())
    return sorted(list(names))

def get_unread_books(selected_names, history_data, history_headers, bookdata_data, bookdata_headers):
    title_idx = history_headers.index('Title')
    name_idx = history_headers.index('Name')
    
    read_books = set()
    for row in history_data:
        names = [normalize_unicode(name.strip()) for name in row[name_idx].split(',')]
        if any(name in selected_names for name in names):
            read_books.add(normalize_unicode(row[title_idx]))

    title_idx_bookdata = bookdata_headers.index('Title')
    unread_books = []
    for row in bookdata_data:
        title = normalize_unicode(row[title_idx_bookdata])
        if title not in read_books:
            unread_books.append(row)
    
    unread_books = sorted(unread_books, key=lambda x: x[title_idx_bookdata])
    return unread_books

# Get unique names from history
name_idx = history_headers.index('Name')
unique_names = get_unique_names(history_data, name_idx)

# Create a multiselect widget for users to choose names
selected_names = st.multiselect('名前を選択してください:', unique_names)

# Create a button for users to click and display the unread books
if st.button('まだ誰も読んでいない本を表示'):
    st.balloons()
    unread_books = get_unread_books(selected_names, history_data, history_headers, bookdata_data, bookdata_headers)
    st.header('未読の本(体験会を除く):')
    author_idx = bookdata_headers.index('author')
    title_idx_bookdata = bookdata_headers.index('Title')
    for row in unread_books:
        st.write(f"{row[title_idx_bookdata]} - {row[author_idx]}")