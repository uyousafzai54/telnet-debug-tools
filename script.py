import sys
import socket
import fcntl, os
import errno
from time import sleep
import re
import unicodedata
import math
import numpy as np
import matplotlib.pyplot as plt


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")


plt.axis([0, 800, 0, 180])
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8889  # Port to listen on (non-privileged ports are > 1023)
lis = []
lis2 = []
lis3 = []
prev = b''
proc = ''
angCnt = 0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK)
    print("connected!")
    print("umar")
    s.send(b"\n")
    s.send(b"mag\n")
    s.send(b"mag 20\n")
    s.send(b"mag rate 100 0\n")
    s.send(b"mag start 100 5000 2 64\n")
    cnt = 0;
    ct = 0;
    while True:
        msg = s.recv(8192)
        # except socket.error as e:
        #     err = e.args[0]
        #     if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
        #         sleep(1)
        #         print('No data available')
        #         cnt+=1
        #         if cnt > 10:
        #             break
        #         else:
        #             continue
        #     else:
        #         # a "real" error occurred
        #         print(e)
        #         sys.exit(1)
        # else:
        ct+=1
        tl = (msg.decode("utf-8"))
        # print(tl, end="")
        ansi_escape_8bit = re.compile(
            br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])'
        )
        result = remove_control_characters((ansi_escape_8bit.sub(b'', msg)).decode("utf-8"))
        result = result.replace('/[\u001b\u009b][[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><]/g', '')
        if b'\x1b[0m' in msg:
            if prev!='':
                proc = prev + msg[0:msg.rfind(b'\x1b[0m')]
                if b'.' in proc:
                    lis2.append(re.sub("[^0-9.\-,]","",remove_control_characters((ansi_escape_8bit.sub(b'', proc)).decode("utf-8"))))
                    try:
                        floats = [float(x) for x in lis2[len(lis2)-1].split(",")]
                        if not (math.abs(floats[0]) > 100 or math.abs(floats[1]) > 100):
                            ang = math.degrees(math.atan2(floats[1], floats[0]))
                            ang = (ang+360) % 360
                            print("angle is: "+str(ang))
                            #plt.scatter(angCnt, ang)
                            #plt.pause(0.05)
                            angCnt += 1
                            floats.append(ang)
                            lis3.append(floats)
                    except: 
                        #print(lis2[len(lis2)-1])
                        a = 1
            prev = msg[(msg.rfind(b'\x1b[0m')+4):len(msg)-1]
        else:
            prev = prev + msg
        #prev = prev + result
        res = result.split(',')
        #print(tl, end="")
        #result = ansi_escape.sub('', result)
        #lis.append(result)
         
    # print("total messages were: "+str(ct))
    # print("\n\n\n")
    for i in range (0, len(lis3)):
        print(lis3[i])
    print("\n**********************\n")
    # print(lis2)
    print(len(lis2))
    #plt.show()
    s.close()
    # s.sendall(b"mag")
    # while True:
    #     data = s.recv(10000)
    #     print(data.decode("utf-8"))
    #     if not data:
    #         break
    # s.close()
