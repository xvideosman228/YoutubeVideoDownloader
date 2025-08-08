import json
from pprint import pprint

import yt_dlp

playlist_url = 'https://www.youtube.com/watch?v=w6-6XHnmFtI&list=OLAK5uy_nBSbfYLKH_2c6COOTd0nlj8ilv-HE03CI'

ytdl_opts = {
    'proxy': 'socks5://0.0.0.0:14228',
    'extract_flat': 'in_playlist',

}

with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
    data = ydl.extract_info(playlist_url, download=False)
    print(f'==={data['title']}===')
    with open('playlist.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    for video in data['entries']:
        print(f'{video['title']} == {video['url']}')