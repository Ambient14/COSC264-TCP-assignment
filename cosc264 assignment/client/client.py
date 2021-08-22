"""
Client side program for COSC 264 assignment 1

by Alexander Doyle
"""
import math
import os
import socket
import sys


def startClientside():
    """Main function that runs client"""
    ipAddressUser = input("Please enter the server IP:\n")
    serverAddress = getIpAddress(ipAddressUser)
    serverPort = getPortNumber()
    fileName = getFileName()
    clientSocket = createClientSocket()
    clientSocket.settimeout(1)
    connectToServer(clientSocket, serverAddress, serverPort)
    sendFileRequest(clientSocket, fileName)
    readFileResponse(clientSocket, fileName)


def getIpAddress(ipAddressUser):
    """Function to ask user for server ip"""
    try:
        returnTuple = socket.gethostbyname_ex(ipAddressUser)
        return returnTuple[2][0]
    except:
        print("Invalid IP address provided")
        sys.exit()


def getPortNumber():
    """Asks the user for the server port number"""
    currentPort = int(input("Please Type and enter a port between 1024 and 64000:\n"))
    # check if the port number is valid
    if currentPort < 1024 or currentPort > 64000 or not (isinstance(currentPort, int)):
        print("Invalid port number")
        sys.exit()
    else:
        return currentPort


def getFileName():
    """asks the user for the file they require from the server"""
    fileName = input("Please input the file you wish to retrieve from the server:\n")
    if fileName in os.listdir():
        print("This file already exists, exiting program")
        sys.exit()
    elif fileName == "":
        print("No input detected, exiting program")
        sys.exit()
    return fileName


def createClientSocket():
    """creates the client socket"""
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return clientSocket
    except:
        print("Failed to create socket")
        sys.exit()


def connectToServer(clientSocket, serverAddress, serverPort):
    """Connects client to the server"""
    try:
        clientSocket.connect((serverAddress, serverPort))
    except:
        print("Failed to connect to server")
        sys.exit()


def sendFileRequest(clientSocket, filename):
    """sends the server the file request"""
    fileRequest = bytearray([
        (0x497E & 0xFF00) >> 8  # magic num byte 1
        , (0x497E & 0xFF) >> 0  # magic num byte 2
        , 1  # type
        , (len(filename.encode()) & 0xFF00) >> 8  # filelength byte 1
        , (len(filename.encode()) & 0xFF) >> 0  # filelength byte 2
    ])
    # filename
    for byte in filename.encode():
        fileRequest.append(byte)
    clientSocket.send(fileRequest)


def readFileResponse(clientSocket, filename):
    """Function to read the file response from server"""
    try:
        data = clientSocket.recv(8)
    except:
        print("Failed to receive file request")
        clientSocket.close()
        sys.exit()
    dataArray = bytearray(data)
    if (((dataArray[0] << 8) | (dataArray[1])) != 0x497E):
        clientSocket.close()
        print("Invalid magic Number")
    elif dataArray[2] != 2:
        clientSocket.close()
        print("Invlaid Type")
    elif dataArray[3] == 0:
        clientSocket.close()
        print("File Does not exist")
    else:
        readFile(dataArray[4:], clientSocket, filename)


def readFile(dataLengthBytes, clientSocket, filename):
    """Function to read file"""
    dataLength = int(dataLengthBytes[0] << 24 | dataLengthBytes[1] << 16 | dataLengthBytes[2] << 8 | dataLengthBytes[3])
    newFile = open(filename, "wb")  # creates new file
    clientSocket.settimeout(1)  # sets file transfer timeout
    totalBytesRecieved = 0  # variable to hold how many bytes received
    for cycle in range(0, math.floor(dataLength / 4096)):  # loop for reading chunks of 4096 bytes and writing them
        totalBytesRecieved += 4096
        try:
            currentData = bytearray(clientSocket.recv(4096))
        except:
            print("An error occured while trying to read file data")
            clientSocket.close()
            sys.exit()
        writeFile(currentData, newFile)

    totalBytesRecieved += dataLength % 4096
    try:
        # Reads the final data bytes that dont fit in 4096 chunks
        finalData = bytearray(clientSocket.recv(dataLength % 4096))
    except:
        print("An error occured while trying to read file data")
        clientSocket.close()
        sys.exit()

    writeFile(finalData, newFile)
    print("-----------------------------------------------------")
    print("Recieved {} bytes from server, transfer complete".format(totalBytesRecieved))
    print("-----------------------------------------------------")
    newFile.close()


def writeFile(currentData, currentFile):
    """Writes data to file"""
    currentFile.write(currentData)


if __name__ == '__main__':
    startClientside()
