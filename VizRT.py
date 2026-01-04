import socket
import sys

# Variable delacration
vizCommandPreffix = '0 MAIN_SCENE*TREE*$myText*GEOM*TEXT SET '
vizCommandSuffix = '\0'

newValue = "Obregon"


# This will call each function in turn
def main():
    talkToViz()


def talkToViz():
    ## Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening

    # this is my artist machine
    server_address = ('192.168.0.185', 6100)

    # connect to the engine in my case I am using the artist machine
    sock.connect(server_address)
    print("Connected")

    # The following two commands will work, pay close attention to the way they are written, one of them is commented while I tested the other one

    # sock.send(b'0 MAIN_SCENE*TREE*$myText*GEOM*TEXT SET TEGNA \0;')
    sock.send(vizCommandPreffix.encode() + newValue.encode() + vizCommandSuffix.encode())

    sock.close()


main()



##############

#
# # Weather update from URL with Pyton
# # Import necessary libraries
# from xml.dom import minidom
# import socket
# import sys
# import datetime
# import time
# from datetime import datetime
# # 'import urllib2
# import urllib.request
#
# # Var declaration
# dayCounter = 0
# dayCounter2 = 0
# weekReport = ()
# dayReport = ()
#
# # ---------------------------------------------------------------------------------------------------------------------
# HOST = '10.55.14.104'  # The remote host
# PORT = 6100  # The same port as used by the server
# socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket.connect((HOST, PORT))
#
#
# # --------------------
#
# def main():
#     readFeed()
#     printDays()
#     printHighTemps()
#     print('DONE')
#
#
# def readFeed():
#     global weekReport, dayReport
#     readXMLfromURL = urllib.request.urlopen(
#         "http://xml.customweather.com/xml?product=current_extended&latitude=27.964157&longitude=-82.452606&client=vizrt_test&client_password=t3mp")
#     wxMiguelXML = minidom.parse(readXMLfromURL)
#     weekReport = wxMiguelXML.getElementsByTagName("report")[0]
#     dayReport = weekReport.getElementsByTagName("forecast")
#
#
# def printDays():
#     global dayCounter
#     for i in dayReport:
#         juanCounter = 0
#         dayNamesArray = []
#         juanPreffix = '0 MAIN_SCENE*TREE*$day0' + str(dayCounter + 1) + '*GEOM*TEXT SET '
#         juanSuffix = '\0'
#         myDays = i.attributes["weekday"]
#         dayNames = myDays.value
#         dayNamesArray.append(dayNames)
#         socket.send(juanPreffix.encode() + dayNamesArray[juanCounter].encode() + juanSuffix.encode())
#         juanCounter = juanCounter + 1
#         dayCounter = dayCounter + 1
#
#
# def printHighTemps():
#     global dayCounter2
#     for j in dayReport:
#         juanCounter2 = 0
#         highTempsArray = []
#         juanPreffix2 = '0 MAIN_SCENE*TREE*$high_temp0' + str(dayCounter2 + 1) + '*GEOM*TEXT SET '
#         juanSuffix = '\0'
#         myHighs = j.attributes["high_temp"]
#         myHighTemps = myHighs.value
#         highTempsArray.append(myHighTemps)
#         socket.send(juanPreffix2.encode() + highTempsArray[juanCounter2].encode() + juanSuffix.encode())
#         juanCounter2 = juanCounter2 + 1
#         dayCounter2 = dayCounter2 + 1
#
#     socket.close()
#
#
# main()