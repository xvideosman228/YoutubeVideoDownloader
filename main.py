import sys
from email.utils import format_datetime
from pprint import pprint

from PyQt6 import QtWidgets
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QGraphicsScene, QMessageBox
from PyQt6.uic.Compiler.qtproxies import QtGui

import foundMenu
import startMenu
import formatsMenu

import youtubeParser
from youtubeParser import YoutubeDownloader


class StartMenu(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = startMenu.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.found)

    @staticmethod
    def found():
        # data = youtubeParser.YoutubeDownloader.GetVideoInfo('https://youtu.be/z0wK6s-6cbo?si=bnNta5oS9UKb2EAh')

        #title = data["title"]
        #thumbnail_link = data["thumbnail"]

        '''
        likes = data["like_count"]
        views = data["view_count"]
        duration = data["duration"]
        timestamp = data["timestamp"]
        duration = data["duration_string"]
        '''

        #thumbnail = YoutubeDownloader.DownloadThumbnail(thumbnail_link, data['title'])
        #thumbnail = QPixmap(thumbnail)

        #found.ui.videoTitle.setText(title)
        #found.ui.label_3.setPixmap(thumbnail)

        start.close()
        formats.show()




class FoundMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = foundMenu.Ui_Form()
        self.ui.setupUi(self)

class FormatsMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = formatsMenu.Ui_Form()
        self.ui.setupUi(self)
        self.url = 'https://youtu.be/LXb3EKWsInQ?si=aSH57ndvFXAF3AdD'
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
            self.ui.radioAVI,
            self.ui.radioMOV
        ]

        self.audioFormatsButtons = [
            self.ui.radioMP3,
            self.ui.radioWAV
        ]

        self.audioQualityButtons = [
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
        self.ui.radioMOV.clicked.connect(lambda: (self.format('mov'), self.video))
        self.ui.radioWEBM.clicked.connect(lambda: (self.format('webm'), self.video))
        self.ui.radioAVI.clicked.connect(lambda: (self.format('avi'), self.video))

        self.ui.audioRadio192.clicked.connect(lambda: (self.quality(192), self.audio))
        self.ui.audioRadio128.clicked.connect(lambda: (self.quality(128), self.audio))

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

    def checkFields(self):
        unchecked = []
        for x in self.format_dict:
            if self.format_dict[x] is None:
                unchecked.append(self.translations[x])
        if not unchecked:
            pprint(self.format_dict)
            if self.format_dict['type'] == 'video':
                YoutubeDownloader.DownloadVideo(self.url, self.format_dict["quality"], self.format_dict["format"])
            elif self.format_dict['type'] == 'audio':
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

    start.show()
    sys.exit(app.exec())