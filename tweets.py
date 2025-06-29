import streamlit as st
from transformers import logging, AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import tweepy
import os

logging.set_verbosity_error()


client = tweepy.Client(bearer_token=st.secrets["BEARER_TOKEN"])

roberta = 'cardiffnlp/twitter-roberta-base-sentiment'
tokenizer = AutoTokenizer.from_pretrained(roberta)
model = AutoModelForSequenceClassification.from_pretrained(roberta)
labels = ['Negative', 'Neutral', 'Positive']

def preprocess(tweet):
    tweet_words = []
    for i in tweet.split(' '):
        if i.startswith('@') and len(i) > 1:
            i = '@user'
        elif i.startswith('#'):
            i = i[1:]
        elif i.startswith('http'):
            i = 'http'
        tweet_words.append(i)
    return ' '.join(tweet_words)

st.title("Twitter Sentiment Analysis 🌟")

query = st.text_input("Enter your search query (example: AI innovation)")

max_results = st.slider("Number of tweets to analyze:", min_value=5, max_value=50, value=10, step=5)

if st.button("Analyze"):
    if query.strip() == "":
        st.warning("Please enter a valid query.")
    else:
        try:
            tweets = client.search_recent_tweets(query=query, max_results=max_results)
            if tweets.data:
                for tweet in tweets.data:
                    text = preprocess(tweet.text)
                    encoded = tokenizer(text, return_tensors='pt')
                    output = model(**encoded)
                    scores = softmax(output.logits.detach().numpy()[0])
                    sentiment = labels[scores.argmax()]
                    st.write(f"**Tweet:** {tweet.text}")
                    st.write(f"**Sentiment:** "f"{sentiment}")
                    st.markdown("---")
            else:
                st.info("No tweets found for this query.")
        except tweepy.TooManyRequests:
            st.warning("Twitter API rate limit exceeded. Please try again later.")
        except Exception as e:
            st.error(f"Error fetching or processing tweets: {e}")