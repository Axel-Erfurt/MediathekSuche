#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import queue     #If this template is not loaded, pyinstaller may not be able to run the requests template after packaging
import requests
################################################


################################################
class Downloader(QWidget):
    def __init__(self, *args, **kwargs):
        super(Downloader, self).__init__(*args, **kwargs)
        
        self.setStyleSheet("QWidget {background: qlineargradient(y1: 0, y2: 1, \
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD, \
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);} \
                                 QPushButton {background: #babdb6;} \
                                 QLabel {background: transparent;}")
        layout = QVBoxLayout(self)
        hlayout = QHBoxLayout()
        
        #self.homepath = QDir.homePath() + "/Downloads/"
        self.root = QFileInfo(__file__).absolutePath()
        self.homepath = ""
        folder = self.root + "/DLOrdner.txt"
        #print("folder", folder)
        with open(folder, 'r') as f:
            t = f.read()
            self.homepath = t.replace("\n", "")
            
            if t == "":
                fd = QDir.homePath() + "/Downloads/"
                with open(folder, 'w') as f:
                    f.write(fd)
                    t = fd
            
        print("Download Ordner:", t)
        self.url = ""
        self.fname = ""

        # Download Button
        self.pushButton = QPushButton(self, minimumWidth=100)
        self.pushButton.setText("Download")
        self.pushButton.setIcon(QIcon.fromTheme("download"))
        hlayout.addWidget(self.pushButton)
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        
        # Cancel Button
        self.cancelButton = QPushButton(self, minimumWidth=100)
        self.cancelButton.setText("Cancel")
        self.cancelButton.setIcon(QIcon.fromTheme("cancel"))
        hlayout.addWidget(self.cancelButton)
        self.cancelButton.setVisible(False)
        self.cancelButton.clicked.connect(self.on_cancelButton_clicked)
        
        # Bar
        self.progressBar = QProgressBar(self, minimumWidth=400)
        self.progressBar.setValue(0)
        #self.progressBar.setFixedHeight(12)
        self.progressBar.setStyleSheet("QProgressBar {font-size: 7pt;}")
        hlayout.addWidget(self.progressBar)
        
        self.lbl = QLabel("status")
        layout.addLayout(hlayout)
        layout.addWidget(self.lbl)
        
        self.lbl.setStyleSheet("QLabel {font-size: 8pt; color: #888a85}")
        self.lbl.setText("Ready")


    def on_pushButton_clicked(self):
        the_url = self.url
        the_filesize = requests.get(the_url, stream=True).headers['Content-Length']
        the_filepath = self.homepath + self.fname
        the_fileobj = open(the_filepath, 'wb')
        #### Create a download thread
        self.downloadThread = downloadThread(the_url, the_filesize, the_fileobj, buffer=10240)
        self.downloadThread.download_proess_signal.connect(self.set_progressbar_value)
        self.downloadThread.start()
        self.lbl.setText("Download started ...")
        self.cancelButton.setVisible(True)



    # Setting progress bar
    def set_progressbar_value(self, value):
        self.progressBar.setValue(value)
        if value == 100:
            QMessageBox.information(self, "Tips", "Download success!")
            self.close()


    def on_cancelButton_clicked(self):
        self.downloadThread.terminate()
        self.lbl.setText("Download cancelled")
        self.cancelButton.setVisible(False)


##################################################################
#Download thread
##################################################################
class downloadThread(QThread):
    download_proess_signal = pyqtSignal(int)                        #Create signal

    def __init__(self, url, filesize, fileobj, buffer):
        super(downloadThread, self).__init__()
        self.url = url
        self.filesize = filesize
        self.fileobj = fileobj
        self.buffer = buffer


    def run(self):
        try:
            rsp = requests.get(self.url, stream=True)                #Streaming download mode
            offset = 0
            for chunk in rsp.iter_content(chunk_size=self.buffer):
                if not chunk: break
                self.fileobj.seek(offset)                            #Setting Pointer Position
                self.fileobj.write(chunk)                            #write file
                offset = offset + len(chunk)
                proess = offset / int(self.filesize) * 100
                self.download_proess_signal.emit(int(proess))        #Sending signal
            #######################################################################
            self.fileobj.close()    #Close file
            self.exit(0)            #Close thread


        except Exception as e:
            print(e)

####################################
#Program entry
####################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Downloader()
    w.setWindowTitle("Downloader")
    w.show()
    sys.exit(app.exec_())
