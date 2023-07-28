from nis import match
import socket, errno, time
import matplotlib.pyplot as plt
import re
import pandas as pd
import math
import numpy
import pyqtgraph as pg
import time
from typing import List

def parse_mag_data(decoded_string: str) -> List[List[float]]:
    res = []
    matches = re.findall(r'[-]?\d+\.\d*[,][-]?\d+\.\d*[,][-]?\d+\.?\d*', decoded_string)
    for k in range(len(matches)):
        components = matches[k].split(',')
        res.append([float(components[0]), float(components[1]), float(components[2])])
    return res

def get_data(csv_title):

    # default mag commands
    MAG_RATE = 100
    MAG_MODE = 1
    MAG_TIME_MS = 30000

    # create and connect to socket
    start = time.perf_counter()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 8889  # Port to listen on (non-privileged ports are > 1023)
    sock.connect((HOST, PORT))
    sock.setblocking(1)
    sock.settimeout(1.5)

    # create and send mag commands to start collecting data
    MAG_FINAL_COMMAND = "mag 20\n\nmag mode " +str(MAG_MODE)+"\n\nmag rate "+str(MAG_RATE)+" 0\n\nmag ser 0\n\ncli colors off\n\n"
    sock.send(MAG_FINAL_COMMAND.encode('UTF-8'))
    MAG_START = "mag start "+str(MAG_RATE)+" "+str(MAG_TIME_MS)+" 2 64\n\n"
    #sock.send(b"mag 20\n\nmag rate 0 2 1\n\nmag ser 0\n\ncli colors off\n\n")
    sock.send(MAG_START.encode('UTF-8'))


    i = 0
    allMatches = []
    ConClosed = 0
    dataCounter = 0
    dataCounterArr = [0]
    sliderCounter = 0

    #empty data frame
    df = pd.DataFrame()
    # create plot
    plt.ion() # <-- work in "interactive mode"
    fig, ax = plt.subplots()
    fig.canvas.set_window_title('Live Chart')
    ax.set_title("Magnetomer Degree vs Sample")
    lastAngle = -1


    allDeg = []




    allCSVData = []

    #pgPlot = pg.plot(df)


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
                    allDeg.append(deg)
                    if abs(lastAngle-deg)>0.2:
                        print("large angle diff with prev")
                        print(components)
                    df = pd.concat([df, pd.DataFrame(row)])
                    df.apply(lambda x: x-x.mean())
                    ax.clear()
                    ax.plot(dataCounterArr, df, color="black")
                    ls = dataCounterArr[-300:]
                    ax.set_xlim(ls[0], ls[len(ls)-1])
                    dataCounter += 1
                    dataCounterArr.append(dataCounter)
                    lastAngle = deg
                    matches[k] = matches[k] + ", "+str(deg)
                    allCSVData.append([float(components[0]), float(components[1]), float(components[2]), deg])
                    #fig.canvas.blit(fig.bbox)
                    # flush any pending GUI events, re-painting the screen if needed
                    #fig.canvas.flush_events()
                allMatches.append(matches)
                #print(dataCounter)
                #print(result)
                #print(matches)
            plt.pause(0.01) 
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
            return
    end = time.perf_counter()
    print("time elapsed is: "+str(end-start))
    maxY = numpy.max(df, axis=0)
    minY = numpy.min(df, axis=0)
    maxY = maxY.tolist()
    minY = minY.tolist()
    delta = maxY[0]-minY[0]
    #ax.plot(dataCounterArr[-5000:], allDeg, color="black")
    print("delta between max and min: %f" % (delta))
    print(len(allCSVData))
    csvDataFrame = pd.DataFrame(allCSVData)
   #csvDataFrame.to_csv(csv_title, index=False)
    sock.send(b"")
    sock.close()


def main():
    for i in range(1):
        get_data("closed-oct6-"+str(i+1)+".csv")
    #get_data("bw3-cont.csv")



if __name__ == "__main__":
   main()