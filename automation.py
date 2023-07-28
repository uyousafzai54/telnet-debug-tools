from audioop import avg
from base64 import decode
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


# version 1.0:
# todo: add live graphing while plotting and support for more stats collection at the en

# default mag command values
MAG_RATE = 100
MAG_MODE = 1
MAG_TIME_MS = 10000

# global vars
matrixA = matrixB = None
calibrateData = ''

def parse_mag_data(decoded_string: str) -> List[List[float]]:
    res = []
    matches = re.findall(r'[-]?\d+\.\d*[,][-]?\d+\.\d*[,][-]?\d+\.?\d*', decoded_string)
    for k in range(len(matches)):
        components = matches[k].split(',')
        res.append([float(components[0]), float(components[1]), float(components[2])])
    return res

def get_data() -> pd.DataFrame:
    # global calibration vars
    global calibrateData, matrixA, matrixB

    # create and connect to socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 8889  # Port to listen on (non-privileged ports are > 1023)
    sock.connect((HOST, PORT))
    sock.setblocking(1)
    sock.settimeout(1.5)

    # create and send mag commands to start collecting data
    MAG_FINAL_COMMAND = "mag 20\n\nmag mode " +str(MAG_MODE)+"\n\nmag rate "+str(MAG_RATE)+" 0\n\nmag ser 0\n\ncli colors off\n\n"
    MAG_START = "mag start "+str(MAG_RATE)+" "+str(MAG_TIME_MS)+" 2 64\n\n"
    MAG_START_NEW_FW = "mag 20\n\nmag rate 0 3 1\n\nmag ser 0\n\ncli colors off\n\nmag start 150 3000 2 64"

    # send start command based on FW version
    # sock.send(MAG_START_NEW_FW.encode('UTF-8'))
    sock.send(MAG_FINAL_COMMAND.encode('UTF-8'))
    sock.send(MAG_START.encode('UTF-8'))

    #empty data frame
    df = pd.DataFrame()

    #array for all csv data
    allDataRows = []
    allCSVData = []

    #var for range of data (min-max)
    dataRange = -1

    #var for storing last angle to filter out badly parsed data
    lastAngle = -1


    while True:
        try:
            data = sock.recv(131072)
            if not data:
                print("connection closed")
            else:
                #print("Received %d bytes:" % (len(data)))
                decoded_string = (data.decode("utf-8"))
                # print(decoded_string)
                matches = parse_mag_data(decoded_string=decoded_string)

                for k in range(len(matches)):
                    deg = math.degrees(math.atan2(abs(float(matches[k][1])), abs(float(matches[k][0]))))
                    row = [deg]
                    
                    # check whether to calibrate
                    if calibrateData != '':
                        # matlab: calibratedData = (x-B)*A where is x is raw data
                        matrixData = numpy.matrix([float(matches[k][0]), float(matches[k][1]), float(matches[k][2])])
                        calibratedMatrix = numpy.matmul(numpy.subtract(matrixData, matrixB), matrixA)
                        deg = math.degrees(math.atan2(abs(float(calibratedMatrix.item((0,1)))), abs(float(calibratedMatrix.item((0,0))))))
                        row = [deg]

                    if not(abs(lastAngle-deg)>100):
                        allDataRows.append(row)
                        allCSVData.append([float(matches[k][0]), float(matches[k][1]), float(matches[k][2]), deg])
                    lastAngle = deg
        except socket.error as e:
            if e.args[0] == errno.EWOULDBLOCK: 
                print('EWOULDBLOCK')
                #i+=1
                #time.sleep(1)           # short delay, no tight loops
            else:
                break
        # quit command for indv run
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            return

    # no data collected from socket, warn the user
    if (dataRange == -1 and lastAngle == -1) or pd.DataFrame(allDataRows).size == 0:
        print("WARNING: no data collected during this run, restart nustool if problem persists")

    df = pd.DataFrame(allDataRows)
    df.apply(lambda x: x-x.mean())
    sock.send(b"")
    sock.close()

    #calculate delta between max and min
    maxY = numpy.max(df, axis=0).tolist()
    minY = numpy.min(df, axis=0).tolist()
    if len(maxY) > 0 and len(minY) > 0:
        dataRange = maxY[0] - minY[0]
    
    #return plot dataframe, csv dataframe and dataRange
    return df, pd.DataFrame(allCSVData), dataRange

def plot(numberOfRuns: int):
    # allow user to change default config
    defaultConfig = input("Start with default config?: ")
    if defaultConfig != '':
        global MAG_RATE, MAG_MODE, MAG_TIME_MS
        MAG_RATE = int(input("Enter sampling rate (Hz): " or "100"))
        MAG_MODE = int(input("Enter mode: " or "1"))
        MAG_TIME_MS = int(input("Enter time in ms: " or "10000"))

    # calibrate data
    global calibrateData, matrixA, matrixB
    calibrateData = input("Calibrate data? (Enter to skip): ")
    if calibrateData != '':
        matrixA = input("Input matrix 3x3 A as numpy matrix string: ")
        matrixB = input("Input matrix 1x3 b as numpy matrix string: ")

    # calibrate data if A and B are not empty
    if matrixA != None and matrixB != None:
        matrixA = numpy.matrix(matrixA)
        matrixB = numpy.matrix(matrixB)
    
    fig, ax = plt.subplots()
    # fig.canvas.set_window_title('Live Chart')
    ax.set_title("Magnetomer Degree vs Sample")

    frames = []
    csvDataFrames = []
    legend = []
    runAverages = []
    avgRange = 0

    for i in range(numberOfRuns):
        # print console message
        print("\n\nstarting run "+str(i+1)+"...")

        # get dataframe and time it
        start = time.perf_counter()
        dataFrame, csvDataFrame, dataRange = get_data()
        end = time.perf_counter()

        print("time elapsed for current run was: "+str(end-start))
        avgRange += dataRange

        # calculate average of run and append to list
        avgOfRun = dataFrame.mean()

        # append data frames for plotting
        frames.append(dataFrame)
        csvDataFrames.append(csvDataFrame)
        runAverages.append(avgOfRun)

        print("avg of the current run was %.4f" % avgOfRun)

        input("Press Enter to continue...")

    print("\nplotting runs...")
    # create plot
    plt.ion() # <-- work in "interactive mode"

    plotted = []
    for i in range(len(frames)):
        temp1 = ax.plot(frames[i].index.values, frames[i])
        plotted.append(temp1)
        legend.append('Run '+str(i+1))

    # calculate average range and show using text box
    avgRange = avgRange / numberOfRuns
    textstr = "Avg Range: %.4f" % avgRange
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=8, verticalalignment='top', bbox=props)

    plt.legend(legend, loc='upper right')
    yMin, yMax = ax.get_ylim()
    while yMax != '' and yMin != '':
        ax.set_ylim(bottom=float(yMin), top=float(yMax))
        plt.pause(1)
        yMax = input("Input y-max to change range: " or None)
        yMin = input("Input y-min to change range: " or None)

    # allow user to customize title of generated plot
    customTitle = input("\nEnter a string to customize title or press enter to skip: ")
    if customTitle != '':
        ax.set_title(customTitle)

    csvDataFrame.to_csv(customTitle, index=False, mode="a")

    # allow user to calculate delta between two sets of runs that they choose 
    AJAR_CLOSED_DELTA = -1
    calculateDelta = input("\nPress y to calculate delta between two sets of runs or press enter to skip: ")
    if calculateDelta != '':
        firstSet = input("Enter run numbers separated by commas for first set: ")
        secondSet = input("Enter run numbers separated by commas for second set: ")

        firstSet = firstSet.split(',')
        secondSet = secondSet.split(',')

        if len(firstSet) == 0 or len(secondSet) == 0:
            print('Invalid sets!')

        else:
            firstSetAvg = 0
            for i in range(len(firstSet)):
                firstSetAvg += runAverages[int(firstSet[i])-1]
                ax.get_lines()[int(firstSet[i])-1].set_color("red")
                # plotted[i-1].set_color("red")
            firstSetAvg /= len(firstSet)

            secondSetAvg = 0
            for i in range(len(secondSet)):
                secondSetAvg += runAverages[int(secondSet[i])-1]
                ax.get_lines()[int(secondSet[i])-1].set_color("blue")
                # plotted[i-1].set_color("blue")
            secondSetAvg /= len(firstSet)
            
            # print delta to console and display on plot
            AJAR_CLOSED_DELTA =  abs(firstSetAvg-secondSetAvg)
            print("delta between the two sets is: %.4f" % abs(firstSetAvg-secondSetAvg))
            textstr = "Ajar vs Closed Delta: %.4f" % abs(firstSetAvg-secondSetAvg)
            # these are matplotlib.patch.Patch properties
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.05, 0.90, textstr, transform=ax.transAxes, fontsize=8, verticalalignment='top', bbox=props)

    # calculate max-min channel size
    channelSize = input("\nPress y to calculate channel size: ")
    if channelSize != '':
        firstSet = input("Enter run numbers separated by commas for set: ")
        firstSet = firstSet.split(',')


        dataPointsLength = int(input("Enter length of data points: "))

        avgFirstNPoints = []
        for i in range(len(firstSet)):
            idx = int(firstSet[i])-1
            avgFirstNPoints.append(float(frames[idx].iloc[0:dataPointsLength].mean()))
        
        textRangeMinMaxDiff = "Min-Max Channel: %.4f" (max(avgFirstNPoints)-min(avgFirstNPoints))
        ax.text(0.05, 0.65, textRangeMinMaxDiff, transform=ax.transAxes, fontsize=8, verticalalignment='top', bbox=props)
    
    # calculate delta percentage
    deltaPerc = input("\nPress y to calculate delta percentage or press enter to skip: ")
    if deltaPerc != '':
        firstSet = input("Enter run numbers separated by commas for set: ")
        firstSet = firstSet.split(',')


        dataPointsLength = int(input("Enter length of data points: "))

        deltaPercArr = []
        rangeHigh = -1
        rangeLow = 10000000
        for i in range(len(firstSet)):
            idx = int(firstSet[i])-1
            diff = frames[idx].iloc[:dataPointsLength].mean() - frames[idx].iloc[-dataPointsLength:].mean()
            rangeHigh = max(rangeHigh, float(frames[idx].iloc[:dataPointsLength].mean()), float(frames[idx].iloc[-dataPointsLength:].mean()))
            rangeLow = min(rangeLow, float(frames[idx].iloc[:dataPointsLength].mean()), float(frames[idx].iloc[-dataPointsLength:].mean()))
            print("diff is: "+str(diff))
            deltaPercArr.append(abs(diff))

        deltaPercAvg = 0
        for i in range(len(deltaPercArr)):
            deltaPercAvg += deltaPercArr[i]
        deltaPercAvg /= len(deltaPercArr)

        print("average drift was: "+str(deltaPercAvg))

        finalPerc = ((deltaPercAvg/AJAR_CLOSED_DELTA)*100)
        print("The delta percentage is %.4f " % finalPerc)

        # print delta to console and display on plot
        textStrPerc = "Percentage of Delta %.4f" % finalPerc
        # display drift
        textBoltDrift = "Lock/Unlock Drift %.4f" % deltaPercAvg
        # range high and range low
        textRangeHigh = "Range High %.4f" % rangeHigh
        textRangeLow = "Range Low %.4f" % rangeLow

        textRangeMinMaxDiff = "Min-Max Channel %.4f" (rangeHigh-rangeLow)
        # delta of cycle Ranges
        textDeltaCycleRanges = "Range of Bolt Cycles %.4f" % abs(rangeHigh - rangeLow)
        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.85, textStrPerc, transform=ax.transAxes, fontsize=8, verticalalignment='top', bbox=props)
        ax.text(0.05, 0.80, textBoltDrift, transform=ax.transAxes, fontsize=8, verticalalignment='top', bbox=props)
        # ax.text(0.05, 0.75, textRangeHigh, transform=ax.transAxes, fontsize=8, verticalalignment='top', bbox=props)
        # ax.text(0.05, 0.70, textRangeLow, transform=ax.transAxes, fontsize=8, verticalalignment='top', bbox=props)
        ax.text(0.05, 0.65, textDeltaCycleRanges, transform=ax.transAxes, fontsize=8, verticalalignment='top', bbox=props)

    plt.show(block=True)


def main():
    runs = input("Enter number of runs: ")
    plot(numberOfRuns=int(runs))

if __name__ == "__main__":
   main()

   # 2.3228    2.3095   -2.7621
   # 0.9631 0 0; 0 2.0551 0; 0 0 0.5052

#    1.5822         0         0; 0    1.2995         0; 0         0    0.4864
#    2.8539    2.0017   -2.1651