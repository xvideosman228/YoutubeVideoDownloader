import json
from pprint import pprint

import yt_dlp
from typing import List

class YoutubeDownloader:
    @staticmethod
    def GetChannelVideos(channel_url: str) -> List[str]:
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',
            'extract_flat': True,
            'ignoreerrors': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            result = {}
            result['videos'] = [{'title': x['title'], 'url': x['url']} for x in info['entries']]
            result['title'] = info['channel']
            with open('channel.json', 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)
        return result
pprint(YoutubeDownloader.GetChannelVideos('https://www.youtube.com/@SHAPKA99'))