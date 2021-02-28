import socket
import sys
from utils import *
import os
import time
import random

host = sys.argv[1]
tcp_port = int(sys.argv[2])
file_name = sys.argv[3]

if(not is_valid_file(file_name)):
  print("Nome não permitido")
  exit()

address_family = socket.getaddrinfo(host, tcp_port)[0][0]
socket_tcp = socket.socket(address_family, socket.SOCK_STREAM)
socket_udp = socket.socket(address_family, socket.SOCK_DGRAM)

f = open(file_name, "rb")

# Enviar mensagem do tipo file (headers + dado)
def send_package(data, index, udp_port):
    socket_udp.sendto(msg_types["file"].encode('utf-8'), (host, udp_port))
    socket_udp.sendto(str(index).encode('utf-8'), (host, udp_port))
    socket_udp.sendto(str(BUFSIZE_FILE_SLICE).encode('utf-8'), (host, udp_port))
    socket_udp.sendto(data, (host, udp_port))

# Recebe uma porta udp retornada pelo sevidor
# Envia 4 pacotes (window size) e a partir disso começa a esperar o retorno
# ack do servidor para enviar mais pacotes (janela deslizante)
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
          print('Received ack #', ack_index)
        if(res[0] == msg_types["fim"]):
          print('Received fim, closing connection...')
          break
      # Reseta para o próximo pacote que não recebeu ack
      except socket.timeout:
        print('Timeout receiving ack...')
        send_index = ack_index + 1
        # Volta na posição de leitura do próximo pacote
        f.seek(send_index * BUFSIZE_FILE_SLICE)

    data_package = f.read(BUFSIZE_FILE_SLICE)
    print('Sending package #', send_index)
    send_package(data_package, send_index, udp_port)
    send_index+=1


def send_hello():
  print('Sending hello')
  send_message(socket_tcp, msg_types["hello"])

# Envia mensagem com informações do arquivo:
# 1. tipo da mensagem,
# 2. Nome do arquivo
# 3. Tamanho do arquivo em bytes
def send_info_file():
  print('Sending file info')
  msgs = [msg_types["info_file"], file_name, str(os.stat(file_name).st_size)]
  send_message(socket_tcp, msgs)

def main():
  print('Waiting for connection response')

  try:
    if(':' in host):
      socket_tcp.connect((host, tcp_port, 0, 0))
    else:
      socket_tcp.connect((host, tcp_port))
  except socket.error as e:
    print(str(e))

  # Executa bloco até receber a mensagem to tipo OK
  # A partir dessa mensagem, a execução é controlada
  # por send_packages_sliding_window
  while True:
    res = recv_message(socket_tcp)
    if(res[0] == msg_types["init_client"]):
      print('Received init')
      send_hello()

    if(res[0] == msg_types["connection"]):
      print('Received connection, udp port', res[1])
      udp_port = int(res[1])
      send_info_file()

    if(res[0] == msg_types["ok"]):
      print("Received ok")
      send_packages_sliding_window(udp_port)
      break

    if(not res or not res[0]):
      break

  socket_udp.close()
  socket_tcp.close()

if __name__ == "__main__":
  main()
