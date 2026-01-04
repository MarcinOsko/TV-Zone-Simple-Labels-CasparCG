from amcp_pylib.core import Client
from amcp_pylib.module import CG_PLAY, CG_NEXT, CG_ADD, CG_CLEAR, CG_UPDATE, CG_INFO, INFO, CG_REMOVE, DATA_STORE, DATA_RETRIEVE, DATA_LIST, DATA_REMOVE

from PyQt6.QtWidgets import QMainWindow, QDialog, QMessageBox, QTableWidgetItem, QLineEdit
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QModelIndex


def sendText(IPSerwer, item1, item2):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        response = client.send(CG_ADD(video_channel=1, layer=20, cg_layer=1, template='SimpleLabels_template', play_on_load=1,
                                      data='<templateData>\
                                                <componentData id="_title">\
                                                    <data id="text" value="{}" />\
                                                </componentData>\
                                                <componentData id="_subtitle">\
                                                    <data id="text" value="{}" />\
                                                </componentData>\
                                            </templateData>'.format(item1, item2)))
        print(response)
        return
    except:
        print("sendText error")



def sendTextUpdate(IPSerwer, item1, item2):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        response = client.send(CG_UPDATE(video_channel=1, layer=20, cg_layer=0,
                                      data='<templateData>\
                                                <componentData id="_title">\
                                                    <data id="text" value="{}" />\
                                                </componentData>\
                                                <componentData id="_subtitle">\
                                                    <data id="text" value="{}" />\
                                                </componentData>\
                                            </templateData>'.format(item1, item2)))
        print(response)
        return
    except:
        print("sendTextUpdate error")



def sendTemplateLoad(IPSerwer):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        response = client.send(CG_ADD(video_channel=1, layer=20, cg_layer=1, template='SimpleLabels_template', play_on_load=0))

        print(response)
        return
    except:
        print("sendTemplateLoad error")



def getInfo(IPSerwer):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        response = client.send(INFO(video_channel=1, layer=20))

        print(response)
        return
    except:
        print("getInfo error")



def nextCG(IPSerwer):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        response = client.send(CG_NEXT(video_channel=1, layer=20, cg_layer=1))

        print(response)
        return
    except:
        print("nextCG error")



def playCG(IPSerwer):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        response = client.send(CG_PLAY(video_channel=1, layer=20, cg_layer=1))

        print(response)
        return
    except:
        print("playCG error")



def clearCG(IPSerwer):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        response = client.send(CG_CLEAR(video_channel=1, layer=20))

        print(response)
        return
    except:
        print("clearCG error")



def removeCG(IPSerwer):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        response = client.send(CG_REMOVE(video_channel=1, layer=20, cg_layer=1))

        print(response)
        return
    except:
        print("removeCG error")



def dataStoreCG(IPSerwer, firstLine, secondLine):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        response = client.send(DATA_STORE(name='firstLine', data=str(firstLine)))
        response = client.send(DATA_STORE(name='secondLine', data=str(secondLine)))
        print(response)
        return
    except:
        print("dataStoreCG error")



def dataRetriveCG(IPSerwer):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        retrive1 = client.send(DATA_RETRIEVE(name='firstLine'))
        retrive2 = client.send(DATA_RETRIEVE(name='secondLine'))
        retriveFirstLine = str(retrive1)[24:-48]
        retriveSecondLine = str(retrive2)[24:-48]
        return retriveFirstLine, retriveSecondLine
    except:
        print("dataRetriveCG error")



def dataRemoveCG(IPSerwer):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        retrive1 = client.send(DATA_REMOVE(name='firstLine'))
        retrive2 = client.send(DATA_REMOVE(name='secondLine'))
        print(retrive1)
        print(retrive2)
        return
    except:
        print("dataRemoveCG error")



def dataListCG(IPSerwer):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        retrive = str(client.send(DATA_LIST()))[23:-43]
        return retrive
    except:
        print("dataListCG error")



def dataStoreTab(IPSerwer, dataTab):
    text = ''
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        for item in dataTab:
            text += str(item) + ';#;'

        response = client.send(DATA_STORE(name='dataTab', data=text))
        print(response)
        return response
    except:
        print("dataStoreCG error")



def dataRetriveTab(IPSerwer):
    try:
        client = Client()
        client.connect(str(IPSerwer), 5250)
        dataTab = client.send(DATA_RETRIEVE(name='dataTab'))
        dataTab = str(dataTab)[24:-51]
        return dataTab
    except:
        print("dataRetriveTab error")

