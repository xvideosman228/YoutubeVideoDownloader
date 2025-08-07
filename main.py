import os
import queue
import sys
import re
import datetime
import time
from pprint import pprint
import json
from io import BytesIO

import humanize
import requests
import yt_dlp
from PIL import Image

from PyQt6 import QtWidgets
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtWidgets import QDialog

import completedWindow
import foundMenu
import startMenu
import formatsMenu
import downloadMenu
import videoshorts
import filtersMenu

import addFormat
import addURL

class YoutubeDownloader:
    @staticmethod
    def GetChannelVideos(channel_url: str):
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',
            'match_filter': lambda dic: print(dic),
            'extract_flat': True,
            'ignoreerrors': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            result = {}
            try:
                result['videos'] = [{'title': x['title'], 'url': x['url']} for x in info['entries']]

            except KeyError:
                # затычка на время
                channel_url += '/videos/'
                info = ydl.extract_info(channel_url, download=False)
                result['videos'] = [{'title': x['title'], 'url': x['url'], 'duration': x['duration']} for x in info['entries']]
            finally:
                result['videos'] = result['videos']
                result['title'] = info['channel']


            for index, video in enumerate(result['videos']):
                print(video)
                video['index'] = index

            with open('channel.json', 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)
        return result

    @staticmethod
    def GetVideoInfo(url: str):
        try:
            opts = {
                'proxy': 'socks5://0.0.0.0:14228',
                'retries': 3,
                'socket_timeout': 10,
                'ignoreerrors': True
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                ydl.sanitize_info(info)
                '''with open('file.json', 'w', encoding='utf-8') as f:
                    json.dump(info, f, indent=4, ensure_ascii=False)
                '''
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
    def DownloadVideoFromChannel(url: str, quality: int, resolution: str, output: str, index: int):
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',  # прокси-сервер
            'format': f'bestvideo[ext={resolution}][height={quality}]+bestaudio/best',
            'merge_output_format': resolution,
            'outtmpl': output,
            'overwrites': True,
            'progress_hooks': [lambda d: start.updateProgressChannel(d, index)]
            # 'writethumbnail': True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError:
                QtWidgets.QMessageBox.warning(None, 'ахтунг', f'Ошибка скачивания {url}')
                start.ui.channelTableVideos.setItem(index, 2, "Ошибка")

    @staticmethod
    def DownloadVideoQueue(url: str, quality: int, resolution: str, output: str, index: int):
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',
            'format': f'bestvideo[ext={resolution}][height={quality}]+bestaudio/best',
            'merge_output_format': resolution,
            'outtmpl': output,
            'overwrites': True,
            'progress_hooks': [lambda d: start.updateProgress(d, index)]
            # 'writethumbnail': True
        }

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError:
                QtWidgets.QMessageBox.warning(None, 'ахтунг', f'Ошибка скачивания {url}')


    @staticmethod
    def DownloadAudioQueue(url: str, quality: int, resolution: str, output: str, index: int):
        opts = {
            'proxy': 'socks5://0.0.0.0:14228',
            'format': f'bestaudio/best[audio_bitrate={quality}k]',
            'progress_hooks': [lambda d: start.updateProgress(d, index)],
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


class VideoShorts(QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = videoshorts.Ui_Dialog()
        self.ui.setupUi(self)
        self.response = ''
        self.ui.downloadVideo.clicked.connect(self.downloadVideo)
        self.ui.downloadShorts.clicked.connect(self.downloadShorts)
        self.ui.downloadAll.clicked.connect(self.downloadAll)

    def downloadVideo(self):
        self.close()
        self.response = 'video'


    def downloadShorts(self):
        self.close()
        self.response = 'shorts'



    def downloadAll(self):
        self.close()
        self.response = 'all'





class CompletedWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = completedWindow.Ui_Form()
        self.ui.setupUi(self)

class FiltersWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = filtersMenu.Ui_Form()
        self.ui.setupUi(self)

class AddURL(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = addURL.Ui_Form()
        self.ui.setupUi(self)

class AddFormat(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = addFormat.Ui_Form()
        self.ui.setupUi(self)

class StartMenu(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = startMenu.Ui_MainWindow()
        self.ui.setupUi(self)
        self.videoQueue = queue.SimpleQueue()

        self._filters = {}
        self._channel_video = {}
        self.completed = CompletedWindow()

        self._max_length_video_channel = 0.0
        self._videos_count = 0

        self.ui.downloadButton.clicked.connect(self.found)
        self.ui.addVideoToQueueButton.clicked.connect(self.addVideo)
        self.ui.downloadAllQueueButton.clicked.connect(self.downloadVideoQueue)
        self.ui.findChannelButton.clicked.connect(self.extractVideosFromChannel)
        self.ui.downloadChannelButton.clicked.connect(self.downloadVideosFromChannel)
        self.ui.filterButton.clicked.connect(self.setFilters)


        self.new_video = {
            'index': 0,
            'url': None,
            'filename': None,
            'format': {}
        }
        self.index = 0
        self.ui.tableWidget.setRowCount(self.index)


    def checkLink(self):
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

    def found(self):
        self.checkLink()

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

    def extractVideosFromChannel(self):
        url = self.ui.channelURL.text().strip()
        videos = YoutubeDownloader.GetChannelVideos(url)
        if videos is None:
            QtWidgets.QMessageBox.warning(self, 'ахтунг', 'Не получилось достать видео')
            return
        self._videos_count = len(videos['videos'])
        channel_title = videos['title']
        self._max_length_video_channel = max([x['duration'] for x in videos['videos']])
        print(self._max_length_video_channel)



        for video in videos['videos']:
            title = video['title']
            url = video['url']
            self.ui.channelTableVideos.insertRow(video['index'])

            self.ui.channelTableVideos.setItem(video['index'], 0, QtWidgets.QTableWidgetItem(title))
            self.ui.channelTableVideos.setItem(video['index'], 1, QtWidgets.QTableWidgetItem(url))
            self.ui.channelTableVideos.setItem(video['index'], 2, QtWidgets.QTableWidgetItem('Простаивает'))
            self.ui.channelTableVideos.setItem(video['index'], 3, QtWidgets.QTableWidgetItem('Не скачивается'))
            self.ui.channelTableVideos.setItem(video['index'], 4, QtWidgets.QTableWidgetItem('Не скачивается'))
            QtWidgets.QApplication.processEvents()

        self._channel_video = videos
        pprint(self._channel_video)

    def downloadVideosFromChannel(self):
        if self._channel_video:
            for video in self._channel_video['videos']:
                self.ui.channelTableVideos.setItem(video['index'] , 2, QtWidgets.QTableWidgetItem('На очереди'))
                QtWidgets.QApplication.processEvents()
                YoutubeDownloader.DownloadVideoFromChannel(video['url'],
                                                720,
                                                'mp4',
                                                f'/home/fedor/PycharmProjects/YTDownloaderPyQt/testChannelVideos/{video['title']}',
                                                video['index'])
        else:
            QtWidgets.QMessageBox.warning(self, 'ахтунг', 'Тут пусто')

    def setFilters(self):
        if not self._videos_count:
            QtWidgets.QMessageBox.warning(self, 'ахтунг', 'Тут нечего фильтровать')
            return
        self.filterWindow = FiltersWindow()
        self.filterWindow.show()
        self.filterWindow.ui.setFilter.clicked.connect(self.applyFilters)
        self.filterWindow.ui.minimalLengthSlider.valueChanged.connect(lambda v: self.filterWindow.ui.minimalLengthLabel.setText(str(humanize.precisedelta(v))))
        self.filterWindow.ui.maximalLengthSlider.valueChanged.connect(lambda v: self.filterWindow.ui.maximalLengthLabel.setText(str(humanize.precisedelta(v))))
        self.filterWindow.ui.minimalLengthSlider.setMaximum(int(self._max_length_video_channel))
        self.filterWindow.ui.maximalLengthSlider.setMaximum(int(self._max_length_video_channel))


    def applyFilters(self):
        if self.filterWindow.ui.minimalLengthSlider.value() > self.filterWindow.ui.maximalLengthSlider.value():
            QtWidgets.QMessageBox.warning(self, 'ахтунг', 'минимальная длина больше максимальной!')
            return
        self._filters['minLength'] = self.filterWindow.ui.minimalLengthSlider.value()
        self._filters['maxLength'] = self.filterWindow.ui.maximalLengthSlider.value()

        print(self._filters)


    def updateProgressChannel(self, d: dict, index: int):
        QtWidgets.QApplication.processEvents()
        with open('p.json', 'w', encoding='utf-8') as f:
            json.dump(d,f,indent=4, ensure_ascii=False)
        if d['status'] == 'downloading':
            percent_str = str(int(d['_percent'])) + '%' + ' загружено'
            #speed_str = str(int(d['speed'])) + '%' + ' загружено'
            #eta_str = str(int(d['eta']))

            self.ui.channelTableVideos.setItem(index, 2, QtWidgets.QTableWidgetItem(percent_str))
            #self.ui.channelTableVideos.setItem(index, 3, QtWidgets.QTableWidgetItem())
            #self.ui.channelTableVideos.setItem(index, 4, QtWidgets.QTableWidgetItem(eta_str))
        elif d['status'] == 'finished':
            self.ui.channelTableVideos.setItem(index, 2, QtWidgets.QTableWidgetItem('Завершен'))

    def addVideo(self):
        addurl.show()
        addurl.ui.nextButton.clicked.connect(self.addTitle)

    def addTitle(self):
        url = addurl.ui.url.text().strip()

        if url:
            self.new_video["url"] = url
            addurl.close()
            addurl.ui.url.setText("")
        elif self.new_video["url"]:
            pass
            return
        else:
            return



        self.metadata = YoutubeDownloader.GetVideoInfo(self.new_video['url'])

        if self.metadata is None:
            QtWidgets.QMessageBox.information(self, 'ахтунг', 'Какая-то хрень вместо ссылки')
            # self.ui.tableWidget.removeRow(self.index)
            return

        self.filename = QtWidgets.QFileDialog.getSaveFileName(self, 'выбери имя файла и куда его сохранить',
                    f"~/{self.metadata['title']}")
        self.filename = self.filename[0]
        if self.filename:
            #self._addFormat()
            self.addFormat()
            addformat.show()
            return
        else:
            self.ui.tableWidget.removeRow(self.index)
            return

    def downloadVideoQueue(self):
        if self.videoQueue.qsize() == 0:
            QtWidgets.QMessageBox.warning(self, 'ахтунг', 'Ты хоть что-то добавь в очередь перед скачиванием')
            return
        for i in range(self.videoQueue.qsize()):
            item = self.videoQueue.get()
            print(item['index'])
            self.ui.tableWidget.setItem(item['index'], 4, QtWidgets.QTableWidgetItem('На очереди'))

            QtWidgets.QApplication.processEvents()
            if item['format']['type'] == 'video':
                YoutubeDownloader.DownloadVideoQueue(
                    url=item['url'],
                    quality=item['format']['quality'],
                    resolution=item['format']['format'],
                    output=item['filename'],
                    index=item['index']
                )
            elif item['format']['type'] == 'audio':
                YoutubeDownloader.DownloadAudioQueue(
                    url=item['url'],
                    quality=item['format']['quality'],
                    resolution=item['format']['format'],
                    output=item['filename'],
                    index=item['index']
                )

        self.createMsg()




    def addFormat(self):
        self.new_video['filename'] = self.filename
        pprint(self.new_video)

        addformat.ui.videoRadioButton.clicked.connect(self.video)
        addformat.ui.audioRadioButton.clicked.connect(self.audio)


        self.format_dict = {
            'type': None,
            'quality': None,
            'format': None,
        }
        self.videoQualityButtons = [
            addformat.ui.radio144,
            addformat.ui.radio240,
            addformat.ui.radio360,
            addformat.ui.radio480,
            addformat.ui.radio720,
            addformat.ui.radio1080,
            addformat.ui.radio1440,
            addformat.ui.radio2160,
        ]
        self.videoFormatsButtons = [
            addformat.ui.radioMP4,
            addformat.ui.radioWEBM,
        ]
        self.audioFormatsButtons = [
            addformat.ui.radioMP3,
            addformat.ui.radioWAV
        ]
        self.audioQualityButtons = [
            addformat.ui.audioRadio64,
            addformat.ui.audioRadio128,
            addformat.ui.audioRadio192
        ]



        self.clearRadioButtons()

        addformat.ui.radio2160.clicked.connect(lambda: (self.quality(2160), self.video))
        addformat.ui.radio1440.clicked.connect(lambda: (self.quality(1440), self.video))
        addformat.ui.radio1080.clicked.connect(lambda: (self.quality(1080), self.video))
        addformat.ui.radio720.clicked.connect(lambda: (self.quality(720), self.video))
        addformat.ui.radio480.clicked.connect(lambda: (self.quality(480), self.video))
        addformat.ui.radio360.clicked.connect(lambda: (self.quality(360), self.video))
        addformat.ui.radio240.clicked.connect(lambda: (self.quality(240), self.video))
        addformat.ui.radio144.clicked.connect(lambda: (self.quality(144), self.video))

        addformat.ui.radioMP4.clicked.connect(lambda: (self.format('mp4'), self.video))
        addformat.ui.radioWEBM.clicked.connect(lambda: (self.format('webm'), self.video))

        addformat.ui.audioRadio192.clicked.connect(lambda: (self.quality(192), self.audio))
        addformat.ui.audioRadio128.clicked.connect(lambda: (self.quality(128), self.audio))
        addformat.ui.audioRadio64.clicked.connect(lambda: (self.quality(64), self.audio))

        addformat.ui.radioMP3.clicked.connect(lambda: (self.format('mp3'), self.audio))
        addformat.ui.radioWAV.clicked.connect(lambda: (self.format('wav'), self.audio))

        addformat.ui.ready.clicked.connect(self._addFormat)

    def quality(self, quality: int):
        self.format_dict['quality'] = str(quality)

    def format(self, format_: str):
        self.format_dict['format'] = format_

    def video(self):
        for radio in self.audioQualityButtons:
            radio.setEnabled(False)
            # self.format_dict['quality'] = None
        for radio in self.audioFormatsButtons:
            radio.setEnabled(False)
            # self.format_dict['format'] = None

        for radio in self.videoQualityButtons:
            radio.setEnabled(True)
        for radio in self.videoFormatsButtons:
            radio.setEnabled(True)

        for x in self.format_dict:
            self.format_dict[x] = None

        addformat.ui.audioRadioButton.setChecked(False)
        self.format_dict['type'] = 'video'

    def audio(self):
        for radio in self.videoQualityButtons:
            radio.setEnabled(False)
        for radio in self.videoFormatsButtons:
            radio.setEnabled(False)

        for radio in self.audioQualityButtons:
            radio.setEnabled(True)
        for radio in self.audioFormatsButtons:
            radio.setEnabled(True)

        addformat.ui.videoRadioButton.setChecked(False)
        self.format_dict['type'] = 'audio'

    def _addFormat(self):
        self.checkFields()



        for radio in self.audioQualityButtons:
            radio.setChecked(False)
            # self.format_dict['quality'] = None
        for radio in self.audioFormatsButtons:
            radio.setChecked(False)
            # self.format_dict['format'] = None

        for radio in self.videoQualityButtons:
            radio.setChecked(False)
        for radio in self.videoFormatsButtons:
            radio.setChecked(False)

    def checkFields(self):
        """Проверка заполнения обязательных полей"""
        unchecked = []
        translations = {'video': "Видео", 'audio': "Аудио"}
        for field in self.format_dict:
            if self.format_dict[field] is None:
                unchecked.append(translations.get(field))

        if unchecked:
            pass
            '''QtWidgets.QMessageBox.warning(self, 'Ахтунг!',
                                          f'Не выбраны поля: {", ".join(unchecked)}. Пожалуйста, выберите!')'''
        else:
            # Добавляем запись в таблицу и обрабатываем её
            self.addVideoToTable()

    def addVideoToTable(self):
        """Добавляет новую строку в таблицу с информацией о видео"""
        self.new_video.update({
            'filename': self.filename,
            'format': self.format_dict.copy(),
            'index': self.index
        })

        self.ui.tableWidget.insertRow(self.index)
        self.ui.tableWidget.setItem(self.index, 0, QtWidgets.QTableWidgetItem(self.metadata['title']))
        self.ui.tableWidget.setItem(self.index, 1, QtWidgets.QTableWidgetItem(self.new_video['url']))
        self.ui.tableWidget.setItem(self.index, 2, QtWidgets.QTableWidgetItem(self.new_video['filename']))
        self.ui.tableWidget.setItem(self.index, 3, QtWidgets.QTableWidgetItem(f'{self.new_video['format']['type']} - {self.new_video['format']['quality']} - {self.new_video['format']['format']}'))
        self.ui.tableWidget.setItem(self.index, 4, QtWidgets.QTableWidgetItem('Простаивает'))

        self.index += 1
        self.ui.tableWidget.setRowCount(self.index)
        self.clearRadioButtons()
        self.videoQueue.put(self.new_video)
        self.format_dict = {'video': None, 'audio': None}
        self.new_video = {'url': None, 'filename': None, 'format': {}}
        self.metadata = {}
        self.title = ''
        self.filename = ''
        addformat.close()

    def clearRadioButtons(self):
        """Очистка выбранных радиобатонов"""
        for radio in self.audioQualityButtons:
            radio.setChecked(False)
        for radio in self.audioFormatsButtons:
            radio.setChecked(False)
        for radio in self.videoQualityButtons:
            radio.setChecked(False)
        for radio in self.videoFormatsButtons:
            radio.setChecked(False)

    def updateProgress(self, d: dict, index: int):
        QtWidgets.QApplication.processEvents()
        if d['status'] == 'downloading':
            percent_str = str(int(d['_percent'])) + '%' + ' загружено'
            self.ui.tableWidget.setItem(index, 4, QtWidgets.QTableWidgetItem(percent_str))
        elif d['status'] == 'finished':
            self.ui.tableWidget.setItem(index, 4, QtWidgets.QTableWidgetItem('Завершен'))

    def createMsg(self):
        self.completed.ui.label.setText(f'Все видео были скачаны!')
        self.completed.ui.mainMenu.clicked.connect(mainMenu)
        self.completed.show()



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
    args = [sys.executable] + sys.argv
    os.execv(sys.executable, args)




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

    def quality(self, quality: int):
        self.format_dict['quality'] = quality

    def format(self, format_: str):
        self.format_dict['format'] = format_


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

    def updateProgress(self, d: dict):
        if d['status'] == 'downloading':
            #delta = datetime.timedelta(seconds=d['eta'])
            #self.ui.timeLeft.setText(humanize.naturaldelta(delta))
            #size = humanize.naturalsize(d['downloaded_bytes'])
            #self.ui.downloaded.setText(f'{size} из ')
            with open('asofasadsofd.json', 'w', encoding='utf-8') as f:
                json.dump(d, f, indent=4, ensure_ascii=False)
            self.ui.progressBar.setValue(int(d['_percent']))




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    start = StartMenu()
    found = FoundMenu()
    formats = FormatsMenu()
    download = DownloadMenu()
    addurl = AddURL(start)
    addformat = AddFormat(start)
    start.show()
    sys.exit(app.exec())