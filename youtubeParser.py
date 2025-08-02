import json
from io import BytesIO
import humanize
import requests
import yt_dlp
from PIL import Image

from collections import defaultdict

class YoutubeDownloader:
    @staticmethod
    def GetVideoInfo(url: str):
        opts = {'proxy': 'socks5://0.0.0.0:14228'}
        with yt_dlp.YoutubeDL(opts) as ydl, open('file.json', 'w', encoding='utf-8') as f:
            info = ydl.extract_info(url, download=False)
            ydl.sanitize_info(info)
            json.dump(info, f, indent=4, ensure_ascii=False)
        return info

    @staticmethod
    def DownloadThumbnail(url: str, name: str):
        proxies = {
            'http': 'socks5://0.0.0.0:14228',
            'https': 'socks5://0.0.0.0:14228'
        }

        response = requests.get(url, proxies=proxies)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image = image.resize([720,405])
            image.save(f'{name}.png')
        else:
            print(f'Ошибка: {response.status_code}')

        return name

    @staticmethod
    def DownloadVideo(url: str, quality: int, resolution: str):
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',  # прокси-сервер
            'format': f'bestvideo[ext={resolution}][height={quality}]+bestaudio/best',
            'merge_output_format': resolution,
            'outtmpl': '%(title)s'
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError:
                print("Ошибка скачивания")

    @staticmethod
    def DownloadAudio(url: str, quality: int, resolution: str):
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',
            'format': f'bestaudio/best[audio_bitrate={quality}k]',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': resolution,
                'preferredquality': str(quality),
            }],
            'outtmpl': '%(title)s',
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError:
                print(f"Ошибка скачивания {url}")

