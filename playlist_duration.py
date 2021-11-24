import re
import os
from googleapiclient.discovery import build
from datetime import timedelta

api_key = os.environ.get('Youtube API Key')

youtube = build('youtube', 'v3', developerKey=api_key)

hours_patterns = re.compile(r'(\d+)H')
minutes_pattern = re.compile(r'(\d+)M')
seconds_patterns = re.compile(r'(\d+)S')

total_video_seconds = 0

nextPageToken = None


def print_playlist_duration(total_video_seconds: int) -> None:
    minutes, seconds = divmod(total_video_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    print(f"{hours} hours, {minutes} minutes and {seconds} seconds")


def get_api_playlist_response(playlist_id=None, max_results=50) -> dict:
    """Sends youtube api request to receive playlist information based on it's id"""

    playlist_request = youtube.playlistItems().list(part='contentDetails',
                                                    playlistId=playlist_id,
                                                    maxResults=max_results,
                                                    pageToken=nextPageToken)
    playlist_response = playlist_request.execute()

    return playlist_response


def get_video_ids(playlist_response) -> str:
    """"Gets video ids from playlist response"""

    video_ids = [item['contentDetails']['videoId'] for item in playlist_response.get('items')]
    video_ids_string = ','.join(video_ids)

    return video_ids_string


def get_api_video_response(playlist_id=None) -> dict:
    """"Sends youtube api request to receive video information based on it's id or ids,
        using this response we can get duration of the video/videos"""

    playlist_response = get_api_playlist_response(playlist_id)
    video_request = youtube.videos().list(part='contentDetails', id=get_video_ids(playlist_response))

    video_response = video_request.execute()

    return video_response


def get_only_numbers(duration):
    hours = hours_patterns.search(duration)
    minutes = minutes_pattern.search(duration)
    seconds = seconds_patterns.search(duration)

    hours = int(hours.group(1)) if hours else 0
    minutes = int(minutes.group(1)) if minutes else 0
    seconds = int(seconds.group(1)) if seconds else 0

    return hours, minutes, seconds


while True:
    if not nextPageToken:
        playlist_id = input("Enter playlist id to receive it's duration: ")
    for item in get_api_video_response(playlist_id).get('items'):
        duration = item['contentDetails']['duration']

        hours, minutes, seconds = get_only_numbers(duration)
        total_seconds = timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()

        total_video_seconds += int(total_seconds)

    nextPageToken = get_api_playlist_response(playlist_id).get('nextPageToken')

    if not nextPageToken:
        break

print_playlist_duration(total_video_seconds)
