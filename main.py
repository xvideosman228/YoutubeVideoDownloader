import sys
import re
from pprint import pprint
import json
from io import BytesIO
import humanize
import requests
import yt_dlp
from PIL import Image
import ffmpeg

from PyQt6 import QtWidgets
from PyQt6.QtGui import QImage, QPixmap

import foundMenu
import startMenu
import formatsMenu
import downloadMenu


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
            'outtmpl': '%(title)s',
            'overwrites': True,
            'progress_hooks': [lambda d: FormatsMenu.updateProgress(formats, d)],
            'writethumbnail': True
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

            },
            {
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False
            }],
            'outtmpl': '%(title)s',
            'writethumbnail': True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError:
                print(f"Ошибка скачивания {url}")


class StartMenu(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = startMenu.Ui_YoutubeDownloader()
        self.ui.setupUi(self)
        self.ui.downloadButton.clicked.connect(self.found)

    def found(self):
        if self.ui.address.text() == '':
            QtWidgets.QMessageBox.warning(self, 'ахтунг', f'Введи хоть какую-то ссылку')
            return
        elif not(re.match("^(http(s)??\:\/\/)?(www\.)?((youtube\.com\/watch\?v=)|(youtu.be\/))([a-zA-Z0-9\-_])+" ,self.ui.address.text())):
            QtWidgets.QMessageBox.warning(self, 'ахтунг', f'Введи ютубовскую ссылку')
            return

        self.data = YoutubeDownloader.GetVideoInfo(self.ui.address.text())

        self.title = self.data["title"]
        self.thumbnail_link = self.data["thumbnail"]



        '''
        likes = data["like_count"]
        views = data["view_count"]
        duration = data["duration"]
        timestamp = data["timestamp"]
        duration = data["duration_string"]
        '''

        self.thumbnail = YoutubeDownloader.DownloadThumbnail(self.thumbnail_link, self.data['title'])
        self.thumbnail = QPixmap(self.thumbnail)

        found.ui.videoTitle.setText(self.title)
        found.ui.label_3.setPixmap(self.thumbnail)

        start.close()
        formats.url = self.ui.address.text()
        formats.show()




class FoundMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = foundMenu.Ui_Form()
        self.ui.setupUi(self)

class DownloadMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = downloadMenu.Ui_Form()
        self.ui.setupUi(self)




class FormatsMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = formatsMenu.Ui_Form()
        self.ui.setupUi(self)
        self.url = ''
        self.format_dict = {
            'type': None,
            'quality': None,
            'format': None
        }

        self.translations = {
            'type': "Тип",
            'quality': "Качество",
            'format': "Формат"
        }

        self.ui.videoRadioButton.clicked.connect(self.video)
        self.ui.audioRadioButton.clicked.connect(self.audio)

        self.videoQualityButtons = [
            self.ui.radio144,
            self.ui.radio240,
            self.ui.radio360,
            self.ui.radio480,
            self.ui.radio720,
            self.ui.radio1080,
            self.ui.radio1440,
            self.ui.radio2160,
                        ]

        self.videoFormatsButtons = [
            self.ui.radioMP4,
            self.ui.radioWEBM,
        ]

        self.audioFormatsButtons = [
            self.ui.radioMP3,
            self.ui.radioWAV
        ]

        self.audioQualityButtons = [
            self.ui.audioRadio64,
            self.ui.audioRadio128,
            self.ui.audioRadio256,
            self.ui.audioRadio192
        ]

        self.ui.radio2160.clicked.connect(lambda: (self.quality(2160), self.video))
        self.ui.radio1440.clicked.connect(lambda: (self.quality(1440), self.video))
        self.ui.radio1080.clicked.connect(lambda: (self.quality(1080), self.video))
        self.ui.radio720.clicked.connect(lambda: (self.quality(720), self.video))
        self.ui.radio480.clicked.connect(lambda: (self.quality(480), self.video))
        self.ui.radio360.clicked.connect(lambda: (self.quality(360), self.video))
        self.ui.radio240.clicked.connect(lambda: (self.quality(240), self.video))
        self.ui.radio144.clicked.connect(lambda: (self.quality(144), self.video))

        self.ui.radioMP4.clicked.connect(lambda: (self.format('mp4'), self.video))
        self.ui.radioWEBM.clicked.connect(lambda: (self.format('webm'), self.video))

        self.ui.audioRadio192.clicked.connect(lambda: (self.quality(192), self.audio))
        self.ui.audioRadio128.clicked.connect(lambda: (self.quality(128), self.audio))
        self.ui.audioRadio64.clicked.connect(lambda: (self.quality(64), self.audio))
        self.ui.audioRadio256.clicked.connect(lambda: (self.quality(256), self.audio))

        self.ui.radioMP3.clicked.connect(lambda: (self.format('mp3'), self.audio))
        self.ui.radioWAV.clicked.connect(lambda: (self.format('wav'), self.audio))

        self.ui.downloadButton.clicked.connect(self.checkFields)

    def updateProgress(self, d:dict):
        self.ui.progressBar.setValue(int(d['_percent']))
        print(d['_percent'])


    def video(self):
        for radio in self.audioQualityButtons:
            radio.setEnabled(False)
            #self.format_dict['quality'] = None
        for radio in self.audioFormatsButtons:
            radio.setEnabled(False)
            #self.format_dict['format'] = None

        for radio in self.videoQualityButtons:
            radio.setEnabled(True)
        for radio in self.videoFormatsButtons:
            radio.setEnabled(True)


        for x in self.format_dict:
            self.format_dict[x] = None

        self.ui.audioRadioButton.setChecked(False)
        self.format_dict['type'] = 'video'

    def checkFields(self):
        unchecked = []
        for x in self.format_dict:
            if self.format_dict[x] is None:
                unchecked.append(self.translations[x])
        if not unchecked:
            pprint(self.format_dict)
            if self.format_dict['type'] == 'video':
                ...
                YoutubeDownloader.DownloadVideo(self.url, self.format_dict["quality"], self.format_dict["format"])

            elif self.format_dict['type'] == 'audio':
                ...
                YoutubeDownloader.DownloadAudio(self.url, self.format_dict["quality"], self.format_dict["format"])
        else:
            QtWidgets.QMessageBox.warning(self, 'ахтунг', f'Не добавлены поля {", ".join(unchecked)}')


    def audio(self):
        for radio in self.videoQualityButtons:
            radio.setEnabled(False)
            self.format_dict['quality'] = None
        for radio in self.videoFormatsButtons:
            radio.setEnabled(False)
            self.format_dict['format'] = None

        for radio in self.audioQualityButtons:
            radio.setEnabled(True)
        for radio in self.audioFormatsButtons:
            radio.setEnabled(True)

        self.ui.videoRadioButton.setChecked(False)
        self.format_dict['type'] = 'audio'

    def quality(self, quality: int):
        self.format_dict['quality'] = quality

    def format(self, format_: str):
        self.format_dict['format'] = format_



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    start = StartMenu()
    found = FoundMenu()
    formats = FormatsMenu()
    download = DownloadMenu()

    start.show()
    sys.exit(app.exec())