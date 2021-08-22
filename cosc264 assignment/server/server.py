"""
Serverside Program for COSC264 Assignment 1

by Alexander Doyle
"""
import socket
import sys
from datetime import datetime


def startServer():
    """Function to start the server"""
    #we need to get the port number
    currentPort = int(input("Please Type and enter a port between 1024 and 64000:\n"))
    # check if the port number is valid
    if currentPort < 1024 or currentPort > 64000 or not(isinstance(currentPort, int)):
        print("Invalid port number") # error printed if port number is invalid
        sys.exit()
    else:# Socket is then created if port is valid
        buildSocket(currentPort)

def buildSocket(portNumber):
    """function for socket creation"""
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Tries to bind a port to the socket
    try:
        serverSocket.bind(('127.0.0.1', portNumber))
    except:
        print("An error occured while binding the socket to a port")
        serverSocket.close()
        sys.exit()
    serverSocket.settimeout(1)
    listenForConnection(serverSocket)



def listenForConnection(serverSocket):
    """Function for listening for new connections"""
    try:
        serverSocket.listen()
    except:
        serverSocket.close()
        print("An Error Occured listening for a connection")
        sys.exit()
    centralLoop(serverSocket)

def centralLoop(serverSocket):
    """Central Running loop for the program"""
    while True:
        print("-----------Server refreshed-----------")
        conn, addr = acceptConnection(serverSocket)
        readFileRequest(conn)


def acceptConnection(serverSocket):
    """Function to handle accepting new connections"""
    conn, addr = serverSocket.accept()
    print("[{}] Connection from {}".format(datetime.now(), addr))
    conn.settimeout(1)
    return conn, addr

def readFileRequest(conn):
    """repsonsible for reading from conn socket
    Need to add time out proper
    """
    try:
        data = conn.recv(264) # max filename length is 255 bytes(for linux)
    except:
        print("failed to recieve file request from client")
        conn.close()
        sys.exit()
    processFileRequest(data, conn)

def processFileRequest(data, conn):
    """Validates that the fileRequest is correct"""
    fileRequest = bytearray(data)
    if len(fileRequest) < 5:
        conn.close()
        print("Not enough data received for a valid fileRequest")
    elif(((fileRequest[0] << 8 )| (fileRequest[1])) != 0x497E):
        conn.close()
        print("Magic Number did not match, closing socket")
    elif(int(fileRequest[2]) != 1):
        conn.close()
        print("Incorrect file request version")
    elif(int(((fileRequest[3] << 8 )| (fileRequest[4]))) < 1
         or int(((fileRequest[3] << 8 )| (fileRequest[4]))) > 1024):
        conn.close()
        print(("Incorrect file name length, closing socket"))
    else:
        openFile(fileRequest,conn)

def openFile(fileRequest,conn):
    """Attempts to open file and read it"""
    filename = getFileName(fileRequest)
    fileData = None
    succesfullyOpened = True
    try:
        #opens file and reads the data
        rawFile = open(filename.decode('UTF-8'), 'rb')
        fileData = rawFile.read()
        rawFile.close()
    except:
        #if file cant be opened, succesfullyopened is false
        succesfullyOpened = False
    sendFileData(fileData, conn, succesfullyOpened)

def getFileName(fileRequest):
    """returns the file name from a file Request"""
    nameByteLength = int(((fileRequest[3] << 8 ) | (fileRequest[4])))
    return fileRequest[5:nameByteLength * 2]

def sendFileData(fileData,conn, succesfullyOpened):
    """sends the file data to a given socket"""
    packetToSend = buildPacket(fileData, succesfullyOpened)
    conn.send(packetToSend)
    conn.close()
    print("{} bytes transferred to client".format(len(packetToSend)))

def buildPacket(fileData, succesfullyOpened):
    """Builds the packet to be returned"""
    statusCode = 0
    #this checks if the file was succesfully opened
    if succesfullyOpened:
        statusCode = 1

    #Packet Header
    returnArray = bytearray([
        (0x497E & 0xFF00) >> 8
        , (0x497E & 0xFF) >> 0
        , 2
        , statusCode
    ])
    # adds fileLength if file exsists
    if succesfullyOpened:
        returnArray.append((len(fileData) & 0xFF000000) >> 24)
        returnArray.append((len(fileData) & 0xFF0000) >> 16)
        returnArray.append((len(fileData) & 0xFF00) >> 8)
        returnArray.append((len(fileData) & 0xFF) >> 0)
    #this adds the file data
        for byte in fileData:
            returnArray.append(byte)

    return returnArray

if __name__ == '__main__':
    startServer()