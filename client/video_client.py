import os
import requests


def UploadVideo(server_url: str, video_path: str, company_name: str) -> str:
    """Uploads a video file to the server and returns its URL."""
    url = f"{server_url.rstrip('/')}/upload"
    filename = os.path.basename(video_path)

    with open(video_path, "rb") as file_obj:
        files = {"file": (filename, file_obj)}
        data = {"company_name": company_name}
        response = requests.post(url, files=files, data=data, timeout=60)

    response.raise_for_status()
    return response.json()["video_url"]


def GetVideoURL(server_url: str, company_name: str) -> str:
    """Returns the video URL for the given company name."""
    url = f"{server_url.rstrip('/')}/get_video_url"
    response = requests.get(url, params={"company_name": company_name}, timeout=30)

    response.raise_for_status()
    return response.json()["video_url"]
