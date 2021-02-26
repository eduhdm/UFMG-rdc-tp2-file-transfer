import socket
import sys
from utils import *
import os
import time
import random

host = sys.argv[1]
tcp_port = int(sys.argv[2])
file_name = sys.argv[3]

address_family = socket.getaddrinfo(host, tcp_port)[0][0]
socket_tcp = socket.socket(address_family, socket.SOCK_STREAM)
socket_udp = socket.socket(address_family, socket.SOCK_DGRAM)

f = open(file_name, "rb")

def send_package(data, index, udp_port):
    # if(random.randint(0, 100) % 50 == 0 and False):
    #   raise Exception('dsa')
    socket_udp.sendto(msg_types["file"].encode('utf-8'), (host, udp_port))
    socket_udp.sendto(str(index).encode('utf-8'), (host, udp_port))
    socket_udp.sendto(str(BUFSIZE_FILE_SLICE).encode('utf-8'), (host, udp_port))
    socket_udp.sendto(data, (host, udp_port))


def send_packages_sliding_window(udp_port):
  socket_tcp.settimeout(1)
  send_index=0
  ack_index=-1
  while True:
    if(send_index >= WINDOW_SIZE):
      try:
        res = recv_message(socket_tcp)

        if(res[0] == msg_types["ack"]):
          ack_index = int(res[1])
          print('ack index is', ack_index)
        if(res[0] == msg_types["fim"]):
          print('Received fim, closing connection...')
          break
      except socket.timeout:
        print('timeout timeout timeout', ack_index)
        f.seek((ack_index + 1) * BUFSIZE_FILE_SLICE)
        send_index = ack_index + 1
        data_package = f.read(BUFSIZE_FILE_SLICE)
        send_package(data_package, send_index, udp_port)
        send_index+=1
        continue

    data_package = f.read(BUFSIZE_FILE_SLICE)
    print('Sending package #', send_index)
    send_package(data_package, send_index, udp_port)
    send_index+=1


def send_hello():
  send_message(socket_tcp, msg_types["hello"])

def send_info_file():
  print('Sending file info')
  msgs = [msg_types["info_file"], file_name, str(os.stat(file_name).st_size)]
  send_message(socket_tcp, msgs)

def main():
  print('Waiting for connection response')
  if(not is_valid_file(file_name)):
    print("Nome não permitido")
    exit()

  try:
    if(':' in host):
      socket_tcp.connect((host, tcp_port, 0, 0))
    else:
      socket_tcp.connect((host, tcp_port))
  except socket.error as e:
    print(str(e))

  while True:
    res = recv_message(socket_tcp)
    print('received message ', res)
    if(res[0] == msg_types["init_client"]):
      print('received init')
      send_hello()

    if(res[0] == msg_types["connection"]):
      print('received connection')
      udp_port = int(res[1])
      print('udp port', udp_port)
      send_info_file()

    if(res[0] == msg_types["ok"]):
      print("received ok")
      send_packages_sliding_window(udp_port)
      break

    if(not res or not res[0]):
      break

  socket_udp.close()
  socket_tcp.close()

if __name__ == "__main__":
  main()
