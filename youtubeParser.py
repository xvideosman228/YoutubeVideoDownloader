import json
from io import BytesIO

import requests
import wget
import yt_dlp
from PIL import Image


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

        # Загрузка изображения через SOCKS5 прокси
        response = requests.get(url, proxies=proxies)

        # Проверка успешности запроса
        if response.status_code == 200:
            # Открытие изображения из байтов
            image = Image.open(BytesIO(response.content))
            image = image.resize([720,405])
            # Сохранение изображения
            image.save(f'{name}.png')
        else:
            print(f'Ошибка при скачивании изображения: {response.status_code}')

        return name