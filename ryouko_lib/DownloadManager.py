#! /usr/bin/env/ python

from __future__ import division
import os, sys
from PyQt4 import QtCore, QtGui, QtNetwork

try: __file__
except: __file__ = sys.executable
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(app_lib)

app_icons = os.path.join(app_lib, "icons")
from Python23Compat import *
from SystemFunctions import *
from QStringFunctions import *
from TranslationManager import *
from RExpander import *
from DialogFunctions import *
from DownloaderThread import *
if sys.platform.startswith("win"):
    app_logo = os.path.join(app_icons, 'about-logo.png')
else:
    app_logo = os.path.join(app_icons, "logo.svg")

downloaderThread = DownloaderThread()

class DownloadProgressBar(QtGui.QProgressBar):
    def __init__(self, reply=None, destination=os.path.expanduser("~"), parent=None):
        super(DownloadProgressBar, self).__init__()
        self.reply = reply
        self.destination = destination
        self.progress = [0, 0]
        if self.reply:
            self.reply.downloadProgress.connect(self.updateProgress)
            self.reply.finished.connect(self.finishDownload)
    def finishDownload(self):
        if self.reply.isFinished():
            data = self.reply.readAll()
            f = QtCore.QFile(self.destination)
            f.open(QtCore.QIODevice.WriteOnly)
            f.writeData(data)
            f.flush()
            f.close()
            self.progress = [0, 0]
    def updateProgress(self, received, total):
        self.setMaximum(total)
        self.setValue(received)
        self.progress[0] = received
        self.progress[1] = total
        self.show()

class DownloadProgressWidget(QtGui.QWidget):
    def __init__(self, reply=None, destination=os.path.expanduser("~"), parent=None):
        super(DownloadProgressWidget, self).__init__()

        self.label = QtGui.QLabel()
        self.label.setText(os.path.split(unicode(destination))[1])

        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.slWidget = QtGui.QWidget()
        self.mainLayout.addWidget(self.slWidget)

        self.subLayout = QtGui.QVBoxLayout()
        self.slWidget.setLayout(self.subLayout)

        self.subLayout.addWidget(self.label)
        
        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)

        self.layoutWidget = QtGui.QWidget()
        self.layoutWidget.setLayout(self.layout)
        self.subLayout.addWidget(self.layoutWidget)

        self.bottomBorder = QtGui.QWidget()
        self.bottomBorder.setStyleSheet("""
        background: palette(shadow);
        """)
        self.bottomBorder.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed))
        self.bottomBorder.setMinimumHeight(1)
        self.mainLayout.addWidget(self.bottomBorder)

        self.progressBar = DownloadProgressBar(reply, destination, self)
        self.destination = self.progressBar.destination
        self.progressBar.reply.downloadProgress.connect(self.updateProgress)
        self.progressBar.reply.finished.connect(self.setFinished)
        self.finished = False
        self.layout.addWidget(self.progressBar)
        self.reply = self.progressBar.reply

        self.openButton = QtGui.QToolButton()
        self.openButton.setToolTip(tr("openFile"))
        self.openButton.setEnabled(False)
        self.openButton.setIcon(QtGui.QIcon().fromTheme("media-playback-start", QtGui.QIcon(os.path.join(app_icons, 'play.png'))))
        self.openButton.clicked.connect(self.openFile)
        self.layout.addWidget(self.openButton)

        self.openFolderButton = QtGui.QToolButton()
        self.openFolderButton.setToolTip(tr("openFolder"))
        self.openFolderButton.setIcon(QtGui.QIcon().fromTheme("document-open", QtGui.QIcon(os.path.join(app_icons, 'open.png'))))
        self.openFolderButton.clicked.connect(self.openDestination)
        self.layout.addWidget(self.openFolderButton)

        self.stopButton = QtGui.QToolButton()
        self.stopButton.setToolTip(tr("abort"))
        self.stopButton.setIcon(QtGui.QIcon().fromTheme("process-stop", QtGui.QIcon(os.path.join(app_icons, 'stop.png'))))
        self.stopButton.clicked.connect(self.abort)
        self.layout.addWidget(self.stopButton)

        self.yay = True
        self.progress = [0, 0]

    def openFile(self):
        system_open(self.destination)

    def openDestination(self):
        if sys.platform.startswith("linux"):
            os.system("xdg-open \"" + os.path.split(unicode(self.destination))[0] + "\"")
        elif sys.platform.startswith("win"):
            os.system("start " + os.path.split(unicode(self.destination))[0])
        elif "darwin" in sys.platform:
            os.system("open \"" + os.path.split(unicode(self.destination))[0] + "\"")

    def setFinished(self, finished=True):
        self.finished = finished
        if self.yay == True:
            self.openButton.setEnabled(True)

    def updateProgress(self, received, total):
        self.progress[0] = received
        self.progress[1] = total

    def abort(self):
        self.yay = False
        self.progressBar.reply.abort()
        self.progressBar.reply.finished.emit()

class DownloadProgressDialog(QtGui.QProgressBar):
    def __init__(self, reply=None, destination=os.path.expanduser("~"), parent=None):
        super(DownloadProgressDialog, self).__init__()
        self.reply = reply
        self.destination = destination
        self.progress = [0, 0]
        if self.reply:
            self.reply.downloadProgress.connect(self.updateProgress)
            self.reply.finished.connect(self.finishDownload)
        self.setWindowTitle(os.path.split(unicode(destination))[1])
    def finishDownload(self):
        if self.reply.isFinished():
            data = self.reply.readAll()
            f = QtCore.QFile(self.destination)
            f.open(QtCore.QIODevice.WriteOnly)
            f.writeData(data)
            f.flush()
            f.close()
            self.progress = [0, 0]
            self.hide()
    def updateProgress(self, received, total):
        self.setMaximum(total)
        self.setValue(received)
        self.progress[0] = received
        self.progress[1] = total
        self.show()

class DownloadManagerGUI(QtGui.QMainWindow):
    downloadProgress = QtCore.pyqtSignal(float)
    downloadFinished = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(DownloadManagerGUI, self).__init__()
        self.downloads = []
        self.progress = 0.0

        self.networkAccessManager = QtNetwork.QNetworkAccessManager(self)

        self.setWindowTitle(tr('downloads'))
        self.setWindowIcon(QtGui.QIcon(app_logo))

        closeWindowAction = QtGui.QAction(self)
        closeWindowAction.setShortcuts(["Ctrl+W", "Esc", "Ctrl+Shift+Y", "Ctrl+J"])
        closeWindowAction.triggered.connect(self.close)
        self.addAction(closeWindowAction)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setStyleSheet("QScrollArea { border: 0; border-bottom: 1px solid palette(shadow); }")
        self.scrollArea.setMinimumHeight(256)
        self.scrollArea.setMinimumWidth(400)
        self.scrollArea.setWidgetResizable(True)
        self.setCentralWidget(self.scrollArea)

        self.centralWidget = QtGui.QWidget()
        self.scrollArea.setWidget(self.centralWidget)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setContentsMargins(0,0,0,0)
        self.centralWidget.setLayout(self.layout)

        self.toolBar = QtGui.QToolBar()
        self.toolBar.setStyleSheet("QToolBar { border: 0; }")
        self.toolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.toolBar.setMovable(False)
        self.toolBar.setStyleSheet("QToolBar { border: 0; }")
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolBar)

        self.clearButton = QtGui.QPushButton(tr("clear"))
        self.clearButton.clicked.connect(self.clear)
        self.toolBar.addWidget(self.clearButton)

        self.abortButton = QtGui.QPushButton(tr("abortAll"))
        self.abortButton.clicked.connect(self.abortAll)
        self.toolBar.addWidget(self.abortButton)

        self.toolBar.addWidget(RExpander())

        self.downloadButton = QtGui.QPushButton(tr("downloadFile"))
        self.downloadButton.clicked.connect(self.downloadFile)
        self.toolBar.addWidget(self.downloadButton)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkProgress)
        self.timer.start(1250)

    """def close(self):
        if self.progress > 0.0:
            q = QtGui.QMessageBox.question(None, tr("warning"),
        tr("downloadsInProgress"), QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if q == QtGui.QMessageBox.Yes:
                QtGui.QWidget.close(self)
        else:
            QtGui.QWidget.close(self)"""

    def newReply(self, reply, destination = os.path.expanduser("~")):
        i = DownloadProgressWidget(reply, destination)
        self.downloads.append(i)
        reply.finished.connect(self.checkForFinishedDownloads)
        self.layout.addWidget(i)
        self.show()
        self.activateWindow()

    def downloadFile(self):
        url = inputDialog(tr("query"), tr('enterURL'))
        if url:
            fname = saveDialog(os.path.split(unicode(url))[1])
            if fname:
                nm = self.networkAccessManager
                reply = nm.get(QtNetwork.QNetworkRequest(QtCore.QUrl(url)))
                self.newReply(reply, fname)

    def clear(self):
        for i in self.downloads:
            if i.finished == True:
                i.deleteLater()
                del i

    def abortAll(self):
        q = QtGui.QMessageBox.question(None, tr("warning"),
        tr("downloadsInProgress"), QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if q == QtGui.QMessageBox.Yes:
            for i in self.downloads:
                i.abort()
                i.reply.finished.emit()

    def checkProgress(self):
        pr = 0.0
        pt = 0.0
        for p in self.downloads:
            if not p.reply.isFinished() and p.yay == True:
                pr = pr + float(p.progress[0])
                pt = pt + float(p.progress[1])
        if pt != 0.0:
            pe = pr/pt
        else:
            pe = 0.0
        if pe == 0.0:
            self.setWindowTitle(tr('downloads'))
        else:
            self.setWindowTitle(tr('downloads') + " - " + str(int(pe*100)) + "%")
        self.progress = pe
        self.downloadProgress.emit(pe)
            
    def checkForFinishedDownloads(self):
        for i in range(len(self.downloads)):
            if self.downloads[i].reply.isFinished():
                if self.downloads[i].yay == False:
                    aborted = True
                else:
                    aborted = False
                if aborted == False:
                    self.downloadFinished.emit()
                else:
                    self.downloads[i].deleteLater()
                    del self.downloads[i]
                break
