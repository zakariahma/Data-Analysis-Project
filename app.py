import streamlit as st
import pandas as pd
from fuzzywuzzy import process
import numpy as np
import ast

st.set_page_config(
    page_title = "Movie Recommender",
    page_icon= ":movie_camera:",
    initial_sidebar_state= "expanded",
    layout="wide")

# Define your CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300..900;1,300..900&display=swap');
            
/* SideBar */

[data-testid="stSidebarContent"] {
    background-color:#B6BBC4;                
}

/* Header */            
[data-testid="stHeader"] {
    background-color: #161A30;
}
/* main content */
.st-emotion-cache-bm2z3a {
    background-color: #161A30;
    color: white;
    font-family: "Figtree", sans-serif;
}
/* Buttons */            
[data-testid="baseButton-secondary"] {
    background-color: #B6BBC4;
    color: #161A30;
    border: none;
}
[data-testid="baseButton-secondary"]:hover {
    color: #A91D3A;
    border-color: #A91D3A;
}
[data-testid="baseButton-secondary"]:active {
    color: #A91D3A;
    border-color: #A91D3A;
}
/* Buttons container */
[data-testid="stButton"] {
    display: flex;
    align-items: center;
    justify-content: center;       
}
/* Favorite Movie */ 
                      
# [data-testid="stMarkdownContainer"] p {
#     font-size: 1.5rem;
#     font-family: "Figtree", sans-serif;
#     font-weight: 600;
# }

# .st-emotion-cache-vdokb0 p {
#     font-size: 1.2rem;
#     font-family: "Figtree", sans-serif;
#     font-weight: 500;                                 
# }
            
[data-testid="stMarkdownContainer"] p {
    padding: 0.25rem;
    font-size: 1.5rem;
    font-family: "Figtree", sans-serif;
    font-weight: 600;    
}

/* Movie Title*/
[data-testid="stHeadingWithActionElements"] h2{
    padding-bottom: 0;
    margin-bottom: 0;
    color: white;
    font-family: "Figtree", sans-serif;
    font-weight: 700;
}

:has(.title) {
    gap: 0.5rem;
    color: white;
}
/* Metrics */
.st-emotion-cache-12w0qpk {
    /*background-color: #31363F;*/
    color: white;
    
}

/* Metrics titles */
.st-emotion-cache-17c4ue {
    color: white; 
}

#overview {
    color: white;
    font-family: "Figtree", sans-serif;
}          


/* Actors links */            
.st-emotion-cache-vdokb0 a {
    color: #76ABAE;
    font-weight: 600;
}

img {
    border-radius: 10px;        
}
/* Movies Buttons*/            
.st-emotion-cache-7ym5gk  {
    color: white; 
    background-color: #161A30;
    border: none; 
}
/*Recommend Button*/
.st-emotion-cache-q3uqly {
    background-color: #B6BBC4;
    color: #161A30;
    border: none;
    font-family: "Figtree", sans-serif;         
}
.st-emotion-cache-j6qv4b p{
    font-family: "Figtree", sans-serif; 
    font-weight: 600;
}
.st-emotion-cache-q3uqly:hover {
    background-color: white;        
}
.st-emotion-cache-q3uqly:active {
    background-color: white;        
}

.st-emotion-cache-1wivap2 {
    text-align: center;
    font-family: "Figtree", sans-serif;
}
.st-emotion-cache-17c4ue {
    display: flex;
    justify-content: center; 
    font-family: "Figtree", sans-serif;       
}
</style>
""", unsafe_allow_html=True) 


#df_movies = pd.read_csv('data.csv')
@st.cache_data
def load_data(filename):
    data = pd.read_csv(filename)
    return data

df_movies = load_data('data.csv')

movie_titles = list(df_movies['formatted_title'])

@st.cache_data(show_spinner=False)
def movie_finder(title, all_titles):
    closest_match = process.extract(title, all_titles, limit = 5)
    return [elt[0] for elt in closest_match]

@st.cache_data
def get_poster_link(df, index):
    poster_path = df.loc[index, 'poster_path']
    if pd.notna(poster_path):
        return f"https://image.tmdb.org/t/p/original{poster_path}"
    return "https://image.tmdb.org/t/p/original/z0235iN9Q8JTJE9L2MqzzaJpHWC.jpg"

@st.cache_data
def return_result(movie):
    movie_id = df_movies[df_movies['formatted_title'] == movie].reset_index().loc[0,'id']
    df = df_movies[df_movies['id'] == int(movie_id)].reset_index()
    result = {}
    result['title'] = df.loc[0, 'title']
    result['year'] = df.loc[0, 'release_date']
    result['language'] = df.loc[0, 'original_language']
    result['vote_average'] = df.loc[0, 'vote_average'] 
    result['vote_count'] = df.loc[0, 'vote_count']
    result['poster_link'] = get_poster_link(df, 0)
    result['overview'] = df.loc[0, 'overview']
    actors = ast.literal_eval(df.loc[0, 'actors'])
    director = ast.literal_eval(df.loc[0, 'director'])
    result['genres'] = ', '.join(ast.literal_eval(df.loc[0, 'genre_names']))

    actor_links = [(elt[1], "https://www.themoviedb.org/person/" + str(elt[0])) for elt in actors]
    director_link = (director[1], "https://www.themoviedb.org/person/" + str(director[0]))
    result['director_page'] = f'<a href="{director_link[1]}" target="_blank">{director_link[0]}</a>'
    result['actor_pages'] = ' | '.join([f'<a href="{url}" target="_blank">{name}</a>' for name, url in actor_links])

    #Recommended movies
    movies_ids = df.loc[0, 'Ranks'].split(',')[1:6]
    movies_ids = [int(elt) for elt in movies_ids]
    result['movie_titles'] = []
    result['movie_formatted_titles'] = []
    result['movie_posters'] = []
    for id in movies_ids:
        df1 = df_movies[df_movies['id'] == id].reset_index()
        result['movie_titles'].append(df1.loc[0, 'title'])
        result['movie_formatted_titles'].append(df1.loc[0, 'formatted_title'])
        result['movie_posters'].append(get_poster_link(df1, 0))
    return result
    
if 'movie' not in st.session_state:
    st.session_state.movie = ""

with st.sidebar:
    # Display the text input field
    movie_name = st.text_input("✨ Favorite Movie",  key='search')
    with st.spinner("Searching for your movie 🎞️"):
        matches = movie_finder(movie_name, movie_titles)
    # Use the current state of 'movie' to update the display dynamically
    if movie_name:  # Check if there is something in the input
        if st.button(matches[0]):
            st.session_state.movie = matches[0]
            st.session_state['button'] = False
        if st.button(matches[1]):
            st.session_state.movie = matches[1]
            st.session_state['button'] = False
        if st.button(matches[2]):
            st.session_state.movie = matches[2]
            st.session_state['button'] = False
        if st.button(matches[3]):
            st.session_state.movie = matches[3]
            st.session_state['button'] = False
        if st.button(matches[4]):
            st.session_state.movie = matches[4]
            st.session_state['button'] = False
    else:
        st.markdown("Please type your favorite movie 🎞️")

if st.session_state.movie :
    result = return_result(st.session_state.movie)
    #  Layout
    col1, col2= st.columns([7, 2])
    with col2:
        st.image(result['poster_link'])
    with col1:
        col3, col4, col5 = st.columns([2, 1, 1])
        with col3:
            st.markdown(f'<h2 class="title">{result["title"]}</h2>', unsafe_allow_html=True)
            st.markdown(f'<span class = "details">{result["year"]} • {result["language"]} • {result["genres"]}</span>', unsafe_allow_html=True)      
        with col4:
            st.metric(label="Vote Average", value = round(result['vote_average'], 2))
        with col5:
            st.metric(label="Vote Count", value = int(result['vote_count']))
        st.header('Overview')
        #st.markdown(css_style, unsafe_allow_html=True)
        st.markdown(f'<p class="custom-font">{result["overview"]}</p>', unsafe_allow_html=True)
        st.markdown("Stars: " + result['actor_pages'], unsafe_allow_html=True)
        st.markdown("Director: " + result['director_page'], unsafe_allow_html=True)

    button1 = st.button("Recommend similar movies", type = "primary")
    if st.session_state.get('button') != True:
        st.session_state['button'] = button1
    if st.session_state['button'] == True:
    
        col6, col7, col8, col9, col10 = st.columns(5)
        with col6:
            st.image(result['movie_posters'][0])
            if st.button(f" {result['movie_formatted_titles'][0]} "):
                st.session_state.movie = f"{result['movie_formatted_titles'][0]}"
                st.session_state['button'] = False
                st.rerun()
        with col7:
            st.image(result['movie_posters'][1])
            if st.button(f" {result['movie_formatted_titles'][1]} "):
                st.session_state.movie = f"{result['movie_formatted_titles'][1]}"
                st.session_state['button'] = False
                st.rerun()
        with col8:
            st.image(result['movie_posters'][2])
            if st.button(f" {result['movie_formatted_titles'][2]} "):
                st.session_state.movie = f"{result['movie_formatted_titles'][2]}"
                st.session_state['button'] = False
                st.rerun()
        with col9:
            st.image(result['movie_posters'][3])
            if st.button(f" {result['movie_formatted_titles'][3]} "):
                st.session_state.movie = f"{result['movie_formatted_titles'][3]}"
                st.session_state['button'] = False
                st.rerun()
        with col10:
            st.image(result['movie_posters'][4])
            if st.button(f" {result['movie_formatted_titles'][4]} "):
                st.session_state.movie = f"{result['movie_formatted_titles'][4]}"
                st.session_state['button'] = False
                st.rerun()
        # col11, col12, col13, col14, col15 = st.columns(5)
        # with col11:
        #     if st.button(f" {result['movie_formatted_titles'][0]} "):
        #         st.session_state.movie = f"{result['movie_formatted_titles'][0]}"
        #         st.session_state['button'] = False
        #         st.rerun()
        # with col12:
        #     if st.button(f" {result['movie_formatted_titles'][1]} "):
        #         st.session_state.movie = f"{result['movie_formatted_titles'][1]}"
        #         st.session_state['button'] = False
        #         st.rerun()
        # with col13:
        #     if st.button(f" {result['movie_formatted_titles'][2]} "):
        #         st.session_state.movie = f"{result['movie_formatted_titles'][2]}"
        #         st.session_state['button'] = False
        #         st.rerun()
        # with col14:
        #     if st.button(f" {result['movie_formatted_titles'][3]} "):
        #         st.session_state.movie = f"{result['movie_formatted_titles'][3]}"
        #         st.session_state['button'] = False
        #         st.rerun()
        # with col15:
        #     if st.button(f" {result['movie_formatted_titles'][4]} "):
        #         st.session_state.movie = f"{result['movie_formatted_titles'][4]}"
        #         st.session_state['button'] = False
        #         st.rerun()



    