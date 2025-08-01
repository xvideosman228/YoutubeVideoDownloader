import sys
from PyQt6 import QtWidgets
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QGraphicsScene

import foundMenu
import startMenu
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
        data = youtubeParser.YoutubeDownloader.GetVideoInfo('https://youtu.be/z0wK6s-6cbo?si=QqtO6pWC3fJlU_vd')
        thumbnail_link = data["thumbnail"]
        print(thumbnail_link)
        print(data['title'])
        thumbnail = YoutubeDownloader.DownloadThumbnail(thumbnail_link, data['title'])
        thumbnail = QPixmap(thumbnail)

        found.ui.label_3.setPixmap(thumbnail)
        start.close()
        found.show()

class FoundMenu(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = foundMenu.Ui_Form()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    start = StartMenu()
    found = FoundMenu()

    start.show()
    sys.exit(app.exec())