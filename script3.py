import matplotlib.pyplot as plt
import time
import threading
import socket, errno, time
import re
import math
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8889  # Port to listen on (non-privileged ports are > 1023)
sock.connect((HOST, PORT))
sock.setblocking(1)
sock.send(b"mag 20\n\nmag mode 1\n\nmag rate 100 0\n\n")
sock.send(b"mag start 100 5000 2 64\n")

plotData = []

# This just simulates reading from a socket.
def data_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 8889  # Port to listen on (non-privileged ports are > 1023)
    sock.connect((HOST, PORT))
    sock.setblocking(1)
    sock.send(b"mag 20\n\nmag mode 1\n\nmag rate 100 0\n\n")
    sock.send(b"mag start 100 5000 2 64\n")
    # sock.send(b"\n")
    # sock.send(b"\n")
    i = 0
    allMatches = []
    ConClosed = 0
    dataCounter = 0
    while True:
        try:
            data = sock.recv(65536)
            print(data)
            if not data:
                #print("connection closed")
                ConClosed +=1
                #sock.close()
            else:
                print("Received %d bytes:" % (len(data)))
                result = (data.decode("utf-8"))
                matches = re.findall(r'\d+\.\d*[,]\d+\.\d*[,]\d+\.?\d*', result)
                # if len(data) == 121:
                #     print(result)
                allMatches.append(matches)
                for k in range(len(matches)):
                    components = matches[k].split(',')
                    plotData.append(math.atan2(components[2], components[1]))
                #print(result)
                #print(matches)
        except socket.error as e:
            if e.args[0] == errno.EWOULDBLOCK: 
                print('EWOULDBLOCK')
                #i+=1
                #time.sleep(1)           # short delay, no tight loops
            else:
                print(e)
                print("bye error")
            print("bro")

if __name__ == '__main__':
    thread = threading.Thread(target=data_listener)
    thread.daemon = True
    thread.start()
    #
    # initialize figure
    # plt.figure() 
    # ln, = plt.plot([])
    # plt.ion()
    # plt.show()
    # while True:
    #     plt.pause(0.001)
    #     ln.set_xdata(range(len(plotData)))
    #     print(len(plotData))
    #     ln.set_ydata(plotData)
    #     plt.draw()