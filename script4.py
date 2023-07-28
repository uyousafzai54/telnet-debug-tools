from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QItemEditorCreatorBase
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore


import collections
import random
import time
import math
import numpy as np

from nis import match
import socket, errno, time
import matplotlib.pyplot as plt
import re
import pandas as pd
import math
import numpy

class DynamicPlotter():

    def __init__(self, sampleinterval=0.1, timewindow=10., size=(600,350)):
        # Data stuff
        self._interval = int(sampleinterval*1000)
        self._bufsize = int(timewindow/sampleinterval)
        self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)
        # PyQtGraph stuff
        self.app = QApplication([])
        self.plt = pg.plot(title='Dynamic Plotting with PyQtGraph')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'amplitude', 'V')
        self.plt.setLabel('bottom', 'time', 's')
        #self.curve = self.plt.plot(self.x, self.y, pen=(255,0,0))
        # QTimer
        self.timer = QtCore.QTimer()
        #self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def getdata(self):
        frequency = 0.5
        noise = random.normalvariate(0., 1.)
        new = 10.*math.sin(time.time()*frequency*2*math.pi) + noise
        return new

    def updateplot(self):
        self.databuffer.append( self.getdata() )
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)
        self.app.processEvents()

    def update_plot_data(self, y):
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append(y)  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.

    def run(self):
        self.app.exec()

def main():
    #app = pg.mkQApp()

    # Create remote process with a plot window
    plt = pg.plot()
    plt.addPlo
    import pyqtgraph.multiprocess as mp
    proc = mp.QtProcess()
    rpg = proc._import('pyqtgraph')
    plotwin = rpg.plot()
    curve = plotwin.plot(pen='y')

    # create an empty list in the remote process
    data1 = [0*100]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 8889  # Port to listen on (non-privileged ports are > 1023)
    sock.connect((HOST, PORT))
    sock.setblocking(1)
    sock.settimeout(1.5)
    try:
        data = sock.recv(65536)
    except socket.error as e:
        x=1
    #sock.send(b"mag 20\n\nmag mode 1\n\nmag rate 100 0\n\nmag ser 0\n\n")
    sock.send(b"mag 20\n\nmag rate 0 2 1\n\nmag ser 0\n\n")
    sock.send(b"mag start 100 2000 2 64\n")
    # sock.send(b"\n")
    # sock.send(b"\n")
    i = 0
    allMatches = []
    ConClosed = 0
    dataCounter = 0
    dataCounterArr = [0]


    lastAngle = -1



    allCSVData = []
    while True:
        try:
            data = sock.recv(131072)
            if not data:
                #print("connection closed")
                ConClosed +=1
                #sock.close()
            # if len(data)==121:
            #     result = (data.decode("utf-8"))
            #     if result.__contains__("Failed to post event to app task event queue"):
            #         break
            else:
                #print("Received %d bytes:" % (len(data)))
                result = (data.decode("utf-8"))
                matches = re.findall(r'[-]?\d+\.\d*[,][-]?\d+\.\d*[,][-]?\d+\.?\d*', result)
                for k in range(len(matches)):
                    components = matches[k].split(',')
                    deg = math.degrees(math.atan2(float(components[1]), float(components[0])))
                    row = [deg]
                    # if abs(lastAngle-deg)>0.2:
                    #     print("large angle diff with prev")
                    #     #print(components)
                    #print(row)
                    # df = pd.concat([df, pd.DataFrame(row)])
                    # df.apply(lambda x: x-x.mean())
                    #ax.plot(dataCounterArr, df)
                    dataCounter += 1
                    dataCounterArr.append(dataCounter)
                    lastAngle = deg
                    matches[k] = matches[k] + ", "+str(deg)
                    allCSVData.append([float(components[0]), float(components[1]), float(components[2]), deg])
                    data1[:-1] = data1[1:]
                    data1[-1] = deg
                    curve.setData(y=data1, _callSync='off')
                    QApplication.processEvents()
                allMatches.append(matches)
                #print(dataCounter)
                #print(result)
                #print(matches)
        except socket.error as e:
            if e.args[0] == errno.EWOULDBLOCK: 
                print('EWOULDBLOCK')
                #i+=1
                #time.sleep(1)           # short delay, no tight loops
            else:
                print(e)
                print("bye :(")
                break
        except Exception as e:
            print(e)
    # maxY = numpy.max(df, axis=0)
    # minY = numpy.min(df, axis=0)
    # maxY = maxY.tolist()
    # minY = minY.tolist()
    # delta = maxY[0]-minY[0]
    # print("delta between max and min: %f" % (delta))
    # print(len(allCSVData))
    # csvDataFrame = pd.DataFrame(allCSVData)
    # csvDataFrame.to_csv("data.csv")
    sock.send(b"")
    sock.close()

if __name__ == '__main__':
    main()