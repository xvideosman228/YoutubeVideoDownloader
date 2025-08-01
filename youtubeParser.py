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
    def DownloadVideo(quality: int, url: str):
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',
            'format': f'bv*[height={quality}]+ba'
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download(url)
            except yt_dlp.utils.DownloadError:
                print('fuck')

    @staticmethod
    def DownloadAudio(quality: int, url: str):
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',
            'format': f'worstaudio/worst[ext=mp3][abr={quality}]'
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download(url)
            except yt_dlp.utils.DownloadError:
                print('fuck')

