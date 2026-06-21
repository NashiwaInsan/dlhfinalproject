```python
import pandas as pd
from pathlib import Path

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download sekali saja
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except:
    nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()


def classify_sentiment(text):

    score = sia.polarity_scores(
        str(text)
    )

    compound = score["compound"]

    confidence = round(
        abs(compound),
        4
    )

    if compound >= 0.05:

        return pd.Series([
            "POSITIVE",
            confidence
        ])

    elif compound <= -0.05:

        return pd.Series([
            "NEGATIVE",
            confidence
        ])

    else:

        return pd.Series([
            "NEUTRAL",
            confidence
        ])


def sentiment_reviews():

    input_file = (
        "lake/silver/reviews/"
        "reviews_clean.parquet"
    )

    if not Path(
        input_file
    ).exists():

        print(
            "reviews_clean.parquet tidak ditemukan"
        )

        return

    df = pd.read_parquet(
        input_file
    )

    df[
        [
            "SentimentLabel",
            "SentimentConfidence"
        ]
    ] = df["review_text"].apply(
        classify_sentiment
    )

    output_file = (
        "lake/silver/reviews/"
        "reviews_sentiment.parquet"
    )

    df.to_parquet(
        output_file,
        index=False
    )

    print(
        "Sentiment analysis selesai"
    )

    print(
        df[
            [
                "review_text",
                "SentimentLabel",
                "SentimentConfidence"
            ]
        ].head()
    )
```
