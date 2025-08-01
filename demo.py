import yt_dlp
from math import ceil


def bytes_to_mb(bytes):
    return round(bytes / (1024 * 1024))


# URL вашего видео на YouTube
video_url = 'https://youtu.be/z0wK6s-6cbo?si=bnNta5oS9UKb2EAh'

ytdl_opts = {
    # Скачать метаданные, но само видео не загружать
    'skip_download': True,
    'proxy': 'socks5://0.0.0.0:14228'
}

with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
    info_dict = ydl.extract_info(video_url, download=False)

    formats = []
    desired_resolutions = ['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p']

    if 'formats' in info_dict:
        video_duration_seconds = float(info_dict.get('duration', 0))  # продолжительность видео в секундах

        for fmt in info_dict['formats']:
            resolution = fmt.get('resolution')

            # Выбираем интересующий формат по разрешению
            if any(res in resolution for res in desired_resolutions):
                avg_bitrate_kbps = int(fmt.get('abr', 0)) + int(fmt.get('asr', 0))  # усреднённый битрейт (аудио+видео)

                # Предположительно рассчитываем размер файла в мегабайтах
                file_size_bytes = ceil((avg_bitrate_kbps * video_duration_seconds) / 8)
                file_size_mb = bytes_to_mb(file_size_bytes)

                formats.append({
                    'format_id': fmt['format_id'],
                    'resolution': resolution,
                    'filesize': f'{file_size_mb:.2f} MB',
                    'vcodec': fmt.get('vcodec'),
                    'acodec': fmt.get('acodec'),
                })

        if formats:
            print("\\nДоступные форматы и размеры файлов:\\n")
            for fmt in formats:
                print(
                    f"{fmt['format_id']}: {fmt['resolution']} | {fmt['filesize']} | {fmt['vcodec']}/{fmt['acodec']}\\n")
        else:
            print("Желаемые форматы не обнаружены.")
    else:
        print("Форматы не найдены.")