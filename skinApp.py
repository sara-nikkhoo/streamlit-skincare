import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


url = r'D:\sara\project\stremlitApp\skinCare\merged_products_reviews.csv'


st.title('Insights in Skincare Products: Ratings, Sentiments, and Reviews')
st.sidebar.title('Analysis of Skincare Products')
st.sidebar.markdown('This application is a Streamlit dashboard used to analyze skincare products 🧴💄')

def convert_to_sentiment(rating):
    if rating >= 4:
        return 'positive'
    elif rating >= 3 and rating < 4:
        return "neutral"
    else:
        return "negative"

@st.cache_data
def load_data():
    # Only load and return the main data
    return pd.read_csv(r'D:\sara\project\stremlitApp\skinCare\cleaned_makeup_products.csv')

@st.cache_data
def load_data_review():
    data_review = pd.read_csv(r'D:\sara\project\stremlitApp\skinCare\cleaned_makeup_reviews.csv')
    data_review.dropna(subset=['comments'], inplace=True)
    
    # Parse dates and apply sentiment conversion 
    data_review['created_date'] = pd.to_datetime(data_review['created_date'], utc=True)
    data_review['sentiment'] = data_review['rating'].apply(convert_to_sentiment)
    
    # Merge with product data and select necessary columns
    data = load_data() 
    products_with_reviews = pd.merge(
        data_review[['product_link_id', 'type', 'nickname', 'created_date', 'updated_date', 'rating', 'helpful_votes', 
                     'not_helpful_votes', 'comments', 'is_verified_reviewer', 'is_verified_buyer', 'sentiment']], 
        data, 
        on='product_link_id'
    )
    return products_with_reviews


data = load_data()
data_with_review = load_data_review()


# Define KPI values here
rating = round(data.rating.mean(),1)
max_price = data['price'].max()
rated_product = data.shape[0]
average_price = round(data.price.mean(),1)



# Styled KPIs after the title
st.markdown(
    f"""
    <style>
        .kpi-container {{
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            background-color: #f9f9f9;
            padding: 20px;
            width: 150px;
            text-align: center;
            border-radius: 8px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }}
        .kpi-title {{
            font-size: 18px;
            font-weight: bold;
            color: #004280;
        }}
        .kpi-value {{
            font-size: 24px;
            font-weight: bold;
            color: rgb(127 199 255); /* coral color for aesthetics */
        }}
        .kpi-icon {{
            font-size: 20px;
            color: #FFA07A; /* lighter coral for icon */
        }}
    </style>
    
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-icon">⭐</div>
            <div class="kpi-title">Rating</div>
            <div class="kpi-value">{rating}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🛒</div>
            <div class="kpi-title">Rated Products</div>
            <div class="kpi-value">{rated_product}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">💲💲</div>
            <div class="kpi-title">Max Price</div>
            <div class="kpi-value">{max_price}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">💲</div>
            <div class="kpi-title">Average Price</div>
            <div class="kpi-value">${average_price}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)



st.sidebar.subheader('Show random comments')
random_comment = st.sidebar.radio('rating star ⭐', (1, 2, 3, 4, 5))
random_row = data_with_review.query('rating_x == @random_comment and comments.str.len() < 50')[['comments', 'category']].sample(n=1)
st.sidebar.markdown(f"({random_row.iat[0, 1]}) {random_row.iat[0, 0]}")

st.sidebar.markdown("### Number of comments by sentiment")
select = st.sidebar.selectbox('Visualization Type', ['Bar plot', 'Pie chart'], key='1')
col = ['rating_star_1', 'rating_star_2', 'rating_star_3','rating_star_4','rating_star_5']
sentiment_count = data[col].sum()
sentiment_count = pd.DataFrame({'Rate':sentiment_count.index, 'Comments':sentiment_count.values})
if not st.sidebar.checkbox('Hide Charts', True, key='2'):
    st.markdown("### Number of Coments by rating")
    if select == 'Bar plot':
        fig = px.bar(sentiment_count, x='Rate', y='Comments', color='Comments')
        st.plotly_chart(fig)
    else:
        fig = px.pie(sentiment_count, values='Comments', names='Rate')
        st.plotly_chart(fig)


st.sidebar.subheader('Produkt Rating vs Price')
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]  
labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90']  # Define labels for the ranges
data['price_range'] = pd.cut(data['price'], bins=bins, labels=labels, right=False)
bubble_data = data.groupby('price_range').agg(
    comment_count=('num_reviews', 'sum'),
    mean_rating=('rating', 'mean')
).reset_index()
if not st.sidebar.checkbox('Hide Chart', True, key='3'):
    fig1 = px.scatter(
    bubble_data,
    x='price_range',
    y='mean_rating',  # Use rating to analyze customer satisfaction or expectations
    size='comment_count',  # Bubble size based on review count or popularity
    color='mean_rating',  # Color bubbles based on rating
    title="Products Price vs Rating",
    labels={'price_range': 'Price', 'mean_rating': 'Rating (*)'},  # Axis labels
    color_continuous_scale='Blues',  # Color scale for rating
    size_max=60  # Max bubble size
)
    st.plotly_chart(fig1)

st.sidebar.subheader("Total number of comments for each category")
each_cat = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='7')
top_cat = data.groupby('category')['num_reviews'].sum().sort_values(ascending=False).head(6)
top_cat = pd.DataFrame({'Products': top_cat.index, 'Comments': top_cat.values.flatten()})
if not st.sidebar.checkbox("Hide charts", True, key='8'):
    if each_cat == 'Bar plot':
        st.subheader("Total number of comments for each category")
        fig_1 = px.bar(top_cat, x='Products', y='Comments', color='Comments', height=500)
        st.plotly_chart(fig_1)
    if each_cat == 'Pie chart':
        st.subheader("Total number of comments for each category")
        fig_2 = px.pie(top_cat, values='Comments', names='Products')
        st.plotly_chart(fig_2)



data['sentiment'] = data['rating'].apply(convert_to_sentiment ) 

st.sidebar.subheader('Breakdown Categories By Rating')
choice = st.sidebar.multiselect('pick product', ['Face Primer', 'Blush', 'Highlighter', 'Foundation','Concealer', 'Bronzer'], key='10' )
if len(choice) > 0:
    
    selected_data = data[data['category'].isin(choice)]
    chart_type = st.sidebar.radio("Select Chart Type", ["Histogram", "Bar Chart", "Pie Chart"])

    if chart_type =="Histogram":
        st.subheader('Sentiment Count Across Categories')
        fig_4 = px.histogram(selected_data, x='category', y='sentiment', histfunc='count', color='sentiment', facet_col='sentiment',
                             labels={'sentiment': 'Sentiment Count'}, height=400, width=800)
        st.plotly_chart(fig_4)
    elif chart_type =="Bar Chart":
        st.subheader("Sentiment Breackdown Per Category")
        fig_5 = make_subplots(rows=1, cols=len(choice), subplot_titles=choice)
        for i, category in enumerate(choice):
            cat_data = selected_data.query('category == @category')[['category', 'sentiment']]
            sentiment_count = cat_data['sentiment'].value_counts()
            fig_5.add_trace(go.Bar(x=sentiment_count.index, y=sentiment_count.values, name=category), row=1, col=i+1)
        fig_5.update_layout(height=400, width=800)
        st.plotly_chart(fig_5)
    elif chart_type== 'Pie Chart':
        st.subheader("Sentiment Proportion Per Category")
        fig_6 = make_subplots(rows=1, cols=len(choice), specs=[[{'type': 'domain'}] * len(choice)], subplot_titles=choice)
        for i, category in enumerate(choice):
            cat_data = selected_data.query('category == @category')[['category', 'sentiment']]
            sentiment_count = cat_data['sentiment'].value_counts()
            fig_6.add_trace(go.Pie(labels=sentiment_count.index, values=sentiment_count.values, name=category), row=1, col=i+1)
        fig_6.update_layout(height=400, width=800)
        st.plotly_chart(fig_6)


st.sidebar.header('Word Cloud')   
word_sentiment = st.sidebar.radio('Display word cloud for what sentiment?', ('positive', 'neutral', 'negative')) 

@st.cache_data
def generate_word_cloud(sentiment):
    # Filter comments based on sentiment and combine them into a single string
    df = data_with_review.query('sentiment == @sentiment')[['comments']]
    words = ' '.join(df['comments'].dropna())  # Drop NaN values before joining
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', width=700, height=600).generate(words)
    return wordcloud

if not st.sidebar.checkbox("Hide Chart", True, key='30'):
    st.subheader(f'Word cloud for {word_sentiment.capitalize()} Sentiment')
    wordcloud = generate_word_cloud(word_sentiment)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')  # Remove axis
    
    
    st.pyplot(fig)
    
    
