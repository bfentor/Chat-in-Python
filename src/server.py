import socket
from dotenv import load_dotenv
import os
import logging
import threading
import csv
import pickle
import sys

def handle_client(c_socket, c_addr):
    try:
        while True:
            skip_send = False
            request = c_socket.recv(1024).decode("utf-8")
            if request:
                logging.info(f"Received: {request}")
                r_split = request.split(":")

                logging.debug(request)

                if r_split[0] == "NICKNAME":
                    list = []

                    with open("db/users.csv", "r") as db:
                        reader = csv.reader(db, delimiter=",")
                        for row in reader:
                            list.append(row)

                    for l in list:
                        if l[0] == r_split[1]:
                            l[3] = r_split[2]

                    with open("db/users.csv", "w") as db:
                        writer = csv.writer(db, delimiter=",")
                        print(list)
                        writer.writerows(list)
                    response = "SER:nickname changed"
                        
                if r_split[0] == "REQ":
                    messages = get_previous_messages(r_split[1], r_split[2])
                    logging.info(f"Sent {response}")
                    c_socket.send(pickle.dumps(messages))
                    continue
                
                if r_split[0] == "C_REQ":
                    messages = get_previous_messages(r_split[1], r_split[2], timestamp=r_split[3])
                    logging.info(f"Sent {response}")
                    c_socket.send(pickle.dumps(messages))
                    continue   

                if r_split[0] == "UID":
                    response = f"SER:{uid_to_nickname(r_split[1])}"

                if r_split[0] == "MSG":
                    with open("db/messages.csv", "a") as db:
                        writer = csv.writer(db, delimiter=";")
                        writer.writerow(r_split[1:])
                    response = "SER:success"

                if r_split[0] == "AUTH":
                    result = authenticate(r_split[1], r_split[2]).split(":")
                    logging.debug(result)
                    if result[0] == "OK":
                        logging.info(f"Authenticated as {r_split[1]}")
                        response = f"SER:accepted:{result[1]}"
                    if result[0] == "BAD_PASSWORD":
                        response = "SER:bad_password"
                    if result[0] == "USER_NOT_FOUND":
                        response = "SER:user_not_found"

                if request == "SYS:close":
                    c_socket.send("SER:closed".encode("utf-8"))
                    logging.info("Sent SER:closed")
                    c_socket.close()
                    logging.info(f"Connection to client ({c_addr[0]}:{c_addr[1]}) closed")
                    break

                c_socket.send(response.encode("utf-8"))
                logging.info(f"Sent {response}")

    except Exception as e:
        logging.critical(f"Error when handling client: {e}")        

def authenticate(uname, psswd):
    message = ""

    with open("db/users.csv") as users:
        reader = csv.reader(users)
        for row in reader:
            if row[1] == uname:
                if row[2] == psswd:
                    logging.debug("Correct password")
                    logging.debug(f"OK:{row[0]}")
                    return f"OK:{row[0]}"
                else:
                    message = f"BAD_PASSWORD"
            else:
                message = f"USER_NOT_FOUND"
        return message

def uid_to_nickname(uid: str):
    with open("db/users.csv") as users:
        reader = csv.reader(users)
        for row in reader:
            if row[0] == str(uid):
                return row[3]

    with open("db/groups.csv") as groups:
        reader = csv.reader(groups, delimiter=";")
        for row in reader:
            if row[0] == str(uid):
                return row[1]
    
    logging.info("UID not found")
    return "error"

def get_previous_messages(uid, from_uid, timestamp=0):
    messages = []
    with open("db/messages.csv") as users:
        reader = csv.reader(users, delimiter=";")

        for row in reader:
            if ((row[0] == str(uid)) and (row[1] == str(from_uid))) or ((row[0] == str(from_uid)) and (row[1] == str(uid))) or (row[1][0] == "g" and row[1] == str(from_uid) and row[3] > timestamp):
                messages.append(row)

    return messages

def main():
    load_dotenv()
    logging.basicConfig(
        format="{asctime} - {levelname} - {message}",
        style="{",
        level=logging.DEBUG,
    )

    ip = os.getenv("SERVER_IP")
    port = int(os.getenv("PORT"))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((ip, port))

            server.listen(0)
            logging.info(f"Listening at {ip}:{port}")

            while True:
                c_socket, c_addr = server.accept()
                logging.info(f"Accepted connection from {c_addr[0]}:{c_addr[1]}")
                thread = threading.Thread(target=handle_client, args=(c_socket, c_addr,))
                thread.start()

    except Exception as e:
        logging.critical(f"Exception occurred: {e}")

if __name__ == "__main__":
    main()

# Credit for a lot of the code structure: https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python?dc_referrer=https%3A%2F%2Fduckduckgo.com%2F