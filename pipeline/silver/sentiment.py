# import nltk
# nltk.download("vader_lexicon")
# Jalankan Sekali

import pandas as pd

from nltk.sentiment import (
    SentimentIntensityAnalyzer
)

sia = SentimentIntensityAnalyzer()


def get_sentiment(text):

    score = sia.polarity_scores(
        str(text)
    )

    compound = score["compound"]

    if compound >= 0.05:
        return "Positive"

    if compound <= -0.05:
        return "Negative"

    return "Neutral"


def sentiment_reviews():

    df = pd.read_parquet(
        "lake/silver/reviews/reviews_clean.parquet"
    )

    df["sentiment"] = df[
        "review_text"
    ].apply(
        get_sentiment
    )

    df.to_parquet(
        "lake/silver/reviews/reviews_sentiment.parquet",
        index=False
    )

    print(
        "Sentiment analysis selesai"
    )