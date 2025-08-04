import os
import subprocess
import sys
import re
import datetime
from pprint import pprint
import json
from io import BytesIO
import humanize
import requests
import yt_dlp
from PIL import Image

from PyQt6 import QtWidgets
from PyQt6.QtGui import QPixmap, QDesktopServices

import completedWindow
import foundMenu
import startMenu
import formatsMenu
import downloadMenu

humanize.i18n.activate("ru_RU")

class YoutubeDownloader:
    @staticmethod
    def GetVideoInfo(url: str):
        try:
            opts = {
                'proxy': 'socks5://0.0.0.0:14228'
            }
            with yt_dlp.YoutubeDL(opts) as ydl, open('file.json', 'w', encoding='utf-8') as f:
                info = ydl.extract_info(url, download=False)
                ydl.sanitize_info(info)
                json.dump(info, f, indent=4, ensure_ascii=False)
            return info
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, 'ахтунг', f'{e}')
            print(e)

    @staticmethod
    def DownloadThumbnail(url: str, name: str):
        try:
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
        except FileNotFoundError:
            return None

    @staticmethod
    def DownloadVideo(url: str, quality: int, resolution: str, output: str):
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',  # прокси-сервер
            'format': f'bestvideo[ext={resolution}][height={quality}]+bestaudio/best',
            'merge_output_format': resolution,
            'outtmpl': output,
            'overwrites': True,
            'progress_hooks': [lambda d: formats.updateProgress(d)]
            #'writethumbnail': True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError:
                QtWidgets.QMessageBox.warning(None, 'ахтунг', f'Ошибка скачивания {url}')

    @staticmethod
    def DownloadAudio(url: str, quality: int, resolution: str, output: str):
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',
            'format': f'bestaudio/best[audio_bitrate={quality}k]',
            'progress_hooks': [lambda d: formats.updateProgress(d)],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': resolution,
                'preferredquality': str(quality),

            },
            {
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False
            }],
            'outtmpl': output,
            'writethumbnail': True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError:
                QtWidgets.QMessageBox.warning(None, 'ахтунг', f'Ошибка скачивания {url}')

class CompletedWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = completedWindow.Ui_Form()
        self.ui.setupUi(self)

class StartMenu(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = startMenu.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.downloadButton.clicked.connect(self.found)


    def found(self):
        if self.ui.address.text() == '':
            QtWidgets.QMessageBox.warning(self, 'ахтунг', f'Введи хоть что-то')
            self.ui.address.setText('')
            return

        elif not(re.match(r'https://.*' ,self.ui.address.text())):
            if not(re.match('www\..*', self.ui.address.text())):
                QtWidgets.QMessageBox.warning(self, 'ахтунг', f'Введи ссылку')
                self.ui.address.setText('')
                return
            else:
                pass



        self.data = YoutubeDownloader.GetVideoInfo(self.ui.address.text())

        self.title = self.data["title"]
        self.thumbnail_link = self.data["thumbnail"]


        formats.metadata['title'] = self.title




        likes = self.data["like_count"]
        views = self.data["view_count"]
        duration = self.data["duration_string"]
        timestamp = self.data["timestamp"]
        #duration = self.data["duration_string"]

        text = f'''Просмотры - {humanize.intword(views)}
Лайки - {humanize.intword(likes)}
Продолжительность - {duration}
Дата публикации - {humanize.naturaltime(datetime.datetime.fromtimestamp(timestamp))}
'''
        found.ui.videoData.setText(text)
        self.thumbnail_image = YoutubeDownloader.DownloadThumbnail(self.thumbnail_link, self.data['title'])
        found.ui.videoTitle.setText(self.title)
        found.setWindowTitle(f'{self.title} - Youtube Downloader')
        formats.url = self.ui.address.text()

        if self.thumbnail_image is not None:
            self.thumbnail = QPixmap(self.thumbnail_image)
            found.ui.label_3.setPixmap(self.thumbnail)
            found.show()
            start.hide()

            os.remove(f'{self.thumbnail_image}.png')
        else:
            found.show()

        self.title = ''
        self.thumbnail_link = ''
        self.thumbnail_image = ''
        self.thumbnail = ''
        self.data = {}

        start.hide()

class FoundMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = foundMenu.Ui_Form()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.formats)

    def formats(self):
        self.close()
        formats.show()

class DownloadMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = downloadMenu.Ui_Form()
        self.ui.setupUi(self)


def mainMenu():
    print("Restarting program...")
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit(0)




class FormatsMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = formatsMenu.Ui_Form()
        self.ui.setupUi(self)
        self.url = ''
        self.format_dict = {
            'type': None,
            'quality': None,
            'format': None,
        }
        self.metadata = {
            'title': None
        }

        self.translations = {
            'type': "Тип",
            'quality': "Качество",
            'format': "Формат"
        }

        self.ui.videoRadioButton.clicked.connect(self.video)
        self.ui.audioRadioButton.clicked.connect(self.audio)
        self.ui.gifRadioButton.clicked.connect(self.gif)

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

        self.ui.radioMP3.clicked.connect(lambda: (self.format('mp3'), self.audio))
        self.ui.radioWAV.clicked.connect(lambda: (self.format('wav'), self.audio))

        self.ui.downloadButton.clicked.connect(self.checkFields)





    def updateProgress(self, d: dict):
        if d['status'] == 'downloading':
            #delta = datetime.timedelta(seconds=d['eta'])
            #self.ui.timeLeft.setText(humanize.naturaldelta(delta))
            #size = humanize.naturalsize(d['downloaded_bytes'])
            #self.ui.downloaded.setText(f'{size} из ')
            with open('asofasadsofd.json', 'w', encoding='utf-8') as f:
                json.dump(d, f, indent=4, ensure_ascii=False)
            self.ui.progressBar.setValue(int(d['_percent']))

    def gif(self):
        for radio in self.audioQualityButtons:
            radio.setEnabled(False)
            #self.format_dict['quality'] = None
        for radio in self.audioFormatsButtons:
            radio.setEnabled(False)
            #self.format_dict['format'] = None

        for radio in self.videoQualityButtons:
            radio.setEnabled(False)
            self.format_dict['quality'] = None
        for radio in self.videoFormatsButtons:
            radio.setEnabled(False)
            self.format_dict['format'] = None

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

    def createMsg(self):
        _translations = {'video': "Видео", 'audio': "Аудио"}
        _title = _translations[self.format_dict['type']]
        self.completed.ui.label.setText(f'{_title} было скачано')
        self.completed.ui.mainMenu.clicked.connect(mainMenu)
        self.completed.show()

    def checkFields(self):
        unchecked = []
        for x in self.format_dict:
            if self.format_dict[x] is None:
                unchecked.append(self.translations[x])


        if not unchecked:
            pprint(self.format_dict)
            self.completed = CompletedWindow()
            if self.format_dict['type'] == 'video':
                filename = QtWidgets.QFileDialog.getSaveFileName(self, 'сохрани файл',
                    f"~/{self.metadata['title']}.{self.format_dict['format']}", "Видео (*.mp4, *.webm)")
                if filename[0] == '':
                    QtWidgets.QMessageBox.warning(self, 'ахтунг', 'Введи хоть какое-то имя файла')
                else:
                    YoutubeDownloader.DownloadVideo(self.url, self.format_dict["quality"], self.format_dict["format"], filename[0])
                    #QtWidgets.QMessageBox.information(self, 'скачано', 'Видео скачано')

            elif self.format_dict['type'] == 'audio':
                filename = QtWidgets.QFileDialog.getSaveFileName(self, 'сохрани файл',
                                                                 f"~/{self.metadata['title']}.{self.format_dict['format']}",
                                                                 "Аудио (*.mp3)")
                YoutubeDownloader.DownloadAudio(self.url, self.format_dict["quality"], self.format_dict["format"],
                                                filename[0])

        else:
            QtWidgets.QMessageBox.warning(self, 'ахтунг', f'Не добавлены поля {", ".join(unchecked)}')
        self.createMsg()
        self.ui.progressBar.setValue(0)

    def audio(self):
        for radio in self.videoQualityButtons:
            radio.setEnabled(False)
        for radio in self.videoFormatsButtons:
            radio.setEnabled(False)

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