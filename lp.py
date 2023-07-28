
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





def main():
    win = pg.plot()

    #p1 = win.addPlot()
    data1 = [0*300]
    #curve1 = p1.plot(data1)
    ptr1 = 0    

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 8889  # Port to listen on (non-privileged ports are > 1023)
    sock.connect((HOST, PORT))
    sock.setblocking(1)
    sock.settimeout(1.5)
    #sock.send(b"mag 20\n\nmag mode 1\n\nmag rate 100 0\n\nmag ser 0\n\n")
    sock.send(b"mag 20\n\nmag rate 0 2 1\n\nmag ser 0\n\n")
    sock.send(b"mag start 100 10000 2 64\n")

    print("messages commands sent")
    while True:
        try:
            data = sock.recv(131072)
            if not data:
                ConClosed +=1
            else:
                print("Received %d bytes:" % (len(data)))
                result = (data.decode("utf-8"))
                matches = re.findall(r'[-]?\d+\.\d*[,][-]?\d+\.\d*[,][-]?\d+\.?\d*', result)
                for k in range(len(matches)):
                    components = matches[k].split(',')
                    deg = math.degrees(math.atan2(float(components[1]), float(components[0])))
                    row = [deg]
                    # if abs(lastAngle-deg)>0.2:
                    #     print("large angle diff with prev")
                    #     #print(components)
                    #dataCounter += 1
                    lastAngle = deg
                    matches[k] = matches[k] + ", "+str(deg)
                    #allCSVData.append([float(components[0]), float(components[1]), float(components[2]), deg])
                    
                    data1[:-1] = data1[1:]  # shift data in the array one sample left
                            # (see also: np.roll)
                    data1[-1] = deg
                    #curve1.setData(data1)
                    ptr1 += 1
                    
            win.plot(data1)
            QApplication.processEvents()
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
    print("done")


if __name__ == '__main__':
    main()
    


