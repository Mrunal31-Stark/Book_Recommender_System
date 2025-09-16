# import the libraries 
import streamlit as st 
import pickle 
import numpy as np 
import pandas as pd 
import gdown
import os

# Download large files if they don't exist
if not os.path.exists('books.pkl'):
    url ="https://drive.google.com/uc?id=1slJTsy1sG2cEVVDxV0rGOexHOb3IcUv1"
    gdown.download(url, "books.pkl", quiet=False)

if not os.path.exists('Books.csv'):
    url = "https://drive.google.com/uc?id=1d3Vl2DFvd-vA45W1lOKySVLpuH8RP52T"
    gdown.download(url, "Books.csv", quiet=False)

st.set_page_config(layout="wide", page_title="📚 Book Recommender System")

# Custom CSS for styling
st.markdown("""
    <style>
        /* Background Gradient */
        .stApp {
            background: linear-gradient(135deg, #1f1c2c, #928dab);
            color: white;
        }

        /* Headers */
        h1, h2, h3, h4, h5 {
            color: #f5f5f5;
            text-align: center;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #2c2c54;
            color: white;
        }

        /* Glowing button */
        div.stButton > button {
            background-color: #6c5ce7;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.6em 1.2em;
            font-size: 16px;
            transition: 0.3s;
            box-shadow: 0px 0px 8px #6c5ce7;
        }
        div.stButton > button:hover {
            background-color: #341f97;
            box-shadow: 0px 0px 20px #9b59b6;
            transform: scale(1.05);
        }

        /* Card styling */
        .recommend-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
            margin: 10px;
        }
        .recommend-card img {
            border-radius: 8px;
        }
        .recommend-title {
            font-size: 16px;
            font-weight: bold;
            margin-top: 8px;
            color: #ffffff;
        }
        .recommend-author {
            font-size: 14px;
            color: #dcdde1;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1>📚 Book Recommender System</h1>", unsafe_allow_html=True)
st.markdown('''
            ##### The site uses collaborative filtering  
            ##### Discover books that match your taste or explore top 50 popular picks.  
            ''')
st.markdown("<h2>🔍 Search for a Book</h2>", unsafe_allow_html=True)
search_query = st.text_input("Type a book title here (partial titles work!)")

# import our models : 
popular = pickle.load(open('popular.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb')) 

# Top 50 Books 
st.sidebar.title("⭐ Top 50 Books")

if st.sidebar.button("SHOW"):
    cols_per_row = 5 
    num_rows = 10 
    for row in range(num_rows): 
        cols = st.columns(cols_per_row)
        for col in range(cols_per_row): 
            book_idx = row * cols_per_row + col
            if book_idx < len(popular):
                with cols[col]:
                    st.markdown(
                        f"""
                        <div class="recommend-card">
                            <img src="{popular.iloc[book_idx]['Image-URL-M']}" width="120">
                            <div class="recommend-title">{popular.iloc[book_idx]['Book-Title']}</div>
                            <div class="recommend-author">{popular.iloc[book_idx]['Book-Author']}</div>
                        </div>
                        """, unsafe_allow_html=True
                    )

# Function to recommed Books (untouched)
def recommend(book_name):
    index = np.where(pt.index == book_name)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x : x[1], reverse=True)[1:11]
    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item) 
    return data

# Book list
book_list = pt.index.values 

st.sidebar.title("📖 Similar Book Suggestions")
selected_book = st.sidebar.selectbox("Select a book from the dropdown", book_list)

if st.sidebar.button("Recommend Me"):
    book_recommend = recommend(selected_book)
    num_recs = len(book_recommend)
    cols_per_row = 5
    num_rows = (num_recs + cols_per_row - 1) // cols_per_row  # Ceiling division
    for row in range(num_rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            book_idx = row * cols_per_row + col_idx
            if book_idx < num_recs:
                with cols[col_idx]:
                    st.markdown(
                        f"""
                        <div class="recommend-card">
                            <img src="{book_recommend[book_idx][2]}" width="120">
                            <div class="recommend-title">{book_recommend[book_idx][0]}</div>
                            <div class="recommend-author">{book_recommend[book_idx][1]}</div>
                        </div>
                        """, unsafe_allow_html=True
                    )

                
if search_query:
    matched_books = [b for b in book_list if search_query.lower() in b.lower()]
    if matched_books:
        selected_book_main = st.selectbox("Select the book you meant:", matched_books)
        if st.button("Recommend for this Book"):
            book_recommend = recommend(selected_book_main)
            num_recs = len(book_recommend)
            cols_per_row = 5
            num_rows = (num_recs + cols_per_row - 1) // cols_per_row
            for row in range(num_rows):
                cols = st.columns(cols_per_row)
                for col_idx in range(cols_per_row):
                    book_idx = row * cols_per_row + col_idx
                    if book_idx < num_recs:
                        with cols[col_idx]:
                            st.markdown(
                                f"""
                                <div class="recommend-card">
                                    <img src="{book_recommend[book_idx][2]}" width="120">
                                    <div class="recommend-title">{book_recommend[book_idx][0]}</div>
                                    <div class="recommend-author">{book_recommend[book_idx][1]}</div>
                                </div>
                                """, unsafe_allow_html=True
                            )
    else:
        st.warning("No books matched your search. Try typing more keywords.")


# import data
books = pd.read_csv('Books.csv')  
users = pd.read_csv('Data/Users.csv') 
ratings = pd.read_csv('Data/Ratings.csv') 

st.sidebar.title("📊 Data Used")

if st.sidebar.button("Show"):
    st.subheader('📘 Books Data')
    st.dataframe(books)
    st.subheader('⭐ Ratings Data')
    st.dataframe(ratings)
    st.subheader('👤 Users Data')
    st.dataframe(users)
