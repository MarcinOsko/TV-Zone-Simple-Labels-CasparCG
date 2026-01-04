import csv
import os
import socket
import threading
import time
import webbrowser

from PyQt6.QtCore import QDir
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem
from amcp_pylib.core import Client
from amcp_pylib.module import BYE

import CasparCG
from CasparCG import sendText, clearCG, nextCG, sendTextUpdate, playCG, dataStoreCG, dataRetriveCG, dataRemoveCG, \
    dataListCG, dataRetriveTab, dataStoreTab
from UI_SimpleLabels import Ui_MainWindow
from UI_SimpleLabels_about import Ui_About
from UI_SimpleLabels_help import Ui_Help

AllIPSerwer = ''


# HelpWindow window class
class HelpWindow(QMainWindow, Ui_Help):
    # def __init__(self, parent=None):
    #     super(AboutWindow, self).__init__(parent)

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi_Help(self)
        # self.show()


# About Window window class
class AboutWindow(QMainWindow, Ui_About):
    # def __init__(self, parent=None):
    #     super(AboutWindow, self).__init__(parent)

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi_About(self)
        # self.show()


# connection thread
class Worker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal()

    def run(self):
        try:
            client = Client()
            client.connect(AllIPSerwer, 5250)
            self.finished.emit()
        except Exception as e:
            print('Worker error:', e)
            self.error.emit()


# auto search and check status server thread
class SS_Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal()
    error = pyqtSignal()

    # for stop thread when change connection to Manual
    stop_thread = threading.Event()

    def run(self):
        is_template = False
        while True:

            # for stop thread when change connection to Manual
            if SS_Worker.stop_thread.is_set():
                break

            try:
                port = 5253
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(0.3)
                s.bind(('', port))
                time.sleep(2)
                data, addr = s.recvfrom(1024)
                self.progress.emit()
                ip_sever = addr[0]
                if data:
                    SimpleLabels.IPSerwer = ip_sever
                data = str(data)
                if data.count('template') > 0:
                    SimpleLabels.is_template = True
                else:
                    SimpleLabels.is_template = False

            except Exception as e:
                print('SS_Worker error:', e)
                self.error.emit()


# main class
class SimpleLabels(QMainWindow, Ui_MainWindow):
    IPSerwer = ''
    RowChanged = False
    AfterClear = False
    SelectTab = None
    N = 1
    isConnectPush = False
    is_template = False

    finished = pyqtSignal()

    # check Manual CONNECT checkbox status
    @staticmethod
    def isManualConect(self):
        isManual = False
        if self.checkBox_manualConnect.isChecked():
            isManual = True
        else:
            isManual = False
        return isManual

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        # Button adds empty row to the main table
        self.toolButton_Add_emptyRow.clicked.connect(self.add_emptyRow)

        # Button remove current row from the main table
        self.toolButton_RemoveSelectedRow.clicked.connect(self.remove_currentRow)

        # Button move current row to up position
        self.toolButton_MoveRowUp.clicked.connect(self.moveRowUp)

        # Button move current row to down position
        self.toolButton_MoveRowDown.clicked.connect(self.moveRowDown)

        # Button connect and disconnect from server CasparCG
        ## line for manual Conect in firs version
        # self.toolButton_connect.clicked.connect(self.serverConnect)
        self.toolButton_connect.clicked.connect(self.runLongTask)
        self.toolButton_connect.clicked.connect(self.IPset)

        # Button TAKE end TAKE OUT from server CasparCG
        self.toolButton_take.clicked.connect(self.takeCommand)

        # # activate button TAKE after click on some item in table
        self.tableWidget_labelsText.currentCellChanged.connect(self.isRowChanged)
        self.tableWidget_labelsText.currentCellChanged.connect(self._createStatusBar)

        # Button CLEAR cear CasparCG
        self.toolButton_clear.clicked.connect(self.clearCommand)
        self.toolButton_takeOut.clicked.connect(self.checkCommand)

        # save to CSV
        self.actionsave.triggered.connect(self.writeCsv)

        # load from CSV
        self.actionopen.triggered.connect(self.loadCsv)

        # export data to server
        self.actionexport.triggered.connect(self.writeData)

        # import data from server
        self.actionimport.triggered.connect(self.loadData)

        # open about Window
        self.actionAbout.triggered.connect(self.about_window)
        self.dialog_about = AboutWindow(self)

        # open help Window
        self.actionHelp.triggered.connect(self.help_window)
        self.dialog_help = HelpWindow(self)

        # open action menu web page
        self.actionWeb_page.triggered.connect(self.openUrl)


        # set buttons inactive
        self.toolButton_clear.setDisabled(True)
        self.toolButton_takeOut.setDisabled(True)
        self.toolButton_take.setDisabled(True)
        self.actionexport.setDisabled(True)
        self.actionimport.setDisabled(True)

        # check template status on server
        if self.is_template == False:
            self.toolButton_clear.setText('INITIALIZE')

        # start thread listening signal UDP signal from CasparCG serwer
        self.ss_checker()

        # make empty row in table after start
        for i in range(1, 41):
            self.add_emptyRow()

        # active StatusBar
        self._createStatusBar()

    # StatusBar function
    def _createStatusBar(self):
        self.statusbar = self.statusBar()

        currentRow = self.tableWidget_labelsText.currentRow()
        selectTab = self.tableWidget_labelsText.currentItem()
        table = self.tableWidget_labelsText

        table = self.tableWidget_labelsText
        if table.item(currentRow, 0) == None:
            item1 = ''
        else:
            item1 = table.item(currentRow, 0).text()

        if table.item(currentRow, 1) == None:
            item2 = ''
        else:
            item2 = table.item(currentRow, 1).text()
        FirstLine = 'First Line:'
        SocondLine = 'Second Line:'
        self.statusbar.showMessage(
            "   {:11} {:<6} {:^12} {:<3}".format(FirstLine, len(str(item1)), SocondLine, len(str(item2)))
        )

    # action menu web link
    def openUrl(self):
        return webbrowser.open('https://tvsimpleapps.com/simple-labels/')



    # show About window
    def about_window(self):
        self.dialog_about.show()

    # show Help window
    def help_window(self):
        self.dialog_help.show()

    # for stop thread
    def isManualConnect(self):
        if self.checkBox_manualConnect.isChecked():
            # print('checkBox is ON')
            SS_Worker.stop_thread.set()
            self.checkBox_manualConnect.setDisabled(True)
        else:
            None
            # print('checkBox is OFF')

    # connect button dissable
    def CnnectButtonDisable(self):
        self.toolButton_connect.setEnabled(False)

    # connect button enable
    def CnnectButtonEnable(self):
        self.toolButton_connect.setEnabled(True)

    # set server global IP
    def IPset(self):
        IPserwer = self.lineEdit_enterIP.text()
        global AllIPSerwer
        AllIPSerwer = IPserwer

    # check Row Changed - Bool
    def isRowChanged(self):
        SimpleLabels.RowChanged = True

    # make button Take on
    def activateButton(self):
        if SimpleLabels.IPSerwer:
            selectTab = self.tableWidget_labelsText.currentItem()
            if selectTab:
                self.toolButton_take.setDisabled(False)
        else:
            None

    # make button Take off
    def deactivateButton(self):
        self.toolButton_take.setDisabled(True)

    # The function add empty rows to the main table
    def add_emptyRow(self):
        if self.tableWidget_labelsText.currentRow() == -1:
            rowPosition = self.tableWidget_labelsText.rowCount()
            self.tableWidget_labelsText.insertRow(rowPosition)
        else:
            rowPosition = self.tableWidget_labelsText.currentRow()
            self.tableWidget_labelsText.insertRow(rowPosition)

    # The function remove current row from the main table
    def remove_currentRow(self):
        if self.tableWidget_labelsText.rowCount() < 2 or self.tableWidget_labelsText.columnCount() < 2:
            self.toolButton_take.setDisabled(True)
        currentRow = self.tableWidget_labelsText.currentRow()
        self.tableWidget_labelsText.removeRow(currentRow)

    # The function move current row up position
    def moveRowUp(self):
        row = self.tableWidget_labelsText.currentRow()
        column = self.tableWidget_labelsText.currentColumn()
        if row > 0:
            self.tableWidget_labelsText.insertRow(row - 1)
            for i in range(self.tableWidget_labelsText.columnCount()):
                self.tableWidget_labelsText.setItem(row - 1, i, self.tableWidget_labelsText.takeItem(row + 1, i))
                self.tableWidget_labelsText.setCurrentCell(row - 1, column)
            self.tableWidget_labelsText.removeRow(row + 1)

    # The function move current row down position
    def moveRowDown(self):
        row = self.tableWidget_labelsText.currentRow()
        column = self.tableWidget_labelsText.currentColumn()
        if row < self.tableWidget_labelsText.rowCount() - 1:
            self.tableWidget_labelsText.insertRow(row + 2)
            for i in range(self.tableWidget_labelsText.columnCount()):
                self.tableWidget_labelsText.setItem(row + 2, i, self.tableWidget_labelsText.takeItem(row, i))
                self.tableWidget_labelsText.setCurrentCell(row + 2, column)
            self.tableWidget_labelsText.removeRow(row)

    # function Take Buttun
    def takeCommand(self):
        currentRow = self.tableWidget_labelsText.currentRow()
        selectTab = self.tableWidget_labelsText.currentItem()
        table = self.tableWidget_labelsText
        selectItem1 = table.item(currentRow, 0)
        selectItem2 = table.item(currentRow, 1)
        dataList = dataListCG(SimpleLabels.IPSerwer)

        if self.checkBox_autoTake.isChecked():
            selectTab = self.tableWidget_labelsText.currentItem()
            dataList = dataListCG(SimpleLabels.IPSerwer)
            SimpleLabels.N = SimpleLabels.N + 1

            if SimpleLabels.N % 2 == 0:
                if selectItem1 == None and selectItem2 == None:
                    nextRow = currentRow + 1
                    self.tableWidget_labelsText.selectRow(nextRow)
                    SimpleLabels.N = 1
                else:
                    try:
                        table = self.tableWidget_labelsText
                        if table.item(currentRow, 0) == None and table.item(currentRow, 1) == None:
                            None
                        else:
                            # check data items from table
                            table = self.tableWidget_labelsText
                            if table.item(currentRow, 0) == None:
                                item1 = ''
                            else:
                                item1 = table.item(currentRow, 0).text()

                            if table.item(currentRow, 1) == None:
                                item2 = ''
                            else:
                                item2 = table.item(currentRow, 1).text()

                            item1 = item1.replace('\\', '\\\\')
                            item2 = item2.replace('\\', '\\\\')

                            sendTextUpdate(IPSerwer=SimpleLabels.IPSerwer, item1=item1, item2=item2)
                            playCG(IPSerwer=SimpleLabels.IPSerwer)
                    except:
                        print('takeCommandAutoParzysta error')
            else:
                if selectItem1 == None and selectItem2 == None and table.item(currentRow - 1, 0) == None and table.item(
                        currentRow - 1, 1) == None:
                    nextRow = currentRow + 1
                    self.tableWidget_labelsText.selectRow(nextRow)
                else:
                    try:
                        table = self.tableWidget_labelsText
                        if table.item(currentRow, 0) == None and table.item(currentRow, 1) == None:
                            None
                        else:
                            # check data items from table
                            table = self.tableWidget_labelsText
                            if table.item(currentRow, 0) == None:
                                item1 = ''
                            else:
                                item1 = table.item(currentRow, 0).text()

                            if table.item(currentRow, 1) == None:
                                item2 = ''
                            else:
                                item2 = table.item(currentRow, 1).text()

                            item1 = item1.replace('\\', '\\\\')
                            item2 = item2.replace('\\', '\\\\')

                            sendTextUpdate(IPSerwer=SimpleLabels.IPSerwer, item1=item1, item2=item2)
                            playCG(IPSerwer=SimpleLabels.IPSerwer)
                            nextRow = currentRow + 1
                            self.tableWidget_labelsText.selectRow(nextRow)
                    except:
                        print('takeCommandAutoNieparszysta error')

        else:
            if selectItem1 == None and selectItem2 == None:
                None
            else:
                if dataList != "''" and selectItem1 == None and selectItem2 == None:

                    # check data items in files in server
                    if dataRetriveCG(SimpleLabels.IPSerwer)[0] == "a=['":
                        item1 = ''
                    else:
                        item1 = dataRetriveCG(SimpleLabels.IPSerwer)[0]

                    if dataRetriveCG(SimpleLabels.IPSerwer)[1] == "a=['":
                        item2 = ''
                    else:
                        item2 = dataRetriveCG(SimpleLabels.IPSerwer)[1]

                    # send to engine and play
                    item1 = item1.replace('\\', '\\\\')
                    item2 = item2.replace('\\', '\\\\')

                    sendTextUpdate(IPSerwer=SimpleLabels.IPSerwer, item1=item1, item2=item2)
                    playCG(IPSerwer=SimpleLabels.IPSerwer)
                else:
                    try:
                        # check data items from table
                        table = self.tableWidget_labelsText
                        if table.item(currentRow, 0) == None:
                            item1 = ''
                        else:
                            item1 = table.item(currentRow, 0).text()

                        if table.item(currentRow, 1) == None:
                            item2 = ''
                        else:
                            item2 = table.item(currentRow, 1).text()

                        # send to engine and play
                        item1 = item1.replace('\\', '\\\\')
                        item2 = item2.replace('\\', '\\\\')

                        sendTextUpdate(IPSerwer=SimpleLabels.IPSerwer, item1=item1, item2=item2)
                        playCG(IPSerwer=SimpleLabels.IPSerwer)

                        # send to global
                        SimpleLabels.RowChanged = False

                        # store in serwer
                        dataStoreCG(SimpleLabels.IPSerwer, item1, item2)

                    except:
                        print('takeCommand in error')

    # take out button
    def nextCommand(self):
        nextCG(IPSerwer=SimpleLabels.IPSerwer)

    # for check line after line all items
    def checkCommand(self):
        currentRow = self.tableWidget_labelsText.currentRow()
        table = self.tableWidget_labelsText
        selectItem1 = table.item(currentRow, 0)
        selectItem2 = table.item(currentRow, 1)
        selectTab = self.tableWidget_labelsText.currentItem()

        if selectItem1 or selectItem2:
            currentRow = self.tableWidget_labelsText.currentRow()
            table = self.tableWidget_labelsText

            table = self.tableWidget_labelsText
            if table.item(currentRow, 0) == None:
                item1 = ''
            else:
                item1 = table.item(currentRow, 0).text()

            if table.item(currentRow, 1) == None:
                item2 = ''
            else:
                item2 = table.item(currentRow, 1).text()

            sendText(IPSerwer=SimpleLabels.IPSerwer, item1=item1, item2=item2)
            nexRow = currentRow + 1
            self.tableWidget_labelsText.selectRow(nexRow)
        else:
            currentRow = self.tableWidget_labelsText.currentRow()
            nexRow = currentRow + 1
            self.tableWidget_labelsText.selectRow(nexRow)

    # clear layer in caspar serwer
    def clearCommand(self):
        clearCG(IPSerwer=SimpleLabels.IPSerwer)
        dataRemoveCG(IPSerwer=SimpleLabels.IPSerwer)

        CasparCG.sendTemplateLoad(SimpleLabels.IPSerwer)
        SimpleLabels.RowChanged = True

        # reset currentRow after Clear Button
        SimpleLabels.AfterClear = True

        self.is_template == True
        if self.is_template == True:
            self.toolButton_clear.setText('CLEAR')

    # save to csv
    def writeCsv(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save File', QDir.homePath() + "/export.csv",
                                              "CSV Files(*.csv *.txt)")
        if path:
            with open(path, 'w') as stream:
                writer = csv.writer(stream, delimiter='\t')

                ## write file with header or no
                # headers = []
                # for column in range(self.tableWidget_labelsText.columnCount()):
                #     header = self.tableWidget_labelsText.horizontalHeaderItem(column)
                #     if header is not None:
                #         headers.append(header.text())
                #     else:
                #         headers.append("Column " + str(column))
                # writer.writerow(headers)

                for row in range(self.tableWidget_labelsText.rowCount()):
                    rowdata = []
                    for column in range(self.tableWidget_labelsText.columnCount()):
                        item = self.tableWidget_labelsText.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)

    # load from csv
    def loadCsv(self):
        try:
            path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')[0]
            items = []
            with open(path, 'r') as file:
                csvreader = csv.reader(file)
                for row in csvreader:
                    items.append(row)

            NumRows = len(items)

            for n in range(self.tableWidget_labelsText.rowCount()):
                self.tableWidget_labelsText.removeRow(n)
                numrow = self.tableWidget_labelsText.rowCount()
            for n in range(self.tableWidget_labelsText.rowCount()):
                self.tableWidget_labelsText.removeRow(n)
                numrow = self.tableWidget_labelsText.rowCount()
            for n in range(self.tableWidget_labelsText.rowCount()):
                self.tableWidget_labelsText.removeRow(n)
                numrow = self.tableWidget_labelsText.rowCount()

            for i in range(1, NumRows):
                self.add_emptyRow()
            if NumRows < 50:
                for i in range(50 - NumRows):
                    self.add_emptyRow()

            for i in range(NumRows):
                item = items[i]
                item = item[0].split('\t')

                for j in range(2):
                    if j == 0:
                        self.tableWidget_labelsText.setItem(i, j, QTableWidgetItem(str(item[0])))
                    if j == 1:
                        self.tableWidget_labelsText.setItem(i, j, QTableWidgetItem(str(item[1])))
        except:
            print('Open Error')

    # export to txt
    def writeTxt(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save File', QDir.homePath() + "/export.txt",
                                              "TXT Files(*.txt)")
        if path:
            data = []
            for row in range(self.tableWidget_labelsText.rowCount()):
                rowdata = []
                for column in range(self.tableWidget_labelsText.columnCount()):
                    item = self.tableWidget_labelsText.item(row, column)
                    if item is not None:
                        rowdata.append(item.text())
                    else:
                        rowdata.append('')
                    data.append(rowdata)

            with open(path, 'w') as file:
                for i in data:
                    file.writelines('{}\n'.format(*i))

    # export to server
    def writeData(self):
        data = []
        for row in range(self.tableWidget_labelsText.rowCount()):
            rowdata = []
            for column in range(self.tableWidget_labelsText.columnCount()):
                item = self.tableWidget_labelsText.item(row, column)
                if item is not None:
                    item_txt = item.text()
                    item_txt = item_txt.replace('\\t', '\t')
                    item_txt = item_txt.replace('\\n', '\n')
                    rowdata.append(item_txt)
                else:
                    rowdata.append('')
            data.append(rowdata)
        dataStoreTab(SimpleLabels.IPSerwer, data)

    # load from server
    def loadData(self):
        try:
            # convert str from file to list
            dataTab = dataRetriveTab(SimpleLabels.IPSerwer)
            dataTab = dataTab.replace('\\\\', '\\')
            dataTab = dataTab.replace('\\\\', '\\')
            dataTab = dataTab.split(sep=';#;')

            # number rows in list
            NumRows = len(dataTab)

            # delete rows
            for n in range(self.tableWidget_labelsText.rowCount()):
                self.tableWidget_labelsText.removeRow(n)
                numrow = self.tableWidget_labelsText.rowCount()
            for n in range(self.tableWidget_labelsText.rowCount()):
                self.tableWidget_labelsText.removeRow(n)
                numrow = self.tableWidget_labelsText.rowCount()
            for n in range(self.tableWidget_labelsText.rowCount()):
                self.tableWidget_labelsText.removeRow(n)
                numrow = self.tableWidget_labelsText.rowCount()

            # create rows
            for i in range(NumRows):
                self.add_emptyRow()
            if NumRows < 50:
                for i in range(50 - NumRows):
                    self.add_emptyRow()

            # put list in table
            for i in range(0, NumRows):
                item = dataTab[i][1:-1]
                item = item.split(', ')
                for j in range(2):
                    if j == 0:
                        none = None
                        if item[0] == "''":
                            self.tableWidget_labelsText.setItem(i, j, None)
                        else:
                            self.tableWidget_labelsText.setItem(i, j, QTableWidgetItem(item[0][1:-1]))
                    if j == 1:
                        if item[1] == "''":
                            self.tableWidget_labelsText.setItem(i, j, None)
                        else:
                            self.tableWidget_labelsText.setItem(i, j, QTableWidgetItem(item[1][1:-1]))
        except:
            print('Open Error')

    # connect parameters
    def serverConnect(self):
        IPserwer = self.lineEdit_enterIP.text()
        SimpleLabels.IPSerwer = IPserwer

        if self.toolButton_connect.text() == 'CONNECT' and self.lineEdit_enterIP.text() != '':
            try:
                client = Client()
                client.connect(IPserwer, 5250)
                self.lineEdit_enterIP.setStyleSheet("QLineEdit"
                                                    "{"
                                                    "border: 1px solid #777777;"
                                                    "border-radius: 6px;"
                                                    "background:green;"
                                                    "color:white"
                                                    "}")
                self.lineEdit_enterIP.setDisabled(True)
                self.toolButton_connect.setText('DISCONNECT')
                self.toolButton_clear.setDisabled(False)
                self.toolButton_takeOut.setDisabled(False)
                self.toolButton_take.setDisabled(False)
                self.actionimport.setDisabled(False)
                self.actionexport.setDisabled(False)
                SimpleLabels.RowChanged = False
                SimpleLabels.isConnectPush = True

            except Exception as e:
                print('Connecion error:', e)

        else:
            try:
                client = Client()
                client.connect(SimpleLabels.IPSerwer, 5250)
                response = client.send(BYE())
                SimpleLabels.IPSerwer = ''
                print(response)
                self.lineEdit_enterIP.setStyleSheet("QLineEdit"
                                                    "{"
                                                    "border: 1px solid #777777;"
                                                    "border-radius: 6px;"
                                                    "background:red;"
                                                    "color:white"
                                                    "}")
                self.lineEdit_enterIP.setDisabled(False)
                self.toolButton_connect.setText('CONNECT')
                self.toolButton_clear.setDisabled(True)
                self.toolButton_takeOut.setDisabled(True)
                self.toolButton_take.setDisabled(True)
                self.actionimport.setDisabled(True)
                self.actionexport.setDisabled(True)
                SimpleLabels.IPSerwer = ''
                SimpleLabels.isConnectPush = False

            except:
                print('Disconnection error')

    def stop_threads(self):
        self.thread.requestInterruption()
        self.thread.wait()
        self.ss_thread.requestInterruption()
        self.ss_thread.wait()

    def runLongTask(self):
        self.thread = QThread(parent=self)
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.start()

        self.toolButton_connect.setEnabled(False)

        self.thread.finished.connect(
            lambda: self.toolButton_connect.setEnabled(True)
        )
        self.worker.finished.connect(
            lambda: self.serverConnect()
        )
        self.worker.error.connect(
            lambda: self.toolButton_connect.setEnabled(True)
        )
        return

    def setProgressStatus(self):
        self.toolButton_connect.setEnabled(True)
        if SimpleLabels.isConnectPush == False:
            self.toolButton_connect.setText('CONNECT')
        self.lineEdit_enterIP.setText(self.IPSerwer)

    def server_down(self):
        self.lineEdit_enterIP.setStyleSheet("QLineEdit"
                                            "{"
                                            "border: 1px solid #777777;"
                                            "border-radius: 6px;"
                                            "background:red;"
                                            "color:white"
                                            "}")
        self.lineEdit_enterIP.setDisabled(False)

        if self.checkBox_manualConnect.isChecked():
            self.toolButton_connect.setText('CONNECT')
            self.toolButton_connect.setEnabled(True)
        else:
            self.toolButton_connect.setText('CASPAR DOWN')

        self.toolButton_clear.setDisabled(True)
        self.toolButton_takeOut.setDisabled(True)
        self.toolButton_take.setDisabled(True)
        self.actionimport.setDisabled(True)
        self.actionexport.setDisabled(True)
        SimpleLabels.isConnectPush = False

    def isInitialize(self):
        if SimpleLabels.is_template == False:
            self.toolButton_clear.setText('INITIALIZE')
        else:
            self.toolButton_clear.setText('CLEAR')

    def ssTreadKill(self):
        if self.checkBox_manualConnect.isChecked():
            print('ssTreadKill')

    def ss_checker(self):
        self.ss_thread = QThread()
        self.worker = SS_Worker()
        self.worker.moveToThread(self.ss_thread)
        self.ss_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.ss_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.ss_thread.finished.connect(self.ss_thread.deleteLater)
        self.worker.error.connect(self.ss_thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.worker.progress.connect(self.setProgressStatus)
        self.worker.progress.connect(self.isInitialize)
        self.worker.progress.connect(self.isManualConnect)
        self.worker.error.connect(self.isManualConnect)
        self.ss_thread.start()

        self.worker.finished.connect(
            lambda: self.toolButton_connect.setEnabled(True)
        )
        self.ss_thread.finished.connect(
            lambda: self.toolButton_connect.setEnabled(True)
        )
        self.worker.error.connect(
            lambda: self.toolButton_connect.setEnabled(False)
        )
        self.worker.error.connect(
            lambda: self.server_down()
        )
        self.worker.error.connect(
            lambda: self.isInitialize()
        )
        return
