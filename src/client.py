import socket
import logging
import datetime
import threading
from time import sleep
import pickle

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    style="{",
    level=logging.DEBUG,
)

port = 8000

def authenticate(uname: str, psswd: str, ip: str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((ip, port))
    s.send(f"AUTH:{uname}:{psswd}".encode("utf-8"))
    data = s.recv(1024).decode("utf-8")
    logging.info(data)

    return data, s

def update_nickname(uid, text, s):
    s.send(f"NICKNAME:{uid}:{text}".encode("utf-8"))
    logging.info("Nickname changed")

def send_message(uid: str, msg: str, s: socket.socket, to_uid: str):
    ct = datetime.datetime.now()
    try:
        # closed = is_socket_closed(s)
        # logging.debug(f"{s} | {closed}")
        s.send(f"MSG:{uid}:{to_uid}:{msg}:{ct.timestamp()}".encode("utf-8"))
        logging.debug("After sending message")
        data = s.recv(1024).decode("utf-8")
        # logging.info(f"SER:{data!r}")
        logging.info(data)
        logging.debug(data.split(":")[1])
    except Exception as e:
        logging.critical(f"Exception occurred: {e}")
    return data.split(":")[1]

def close_connection(s: socket.socket):
    try:
        s.send(f"SYS:close".encode("utf-8"))
        data = s.recv(1024).decode("utf-8")
        logging.info(data)
    except Exception as e:
        logging.info(f"Exception occurred in close_connection: {e}")
    finally:
        s.close()

def check_for_new_messages(uid: str, from_uid: str, s: socket.socket, timestamp):
    try:
        logging.info(f"Checking for messages between {uid} and {from_uid}")
        thread = threading.Thread(target=continuous_check, args=(uid, from_uid, s, timestamp))
        thread.start()

    except Exception as e:
        logging.critical(f"Exception occurred: {e}")

def continuous_check(uid: str, from_uid: str, s:socket.socket, timestamp):
    try:
        while True:
            msg = f"C_REQ:{uid}:{from_uid}:{timestamp}"
            s.send(msg.encode("utf-8"))
            data = s.recv(1024)
            logging.debug(msg)
            
            sleep(0.5)
    except Exception as e:
        logging.critical(f"Error in client thread: {e}")

def get_previous_messages(uid: str, from_uid: str, s: socket.socket):
    try:
        s.send(f"REQ:{uid}:{from_uid}".encode("utf-8"))
        data = s.recv(1024)
        # logging.info(f"SER:{data!r}")
        logging.debug(data)
        # logging.debug(data.split(":")[1])
    except Exception as e:
        logging.critical(f"Exception occurred: {e}")
    return data

def uid_to_nickname(uid: str, s: socket.socket):
    try:
        s.send(f"UID:{uid}".encode("utf-8"))
        data = s.recv(1024).decode("utf-8")
        # logging.info(f"SER:{data!r}")
        logging.info(data)
        # logging.debug(data.split(":")[1])
    except Exception as e:
        logging.critical(f"Exception occurred: {e}")
    return data.split(":")[1]

def is_socket_closed(sock: socket.socket) -> bool:
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError:
        logging.debug("Socket is open")
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        logging.debug("Socket was closed")
        return True  # socket was closed for some other reason
    except Exception as e:
        logging.exception("unexpected exception when checking if a socket is closed")
        return False
    return False
