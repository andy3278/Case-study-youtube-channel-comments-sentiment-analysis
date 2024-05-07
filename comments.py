import os


from googleapiclient.discovery import build
from dotenv import load_dotenv
import logging
import sys

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

load_dotenv()

apiKey = os.getenv("api_key")
def get_comments(video_id: str) -> list:
    youtube = build('youtube','v3',
                    developerKey=apiKey)

    # retrieve youtube video results
    video_response=youtube.commentThreads().list(
        part='snippet,replies',
        videoId=video_id
    ).execute()

    comments = []

    # loop through video results
    while video_response:
        for item in video_response['items']:
            # extract comment
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        # since response is limited, we need next page token to get the more comments
        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                pageToken=video_response['nextPageToken']
            ).execute()
        else:
            break
    return comments

id = "e2refaykZgs"

# cleaning
# You may need to download these nltk resources if you haven't already
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')


def clean_text(text: str) -> str:
    text = text.lower()
    text = "".join([char for char in text if char not in string.punctuation])
    words = nltk.word_tokenize(text)
    words = [word for word in words if "https" not in word]
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    return " ".join(words)
# detect language and remove non-english comments

from langdetect import detect

def filter_comments(comments: list) -> list:
    english_comments = []
    for comment in comments:
        try:
            if detect(comment) == 'en':
                english_comments.append(comment)
        except:
            pass
    return english_comments

comments = get_comments(id)
print(f"Number of comments: {len(comments)}")

english_comments = filter_comments(comments)
cleaned_comments = [clean_text(comment) for comment in english_comments]
print(f"Number of English comments after cleaning: {len(cleaned_comments)}")
print(cleaned_comments[:5])

# ploarity score 

from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

sid = SentimentIntensityAnalyzer()

def polarity_score(text: str) -> float:
    return sid.polarity_scores(text)['compound']

polarity_scores = [polarity_score(comment) for comment in cleaned_comments]
overall_score = sum(polarity_scores) / len(polarity_scores)
print(f"Overall sentiment score: {overall_score}")