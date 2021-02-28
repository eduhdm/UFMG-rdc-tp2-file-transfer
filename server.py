import socket
import sys
import os
import time
import random
from _thread import *
from utils import *

socket_tcp = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
host = '::'
port = int(sys.argv[1])
udp_port_init = 51512

def receive_package(socket_udp):
  _ = socket_udp.recvfrom(BUFSIZE_UDP)[0].decode('utf-8')
  index = socket_udp.recvfrom(BUFSIZE_UDP)[0].decode('utf-8')
  payload_size = socket_udp.recvfrom(BUFSIZE_UDP)[0].decode('utf-8')
  package_data = socket_udp.recvfrom(BUFSIZE_UDP)[0]

  return int(index), int(payload_size), package_data

def create_file_receiver(socket_tcp, file_name, file_size, udp_port):
  socket_udp = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
  socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  socket_udp.bind((host, udp_port))

  try:
    f = open(f'output/{file_name}', 'wb+')
  except FileNotFoundError:
    os.mkdir('./output')
    f = open(f'output/{file_name}', 'wb+')

  received_size = 0
  send_index = 0
  ack_index = 0
  payload_size = 0
  while (received_size < file_size):
    if(send_index >= WINDOW_SIZE - 1):
      try:
        send_message(socket_tcp, [msg_types["ack"], str(ack_index)])
        print('Sending ack #', ack_index)
        received_size += payload_size
        ack_index += 1
      except:
        received_size = ack_index * BUFSIZE_FILE_SLICE
        print('Error sending ack', ack_index)
        f.seek(ack_index * BUFSIZE_FILE_SLICE)

    send_index, payload_size, package_data = receive_package(socket_udp)
    f.write(package_data)
    print('Receiving package #', send_index)

  socket_tcp.send(str.encode(msg_types["fim"]))
  socket_udp.close()
  f.close()


def multi_threaded_client(connection, CLIENT_COUNT, udp_port):
  send_message(connection, msg_types["init_client"])
  file_name = ''
  file_size = ''
  udp_port = 0

  while True:
    res = recv_message(connection)
    if(res[0] == msg_types["hello"]):
      print('Received hello')
      udp_port = udp_port_init + CLIENT_COUNT
      send_message(connection, [msg_types["connection"], str(udp_port)])

    if(res[0] == msg_types["info_file"]):
      print('Received info_file')
      file_name = res[1]
      file_size = res[2]
      send_message(connection, msg_types["ok"])
      create_file_receiver(connection, file_name, int(file_size), udp_port)

    if not res or not res[0]:
        break
  connection.close()

def main():
  udp_port_init = 51512
  CLIENT_COUNT = 0

  try:
    socket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_tcp.bind((host, int(port)))
  except socket.error as e:
    print(str(e))

  print('Socket is listening..')
  socket_tcp.listen(1)

  print('client_count', CLIENT_COUNT)
  while True:
    Client, address = socket_tcp.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (Client, CLIENT_COUNT, udp_port_init))
    CLIENT_COUNT += 1
    print('Thread Number: ' + str(CLIENT_COUNT))

  socket_tcp.close()

if __name__ == "__main__":
  main()
