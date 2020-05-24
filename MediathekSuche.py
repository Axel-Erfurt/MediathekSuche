#!/usr/bin/python3
# -*- coding: utf-8 -*-

### © Axel Schneider 2020 ###
### Credits: https://github.com/mediathekview/mediathekviewweb (API used) ###
### GNU General Public License v3.0 ###

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (QFileInfo, Qt, QSettings, QSize, QFile, QModelIndex, QObject, QEvent)
from PyQt5.QtWidgets import (QMainWindow, QTableWidget, QGridLayout, QPushButton, 
                             QAbstractItemView, QAction, QLineEdit, QWidget, QLabel, 
                             QComboBox, QMessageBox, QApplication,  QTableWidgetItem, QCheckBox)
import MediathekPlayer
import Downloader
import time
import requests
###################################

class MyWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__()
        self.setObjectName("MediathekQuery")
        self.root = QFileInfo(__file__).absolutePath()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.settings = QSettings('Axel Schneider', self.objectName())
        self.viewer = QTableWidget()
        
        
        self.horizontalHeader = self.viewer.horizontalHeader()
        
        icon = self.root + "/icon.png"
        
        self.titleList = []
        self.topicList = []
        self.urlList = []
        self.urlKleinList = []
        self.beschreibungList = []
        self.idList = []
        self.chList = []
        self.lengthList = []
        self.results = ""
        
        self.myurl = ""
        self.fname = ""
        self.viewer.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.viewer.SelectionMode(QAbstractItemView.SingleSelection)
        self.viewer.setSortingEnabled(False)
        self.viewer.verticalHeader().setStretchLastSection(False)
        self.viewer.horizontalHeader().setStretchLastSection(True)
        #self.viewer.horizontalHeader().sectionClicked.connect(self.sortTable)

        self.viewer.setColumnCount(7)
        self.viewer.setColumnWidth(0, 48)
        self.viewer.setColumnWidth(1, 130)
        self.viewer.setColumnWidth(2, 160)
        self.viewer.setColumnWidth(3, 60)
        self.viewer.hideColumn(4)
        self.viewer.hideColumn(5)
        self.viewer.setHorizontalHeaderLabels(["Sender", "Thema", "Titel", "Länge", "HD", "SD", "Beschreibung"])

        self.viewer.verticalHeader().setVisible(True)
        self.viewer.horizontalHeader().setVisible(True)
        self.setStyleSheet(stylesheet(self))        
        self.viewer.selectionModel().selectionChanged.connect(self.getCellText)
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.viewer,0, 0, 1, 6)

        self.findfield = QLineEdit()
        self.fAction = QAction(QIcon.fromTheme("edit-clear"), "", triggered = self.findfieldAction)
        self.findfield.addAction(self.fAction, 1)
        self.findfield.returnPressed.connect(self.myQuery)
        self.findfield.setFixedWidth(200)
        self.findfield.setPlaceholderText("suchen ...")
        self.findfield.setToolTip("ENTER to find")
        self.layout.addWidget(self.findfield,1, 0)
        
        self.chCombo = QComboBox()
        self.chCombo.setFixedWidth(80)
        self.chCombo.addItems(['ARD', 'ZDF', 'MDR', 'PHOENIX', 'RBB', 'BR', 'HR', 'SR', \
                               'SWR', 'NDR', 'DW', 'WDR', 'ARTE', '3SAT', 'KIKA', 'ORF', 'SRF'])
        self.chCombo.addItem("alle")
        self.chCombo.setToolTip("Sender wählen")
        self.chCombo.currentIndexChanged.connect(self.myQuery)
        self.layout.addWidget(self.chCombo,1, 1)
        
        self.btnPlay = QPushButton("Play")
        self.btnPlay.setFixedWidth(80)
        self.btnPlay.setIcon(QIcon.fromTheme("media-playback-start"))
        self.layout.addWidget(self.btnPlay,1, 2)
        self.btnPlay.clicked.connect(self.playVideo)
        
        self.btnDownload = QPushButton("Download")
        self.btnDownload.setFixedWidth(100)
        self.btnDownload.setIcon(QIcon.fromTheme("download"))
        self.layout.addWidget(self.btnDownload,1, 3)
        self.btnDownload.clicked.connect(self.downloadVideo)
        
        self.chBox = QPushButton("SD")
        self.chBox.setToolTip("umschalten HD / SD")
        self.chBox.setStyleSheet("background: #729fcf;")
        self.chBox.setFixedWidth(44)
        self.chBox.clicked.connect(self.toggleQuality)
        self.layout.addWidget(self.chBox,1, 4)
        
        self.lbl = QLabel("Info")
        self.layout.addWidget(self.lbl,1, 5)

        self.myWidget = QWidget()
        self.myWidget.setLayout(self.layout)

        self.msg("Ready")
        self.setCentralWidget(self.myWidget)
        self.setWindowIcon(QIcon(icon))
        self.setGeometry(20,20,600,450)
        self.setWindowTitle("Mediathek Suche")
        self.readSettings()
        self.msg("Ready")
        self.findfield.setFocus()
        self.player = MediathekPlayer.VideoPlayer('')
        self.player.hide()
        help_label = QLabel("<b>Wildcards:</b> <b>+</b> Titel, <b>#</b> Thema, <b>*</b> Beschreibung")
        help_label.setStyleSheet("font-size: 8pt; color: #1a2334;")
        self.statusBar().addPermanentWidget(help_label)
        self.statusBar().showMessage("Ready")
        
    def toggleQuality(self):
        if self.chBox.text() == "SD":
            self.chBox.setText("HD")
            self.chBox.setStyleSheet("background: #8ae234;")
            self.getCellText()
        else:
            self.chBox.setText("SD")
            self.chBox.setStyleSheet("background: #729fcf;")
            self.getCellText()
        
    def myQuery(self):
        if not self.findfield.text() == "":
            self.viewer.setRowCount(0)
            self.viewer.clearContents()
            self.titleList = []
            self.topicList = []
            self.urlList = []
            self.urlKleinList = []
            self.beschreibungList = []
            self.idList = []
            self.chList = []
            self.lengthList = []

            channels = [self.chCombo.currentText()]
            if channels == ["alle"]:
                channels = ["ard", "zdf", "mdr", "phoenix", "rbb", "br", "hr", "sr", "swr", "ndr",\
                            "dw", "wdr", "arte", "3sat", "kika", "orf", "srf"]
            print("suche",  self.findfield.text(), "in", ','.join(channels).upper())
            
            if self.findfield.text().startswith("*"):
                ### nur Beschreibung
                for ch in channels:
                    r = self.makeQueryBeschreibung(ch, self.findfield.text()[1:])
            elif self.findfield.text().startswith("#"):
                ### nur Thema
                for ch in channels:
                    r = self.makeQueryTopic(ch, self.findfield.text()[1:])
            elif self.findfield.text().startswith("+"):
                ### nur Titel
                for ch in channels:
                    r = self.makeQueryTitle(ch, self.findfield.text()[1:])
            else:
                ### alle Felder
                for ch in channels:
                    r = self.makeQuery(ch, self.findfield.text())

            for b in range(len(self.titleList)):
                self.idList.append(str(b))
                    
            for x in range(len(self.titleList)):
                #print(f"{self.idList[x]}\t{self.chList[x]}\t{self.topicList[x]}\t{self.titleList[x]}\t{self.urlList[x]}")
                self.viewer.insertRow(x)
                self.viewer.setItem(x, 0, QTableWidgetItem(self.chList[x]))
                self.viewer.setItem(x, 1, QTableWidgetItem(self.topicList[x]))
                self.viewer.setItem(x, 2, QTableWidgetItem(self.titleList[x]))
                self.viewer.setItem(x, 4, QTableWidgetItem(self.urlList[x]))
                self.viewer.setItem(x, 5, QTableWidgetItem(self.urlKleinList[x]))
                self.viewer.setItem(x, 6, QTableWidgetItem(self.beschreibungList[x]))
                self.viewer.setItem(x, 3, QTableWidgetItem(self.lengthList[x]))
            for x in range(len(self.titleList)):
                self.viewer.resizeRowToContents(x)
        
        
    def makeQuery(self, channel, myquery):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0',
            'Accept': '*/*',
            'Accept-Language': 'de-DE,en;q=0.5',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Connection': 'keep-alive',
        }
        
        data = {"future":"true", "size":"500", "sortBy":"timestamp", "sortOrder":"desc", \
                "queries":[{"fields":["title", "topic", "description"],
                "query":"" + myquery + ""},{"fields":["channel"],
                "query":"" + channel + ""}]}
        
        response = requests.post('https://mediathekviewweb.de/api/query', headers=headers, json=data)
        response_json = response.json()
        count = int(response_json['result']['queryInfo']['resultCount'])
        for x in range(count):
            topic = response_json['result']['results'][x]['topic']
            title = response_json['result']['results'][x]['title']
            url = response_json['result']['results'][x]['url_video']
            url_klein = response_json['result']['results'][x]['url_video_low']
            beschreibung = response_json['result']['results'][x]['description']
            l = response_json['result']['results'][x]['duration']
            if not l == "":
                length = time.strftime('%H:%M:%S', time.gmtime(l))
                self.lengthList.append(length)
            else:
                self.lengthList.append("")
            ch = response_json['result']['results'][x]['channel']
            if not ch == "":
                self.chList.append(ch)
            else:
                self.chList.append("")
            if not title == "":    
                self.titleList.append(title)
            else:
                self.titleList.append("")
            if not topic == "":
                self.topicList.append(topic)
            else:
                self.topicList.append("")
            if not url == "":
                self.urlList.append(url)
            else:
                self.urlList.append("")
            if not url_klein == "":
                self.urlKleinList.append(url_klein)
            else:
                self.urlKleinList.append("")
            if not beschreibung == "":
                self.beschreibungList.append(beschreibung)
            else:
                self.beschreibungList.append("")
            
        print(count, "Beiträge gefunden")
        self.lbl.setText(f"{count} Beiträge gefunden")
        
    def makeQueryBeschreibung(self, channel, myquery):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0',
            'Accept': '*/*',
            'Accept-Language': 'de-DE,en;q=0.5',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Connection': 'keep-alive',
        }
        
        data = {"future":"true", "size":"500", "sortBy":"timestamp", "sortOrder":"desc", \
                "queries":[{"fields":["description"],
                "query":"" + myquery + ""},{"fields":["channel"],
                "query":"" + channel + ""}]}
        
        response = requests.post('https://mediathekviewweb.de/api/query', headers=headers, json=data)
        response_json = response.json()
        count = int(response_json['result']['queryInfo']['resultCount'])
        for x in range(count):
            topic = response_json['result']['results'][x]['topic']
            title = response_json['result']['results'][x]['title']
            url = response_json['result']['results'][x]['url_video']
            url_klein = response_json['result']['results'][x]['url_video_low']
            beschreibung = response_json['result']['results'][x]['description']
            l = response_json['result']['results'][x]['duration']
            if not l == "":
                length = time.strftime('%H:%M:%S', time.gmtime(l))
                self.lengthList.append(length)
            else:
                self.lengthList.append("")
            ch = response_json['result']['results'][x]['channel']
            if not ch == "":
                self.chList.append(ch)
            else:
                self.chList.append("")
            if not title == "":    
                self.titleList.append(title)
            else:
                self.titleList.append("")
            if not topic == "":
                self.topicList.append(topic)
            else:
                self.topicList.append("")
            if not url == "":
                self.urlList.append(url)
            else:
                self.urlList.append("")
            if not url_klein == "":
                self.urlKleinList.append(url_klein)
            else:
                self.urlKleinList.append("")
            if not beschreibung == "":
                self.beschreibungList.append(beschreibung)
            else:
                self.beschreibungList.append("")
            
        print(count, "Beiträge gefunden")
        self.lbl.setText(f"{count} Beiträge gefunden")
        
    def makeQueryTopic(self, channel, myquery):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0',
            'Accept': '*/*',
            'Accept-Language': 'de-DE,en;q=0.5',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Connection': 'keep-alive',
        }
        
        data = {"future":"true", "size":"500", "sortBy":"timestamp", "sortOrder":"desc", \
                "queries":[{"fields":["topic"],
                "query":"" + myquery + ""},{"fields":["channel"],
                "query":"" + channel + ""}]}
        
        response = requests.post('https://mediathekviewweb.de/api/query', headers=headers, json=data)
        response_json = response.json()
        count = int(response_json['result']['queryInfo']['resultCount'])
        for x in range(count):
            topic = response_json['result']['results'][x]['topic']
            title = response_json['result']['results'][x]['title']
            url = response_json['result']['results'][x]['url_video']
            url_klein = response_json['result']['results'][x]['url_video_low']
            beschreibung = response_json['result']['results'][x]['description']
            l = response_json['result']['results'][x]['duration']
            if not l == "":
                length = time.strftime('%H:%M:%S', time.gmtime(l))
                self.lengthList.append(length)
            else:
                self.lengthList.append("")
            ch = response_json['result']['results'][x]['channel']
            if not ch == "":
                self.chList.append(ch)
            else:
                self.chList.append("")
            if not title == "":    
                self.titleList.append(title)
            else:
                self.titleList.append("")
            if not topic == "":
                self.topicList.append(topic)
            else:
                self.topicList.append("")
            if not url == "":
                self.urlList.append(url)
            else:
                self.urlList.append("")
            if not url_klein == "":
                self.urlKleinList.append(url_klein)
            else:
                self.urlKleinList.append("")
            if not beschreibung == "":
                self.beschreibungList.append(beschreibung)
            else:
                self.beschreibungList.append("")
            
        print(count, "Beiträge gefunden")
        self.lbl.setText(f"{count} Beiträge gefunden")
        
    def makeQueryTitle(self, channel, myquery):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0',
            'Accept': '*/*',
            'Accept-Language': 'de-DE,en;q=0.5',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Connection': 'keep-alive',
        }
        
        data = {"future":"true", "size":"500", "sortBy":"timestamp", "sortOrder":"desc", \
                "queries":[{"fields":["title"],
                "query":"" + myquery + ""},{"fields":["channel"],
                "query":"" + channel + ""}]}
        
        response = requests.post('https://mediathekviewweb.de/api/query', headers=headers, json=data)
        response_json = response.json()
        count = int(response_json['result']['queryInfo']['resultCount'])
        for x in range(count):
            topic = response_json['result']['results'][x]['topic']
            title = response_json['result']['results'][x]['title']
            url = response_json['result']['results'][x]['url_video']
            url_klein = response_json['result']['results'][x]['url_video_low']
            beschreibung = response_json['result']['results'][x]['description']
            l = response_json['result']['results'][x]['duration']
            if not l == "":
                length = time.strftime('%H:%M:%S', time.gmtime(l))
                self.lengthList.append(length)
            else:
                self.lengthList.append("")
            ch = response_json['result']['results'][x]['channel']
            if not ch == "":
                self.chList.append(ch)
            else:
                self.chList.append("")
            if not title == "":    
                self.titleList.append(title)
            else:
                self.titleList.append("")
            if not topic == "":
                self.topicList.append(topic)
            else:
                self.topicList.append("")
            if not url == "":
                self.urlList.append(url)
            else:
                self.urlList.append("")
            if not url_klein == "":
                self.urlKleinList.append(url_klein)
            else:
                self.urlKleinList.append("")
            if not beschreibung == "":
                self.beschreibungList.append(beschreibung)
            else:
                self.beschreibungList.append("")
            
        print(count, "Beiträge gefunden")
        self.lbl.setText(f"{count} Beiträge gefunden")
        
    def findfieldAction(self):
        self.findfield.setText("")
        
    def downloadVideo(self):
        if not self.url == "":
            self.downloader = Downloader.Downloader()
            self.downloader.setWindowTitle("Downloader")
            self.downloader.url = self.url
            item = self.viewer.selectedIndexes()[2]
            if not item == "":
                filename = str(item.data())
            self.downloader.fname = filename + self.url[-4:]
            self.downloader.lbl.setText("speichern als: " + self.downloader.homepath + self.downloader.fname)
            self.downloader.move(self.x() + 2, self.y() + 28)
            self.downloader.show()
        else:
            print("keine URL")
            self.msg("keine URL")
        
        
    def getCellText(self):
        if self.viewer.selectionModel().hasSelection():
            row = self.selectedRow()
            if not self.chBox.text() == "SD":
                item = self.urlList[row]
            else:
                item = self.urlKleinList[row]
            if not item == "":
                name = item
                self.url = str(item)
                print(self.url)
            infotext = f"{self.chList[row]}: {self.topicList[row]} - {self.titleList[row]} \
                        ({self.chBox.text()}) Dauer: {self.lengthList[row]}"
            self.msg(infotext)
            self.fname = str(self.viewer.selectedIndexes()[1].data())

        
    def playVideo(self):
        if self.viewer.selectionModel().hasSelection():
            row = self.selectedRow()
            if not self.chBox.text() == "SD":
                item = item = self.urlList[row]
                print("play HD")
            else:
                item = self.urlKleinList[row]
                print("play SD")
            if not item == "":
                self.url = item
                if not self.url == "":
                    print("url =", self.url)
                    self.player.show()
                    self.player.playMyURL(self.url)
                else:
                    print("keine URL vorhanden")
                    self.msg("keine URL vorhanden")
            else:
                print("keine URL vorhanden")
        else:
            print("keine URL vorhanden")

    def selectedRow(self):
        if self.viewer.selectionModel().hasSelection():
            row =  self.viewer.selectionModel().selectedIndexes()[0].row()
            return int(row)           

    def closeEvent(self, e):
        self.writeSettings()
        self.player.close()
        e.accept()

    def readSettings(self):
        print("lese Fensterposition")
        if self.settings.contains('geometry'):
            self.setGeometry(self.settings.value('geometry'))

    def writeSettings(self):
        print("Fensterposition gespeichert")
        self.settings.setValue('geometry', self.geometry())

    def msg(self, message):
        self.statusBar().showMessage(message, 0)


def stylesheet(self):
        return """
        QTableWidget
        {
            border: 1px solid grey;
            border-radius: 0px;
            font-size: 8pt;
            background-color: #d2d2d2;
            selection-background-color: #1a2334;
            selection-color: #ffffff;
        }
        QHeaderView
        {background-color:#d3d7cf;
        color: #2e3436; 
        font: bold
        }

        QHeaderView::section
        {background-color:#d3d7cf;
        color: #2e3436; 
        font: bold
        }
        QTableCornerButton::section 
        {
        background-color:#d3d7cf; 
        }

        QStatusBar
        {
            font-size: 8pt;
            color: #57579e;
        }

        QPushButton
        {
            height: 20px;
            font-size: 9pt;   
            background: #babdb6;
        }
        QPushButton:hover
        {   
            color: black;
            background: #729fcf;           
        }

        QComboBox
        {
            height: 22px;
            font-size: 9pt;
            background: #babdb6;
        }
        QComboBox:hover
        {   
            color: grey;
            background: #729fcf;           
        }
        QComboBox:item:hover
        {   
            color: grey;
            background: #204a87;           
        }       
        QMainWindow
        {
         background: qlineargradient(y1: 0, y2: 1,
                                     stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                     stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
        }
        QLineEdit
        {   
            height: 22px;
             background: qlineargradient(y1: 0, y2: 1,
                                         stop: 0 #d3d7cf, stop: 1.0 #babdb6);
}
    """
###################################     
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setApplicationName('MediathekQuery')
    main = MyWindow("")
    main.show()
    sys.exit(app.exec_())
