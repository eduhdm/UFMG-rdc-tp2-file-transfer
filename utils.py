import socket

msg_types = {
  "init_client": '0',
  "hello": '1',
  "connection": '2',
  "info_file": '3',
  "ok": '4',
  "fim": '5',
  "file": '6',
  "ack": '7',
}

WINDOW_SIZE = 4
SEPARATOR = '|'
BUFSIZE_TCP = 1024
BUFSIZE_UDP = 1024
BUFSIZE_FILE_SLICE = 1024

def recv_message(socket_con):
  return socket_con.recv(BUFSIZE_TCP).decode('utf-8').split(SEPARATOR)

def send_message(socket_con, msg):
  payload = msg
  if(isinstance(msg, list)):
    payload = SEPARATOR.join(msg)

  return socket_con.send(payload.encode('utf-8'))

def is_valid_file(file_name):
  try:
    file_name.encode('ascii')
  except UnicodeEncodeError:
    return False

  return (
    len(file_name) <= 15
    and file_name.count('.') == 1
    and len(file_name.split('.')[1]) >= 3
  )

