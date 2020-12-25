import os,sys,socket,re
from time import sleep
from threading import Thread,Lock
from queue import Queue

socket.setdefaulttimeout(5)
# read file
def readpath2dict(filename):
    with open(filename, 'r') as file:
        c = file.read()
        lines=re.split('\r?\n',c)
        res={}
        minlengthdict={1:0}
        now=0

        for i in lines:
            i=i.strip()
            if i:
                if i and i.startswith('Node'):
                    now = int(i.split()[1])
                    res[now]={}
                else:
                    res[now][int(i.split()[0])]=int(i.split()[1])
                    minlengthdict[int(i.split()[0])]=float('inf')
        return res

filename=sys.argv[2]
# use the file
path=readpath2dict(filename)


node=int(sys.argv[1])
host = '127.0.0.1'
port=1000+node
node2socket={}
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1',port))
updateQueue=Queue()
# three locks, for sync
lock1=Lock()
lock2=Lock()
lock3=Lock()

sametime=-3
lastroutine={}

if node in path:
    nbr = path[node]
else:
    nbr={}

distance=dict(nbr)
rout={}

for i in nbr:
    rout[i]=i

# receive
def actRecv(s):
        recvThread(s)

def receive():
    while True:
        s.listen(0)
        try:
            conn, addr = s.accept()
        except:
            continue
        res = conRecv(conn)
        thisnode = protocol(res)
        lock1.acquire()
        node2socket[thisnode] = conn
        lock1.release()
        # to thread, receive all the time
        Thread(target=recvThread, args=(conn,)).start()


Thread(target=receive).start()


def recvThread(conn):
    while True:
        content = conRecv(conn)
        # deal with message to protocol
        protocol(content)

# receive message
def conRecv(conn):

    alll = b''
    last = b''
    try:
        while True:
            if last != b'\n':
                last = conn.recv(1)
                alll += last
            else:
                nxt = conn.recv(1)
                if nxt == b'\n':
                    break
                else:
                    alll += nxt
                    last = b''
    except:
        None
    return alll.decode().split('\n')

def protocol(mess:[]):
    n=0
    try:
        for i in mess:
            if i.startswith('ITS'):
                n+=1
                nodenum=int(i.split()[1])
            if i.startswith('AWY'):
                lock2.acquire()
                distance[nodenum]=int(i.split()[1])
                lock2.release()
                lock3.acquire()
                rout[nodenum]=nodenum
                lock3.release()
            if i.startswith('KNW'):
                knwnode=int(i.split()[1])
            if i.startswith('DIS'):
                knwdis=int(i.split()[1])
                if knwnode==node:
                    continue
                # Core, compare the distance
                if (knwnode in distance and distance[knwnode]>distance[nodenum]+knwdis) or (not knwnode in distance):
                    lock2.acquire()
                    distance[knwnode] = distance[nodenum] + knwdis
                    lock2.release()
                    lock3.acquire()
                    rout[knwnode]=nodenum
                    lock3.release()
        return nodenum

    except:
        return

def getPort(a):
    return int(a)+1000


def makeaddr(i):
    return ('127.0.0.1',getPort(i))

def sendto(n:int,mess:[]):
    ns=node2socket[n]
    nm='\n'.join(mess)
    nm+='\n\n'
    try:
        ns.sendall(nm.encode())
    except:
        None
# wait for all server up
sleep(1)
# start up
for i in nbr:
    ns=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ns.connect(makeaddr(i))

    lock1.acquire()
    node2socket[i]=ns
    lock1.release()
    Thread(target=actRecv,args=(ns,)).start()
    sendto(i, ['ITS ' + str(node), 'AWY ' + str(nbr[i])])

# send all distance
while True:
    for i in dict(node2socket):
        for n in dict(distance):
            sendto(i,['ITS '+str(node),'KNW '+str(n),'DIS '+str(distance[n])])
    if not lastroutine:
        lastroutine=dict(distance)
    else:
        if lastroutine==distance:
            sametime+=1
            if sametime>3:
                break
        else:
            lastroutine = dict(distance)
    # wait for message sync
    sleep(max(0.02*6,0.02*len(distance)))

# to file
output=''
for i in distance:
    output+="go to "+str(i)+", pass through "+str(rout[i])+", length is "+str(distance[i])+'\n'

with open(str(node)+'.txt','w+') as file:
    file.write(output)
# exit
os._exit(0)
