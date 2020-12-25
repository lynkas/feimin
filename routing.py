import json
import socket
from multiprocessing import Process
import time

# This function is used to read a .json file and convert it into a dict
def read_file(filename):
    with open(filename) as f:
        nodes = f.read()
        return json.loads(nodes)

# Define a protocol that contains three components(node name, direction vector and port number)for sender
def encapsulate(node_name, dv, port):
    return ('node_name '+node_name+'\r\n'+'dv '+json.dumps(dv)+'\r\n'+'port '+str(port)).encode()

# help sender analyze the protocol
def decapsulate(capsule):
    transfer_table = capsule.decode()
    info = transfer_table.split("\r\n")
    node_name = info[0][10:]
    dv = info[1][3:]
    dv = json.loads(dv)
    port = int(info[2][5:])
    return node_name,dv,port

# Use the socket to receive the packet
def receiver(s:socket.socket):
    message, address = s.recvfrom(1024)
    return decapsulate(message)

# Use the socket to receive the packet
def sender(s:socket.socket, node_name, dv, port):
    message = encapsulate(node_name, dv, port)
    s.sendto(message, ('127.0.0.1',port))

# Use the bellman-ford algorithm to update the transform table
def update(name, received_table, local_table,file,my_name, adjancent_node):

    flag = False
    # flag is used to decide whether table should be retransmitted.
    for received_name in received_table:
        if received_name == my_name:
            continue
        if received_name in local_table:
            if local_table[received_name]['distance']>adjancent_node[name]+received_table[received_name]['distance']:
                local_table[received_name]['distance'] = adjancent_node[name]+received_table[received_name]['distance']
                local_table[received_name]['next_hop'] = name
                flag=True
        else:
            local_table[received_name] = {}
            local_table[received_name]['distance'] = adjancent_node[name]+received_table[received_name]['distance']
            local_table[received_name]['next_hop'] = name
            flag=True
            file.write('Node '+received_name+' is a newly added node.\n')
    return local_table, flag

# Simulate a server
def server(name,port_number,adjancent_node,adjancent_route):
    file = open(name + '.txt', 'w')
    file.write('node ' + name + '\n')
    file.write('--------------------------------------------------\n')
    step = 1
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.settimeout(0.1)
    s.bind(("127.0.0.1", port_number))
    # dv = {name:{'distance':0,'next_hop':name}}
    dv={}
    for i in adjancent_node:
        dv[i] = {'distance':adjancent_node[i],'next_hop':i}
    file.write('local dv in node '+name+' is :\n')
    file.write(json.dumps(dv)+'\n')
    file.write('\n')
    route = adjancent_route
    time_to_wait = 10
    time.sleep(1)
    for node_name in route:
        sender(s,name,dv,route[node_name])

    # time_to_wait is used to decide when to exit the program.
    while time_to_wait!=0:
        try:
            node_name,received_dv,_=receiver(s)
            file.write('step '+str(step)+'\n')
            step += 1
            file.write('From node '+node_name+'\n')
            file.write(json.dumps(received_dv)+'\n')

            dv,flag = update(node_name,received_dv,dv,file,name,adjancent_node)
            if flag:
                file.write('Current DV:\n')
                file.write(json.dumps(dv)+'\n')
            else:
                file.write('No update.\n')
            file.write('\n')

            time_to_wait=10
            if flag:
                for node_name in route:
                    sender(s, name, dv, route[node_name])
        except socket.timeout:
            time_to_wait-=1
            # if the socket have not received the socket after 0.1 second, the the program will end.

    file.write('Final dv is: '+json.dumps(dv))
    file.close()
    s.close()

if __name__ == '__main__':
    nodes = read_file("new_node.json")
    port_base = 20000
    process_list=[]
    # process is used to record the different process
    route = {}
    # this dict is used to store port number.
    for i in nodes:
        route[i]=port_base
        port_base+=1
    for i in nodes:
        process = Process(target=server,args=(i,route[i],nodes[i],{x:route[x] for x in nodes[i]}))
        process_list.append(process)
        process.start()
    for i in process_list:
        i.join()