import random
import socket
import threading
from datetime import datetime
import pickle
import time

HOST = '10.152.13.188'
PORT = 65423
flag_ttl = 0
lock = threading.Lock()

class Threads:

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.peer_list = dict()

    def peer_list_init(self, hostIP_port):
        global ttl_val
        self.peer_list[hostIP_port] = {}
        self.peer_list[hostIP_port]['hostname'] = ""
        self.peer_list[hostIP_port]['cookie'] = 0
        self.peer_list[hostIP_port]['active'] = 0
        self.peer_list[hostIP_port]['TTL'] = 0
        self.peer_list[hostIP_port]['port_num'] = 0
        self.peer_list[hostIP_port]['number_reg'] = 0
        self.peer_list[hostIP_port]['recent_login'] = ""

    def cookie_gen(self, time_stamp):
        cookie = '_$_' + str(time_stamp) + '_$_' + str(random.randint(1, 101))
        return cookie

    def listner(self):
        self.s.listen()
        print("Listening at port:" + str(PORT))
        while True:
            conn, addr = self.s.accept()
            # collecting the time stamp immediately after the connection has been accepted
            time_stamp = datetime.now()
            hostIP_port = str(addr[0])
            t2 = threading.Thread(name="Service func", target=self.service, args=(conn, addr, hostIP_port, time_stamp))
            t2.start()

    def keepalive(self):
        while True:
            length = len(self.peer_list)
            time.sleep(1)
            lock.acquire()
            print(len(self.peer_list))
            try:
                if length > 0:
                    for ip, value in self.peer_list.items():
                            value['TTL'] -= 1
                            # print(ip,value['TTL'])
                            if value['TTL'] == 0:
                                print("Deleting peer" + str(ip) +  "as TTL expired\n")
                                del self.peer_list[ip]
                                print("current content")
                                print(self.peer_list)
                                length = len(self.peer_list)
            except:
                print("Empty DB")
            lock.release()


    def update_ttl(self, host_ip):
        for key, val in self.peer_list[host_ip].items():
            if key == 'TTL':
                lock.acquire()
                self.peer_list[host_ip][key] = 1000
                lock.release()

    def service(self, conn, addr, hostIP_port, time_stamp):
        global flag_ttl, ttl_val
        data = pickle.loads(conn.recv(1024))
        print("----------------THIS IS THE PROTOCOL THAT IS BEING SENT----------------")
        # print(data)
        print(data[3])

        hostIP_port = data[1]
        if int(data[0]) == 700:
            print("Updating keepalive ba dei")
            self.update_ttl(hostIP_port)
            conn.close()

        for k, v in self.peer_list.items():
            print("KEY:")
            print(k)
            print("VAL:")
            print(v)

        if int(data[0]) == 1:
            flag_ttl = 1
            if hostIP_port not in self.peer_list.keys():
                self.peer_list_init(str(hostIP_port))
                self.peer_list[hostIP_port]['cookie'] = self.cookie_gen(str(time_stamp))
            self.peer_list[hostIP_port]['hostname'] = data[1]
            self.peer_list[hostIP_port]['active'] = 1
            self.peer_list[hostIP_port]['TTL'] = 1000
            ttl_val = 20
            self.peer_list[hostIP_port]['port_num'] = data[2]
            self.peer_list[hostIP_port]['number_reg'] += 1
            self.peer_list[hostIP_port]['recent_login'] = str(time_stamp)
            if self.peer_list[hostIP_port]['cookie']:
                conn.sendall(self.peer_list[hostIP_port]['cookie'].encode())
                print("----------PEER LIST-------------")
                for keys in self.peer_list.keys():
                    print("\nsession: ", keys)
                    for key2 in self.peer_list[keys]:
                        print(key2, ':', self.peer_list[keys][key2])
                print("--------------------------------")
                self.update_ttl(hostIP_port)
                conn.close()
        elif int(data[0]) == 2:
            print("client sent this\n" + str(data))
            del (self.peer_list[hostIP_port])
            print("----------PEER LIST-------------")
            for keys in self.peer_list.keys():
                print("\nsession: ", keys)
                for key2 in self.peer_list[keys]:
                    print(key2, ':', self.peer_list[keys][key2])
            print("--------------------------------")
            conn.close()
        elif int(data[0]) == 3:
            flag_ttl = 3
            print(type(self.peer_list))
            # if the requester is in the peer list, then send him the
            if hostIP_port in self.peer_list.keys():
                conn.sendall(pickle.dumps(self.peer_list))
                print("Sent all existing peer info!")
                self.update_ttl(hostIP_port)
                conn.close()
            else:
                data = "You have not registered! Please register with the RS server before you request for peer list"
                conn.sendall(pickle.dumps(data))
                conn.close()


inst1 = Threads()
t = threading.Thread(name = "Listening func", target = inst1.listner)
ttl_thread = threading.Thread(name = "Threading keepalive", target = inst1.keepalive)
ttl_thread.setDaemon(True)
t.start()
ttl_thread.start()
