import os


from googleapiclient.discovery import build
from dotenv import load_dotenv
import logging
import sys
load_dotenv()

apiKey = os.getenv("api_key")
def get_comments(video_id):
    youtube = build('youtube','v3',
                    developerKey=apiKey)

    # retrieve youtube video results
    video_response=youtube.commentThreads().list(
        part='snippet,replies',
        videoId=video_id
    ).execute()

    comments = []

    while video_response:
        for item in video_response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

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

print(get_comments(id))