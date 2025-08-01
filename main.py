import sys
from pprint import pprint

from PyQt6 import QtWidgets
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QGraphicsScene

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
        self.format_dict = {
            'type': '',
            'quality': 0,
            'format':''
        }

        self.ui.videoRadioButton.clicked.connect(self.video)
        self.ui.audioRadioButton.clicked.connect(self.audio)

        self.ui.radio1080.clicked.connect(lambda: self.quality(1080))
        self.ui.radio720.clicked.connect(lambda: self.quality(720))

        self.ui.radioMP4.clicked.connect(lambda: self.format('mp4'))
        self.ui.radioMOV.clicked.connect(lambda: self.format('mov'))

        self.ui.radio192.clicked.connect(lambda: self.quality(192))

        self.ui.radioMP3.clicked.connect(lambda: self.format('mp3'))
        self.ui.radioWAV.clicked.connect(lambda: self.format('wav'))

        self.ui.pushButton.clicked.connect(lambda: pprint(self.format_dict))

    def video(self):
        if not self.ui.videoFrame.isEnabled():
            self.ui.videoFrame.setEnabled(True)
        self.ui.audioFrame.setEnabled(False)
        self.ui.audioRadioButton.setChecked(False)
        self.format_dict['type'] = 'video'

    def audio(self):
        if not self.ui.audioFrame.isEnabled():
            self.ui.audioFrame.setEnabled(True)
        self.ui.videoFrame.setEnabled(False)
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