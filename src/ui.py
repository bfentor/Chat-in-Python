from tkinter import *
from client import *
import pickle
from time import sleep
import datetime

# global uid
# global s
# global ip

def button_clicked():
    logging.debug(f"User name = {uname.get()}")
    logging.debug(f"Password = {password.get()}")
    error = "Error: Enter ip address" if ip_entry.get() == "" else ""
    error = "Error: Enter password" if password.get() == "" else ""
    error = "Error: Enter username" if uname.get() == "" else ""
    
    uid = -1

    try:
        if len(error) > 0:
            raise ValueError
        data, s = authenticate(uname.get(), password.get(), ip_entry.get())
        d_split = data.split(":")
        logging.debug(d_split)
        if d_split[1] == "accepted":
            uid = d_split[2]
        
        ip = ip_entry.get()
    except ConnectionRefusedError:
        logging.info("Connection refused")
        error_label.config(text="Connection refused")
        return
    except ValueError:
        logging.info(error)
        error_label.config(text=error)
        return
    # except Exception as e:
    #     logging.info(f"Unknown error: {e}")
    #     error_label.config(text=f"Unknown error")
    #     return

    # logging.debug(f"UID IP AND S 1234 {uid} {ip} {s}")

    if uid != -1:
        open_new_window(uid, ip, s) 
    else:
        logging.info(f"Authentication Failed")
        error_label.config(text="Authentication Failed")
        return

    
def open_new_window(uid, ip, s):

    # logging.debug(f"UID: {uid}, IP: {ip}, S: {s}")

    def chat_select(to_uid, uid, ip, s):

        def enter_text(arg):
            text = entry.get()
            entry.delete(0,END)

            logging.debug("Before send_message")
            rec = send_message(uid, text, s, to_uid)
            logging.debug(rec)
            if rec == "success":
                display = Label(chat, text=f"{uid_to_nickname(uid, s)} - {text}", anchor='e', fg='blue', wraplength=300, justify=LEFT)
                display.pack(side=BOTTOM, fill=X, after=entry)
            elif rec == "error":
                display = Label(chat, text=f"ERROR: Message could not be sent", anchor='e', fg='blue', wraplength=300, justify=LEFT)
                display.pack(side=BOTTOM, fill=X, after=entry)    

        # print(f"The ID of the widget is: {id}")
        nickname = uid_to_nickname(to_uid, s)
        user_nickname = uid_to_nickname(uid, s)
        chat = Toplevel(main)
        chat.protocol("WM_DELETE_WINDOW", logging.debug("Chat window killed"))
        chat.title(f"Chat - {nickname}")
        chat.geometry("700x500")

        entry = Entry(chat)
        entry.pack(side=BOTTOM, fill=X)

        # chat_frames = []
        # chat_frames.append(Frame(chat, anchor='w'))
        
        raw_messages = pickle.loads(get_previous_messages(uid, to_uid, s))
        messages = raw_messages[::-1]

        for message in messages:
            if message[0] == uid:
                Label(
                    chat, 
                    text=f"{uid_to_nickname(uid, s)} - {message[2]}", 
                    anchor="e", 
                    fg='blue', 
                    wraplength=300, 
                    justify=LEFT).pack(side=BOTTOM, fill=X
                )
            elif (message[1][0] == "g") and (message[1] == to_uid) and (message[0] != uid):
                Label(
                    chat, 
                    text=f"{uid_to_nickname(message[0], s)} - {message[2]}", 
                    anchor="w", 
                    fg='red', 
                    wraplength=300, 
                    justify=LEFT).pack(side=BOTTOM, fill=X
                )
            elif message[0] == to_uid:
                Label(
                    chat, 
                    text=f"{uid_to_nickname(to_uid, s)} - {message[2]}", 
                    anchor="w", 
                    fg='red', 
                    wraplength=300, 
                    justify=LEFT).pack(side=BOTTOM, fill=X
                )

        chat.bind('<Return>', enter_text)


    root.destroy()
    main = Tk()
    main.title(f"Colloquium - {uid_to_nickname(uid, s)}")
    main.geometry("900x1500")  
    main.resizable(False, False)
    # main.protocol("WM_DELETE_WINDOW", close_connection(s))

    f1 = Frame(main)
    f1.grid_rowconfigure(10, weight=1)

    chatrooms = Frame(
        f1, relief=RAISED,
        bg='lightblue', bd=3,
        width=900, height=55,
        highlightbackground='black',
        highlightthickness=2,
    )

    cl1 = Label(chatrooms, text="Chatrooms", bg="lightblue")
    cl1.grid(row=0, column=0)


    pm = Frame(
        f1, relief=RAISED,
        bg='lightblue', bd=3,
        width=900, height=55,
        highlightbackground='black',
        highlightthickness=2,
    )

    pl1 = Label(pm, text="Private Messaging", bg="lightblue")
    pl1.grid(row=0, column=0)

    def disconnect():
        close_connection(s)
        main.destroy()

    Button(
        main, relief=RAISED,
        command= disconnect,
        bg='red', bd=3,
        fg="white",
        width=56, height=1,
        # highlightbackground='red',
        highlightthickness=2,
        text="Disconnect",
        cursor="hand2"
        # activeforeground="grey"
    ).grid(row=0, column=0)

    def change_nickname(arg):
        text = e1.get()
        e1.delete(0,END)

        update_nickname(uid, text, s)
        sleep(1)

    nicknameChange = Frame(
        main, relief=RAISED,
        bg='lightblue', bd=3,
        width=900, height=55,
        highlightbackground='black',
        highlightthickness=2,
    )

    
    l3 = Label(nicknameChange, text="Nickname", bg="lightblue")
    l3.grid(row=0, column=0)
    e1 = Entry(nicknameChange)
    e1.grid(row=0, column=1)
    
    e1.bind('<Return>', change_nickname)

    # f1.grid_propagate(False)
    nicknameChange.grid_propagate(False)
    chatrooms.grid_propagate(False)
    pm.grid_propagate(False)
    
    nicknameChange.grid(row=1,column=0)
    f1.grid(row=10,column=0)
    chatrooms.grid(row=0, column=0)
    pm.grid(row=100, column=0)

    list_chatrooms = []

    #prototype
    list_chatrooms = ["g493", "g984", "g281"]
    list_buttons_chatrooms = []

    list_chats = ["1234", "2534", "5342", "0798"]
    list_buttons_chats = []

    for i, k in enumerate(list_chatrooms):
        Button(
            f1, relief=RAISED,
            command= lambda k=k: chat_select(k, uid, ip, s),
            bg='lightgreen', bd=3,
            width=56, height=2,
            # highlightbackground='red',
            highlightthickness=2,
            text=uid_to_nickname(k, s),
            fg="black",
            cursor="hand2"
            # activeforeground="grey"
        ).grid(row=i+1, column=0)

    for i, k in enumerate(list_chats):
        logging.debug(f"{k}, {uid}")
        if k == uid:
            continue
        Button(
            f1, relief=RAISED,
            command= lambda k=k: chat_select(k, uid, ip, s),
            bg='lightgreen', bd=3,
            width=56, height=2,
            # highlightbackground='red',
            highlightthickness=2,
            text=uid_to_nickname(k, s),
            fg="black",
            cursor="hand2"
            # id=i
            # activeforeground="grey"
        ).grid(row=i+101, column=0)

        
    


root=Tk()
root.geometry("400x800")
root.title("Login")
root.resizable(False, False)

# root.iconbitmap(default="img/smile.ico")

smile = PhotoImage(file=r"img/smile.png")
img = Label(root, image=smile)

# uframe = widget_type(root, Frame, )

uframe = Frame(
    root, relief=RAISED,
    bg='lightblue', bd=3,
    height=100, width=400,
    highlightbackground='black',
    highlightthickness=2,
)

pframe = Frame(
    root, relief=RAISED,
    bg='lightblue', bd=3,
    height=100, width=400,
    highlightbackground='black',
    highlightthickness=2,
)

ipframe = Frame(
    root, relief=RAISED,
    bg='lightblue', bd=3,
    height=100, width=400,
    highlightbackground='black',
    highlightthickness=2,
)

uname_label = Label(uframe, text="Username", bg="lightblue")
uname = Entry(uframe, width=25)
uname_label.pack()
uname.pack()

password_label = Label(pframe, text="Password", bg="lightblue")
password = Entry(pframe, width=25)
password_label.pack()
password.pack()

ip_label = Label(ipframe, text="Server IP", bg="lightblue")
ip_entry = Entry(ipframe, width=25)
ip_label.pack()
ip_entry.pack()

enter = Button(
    root, text="Login", 
    command=button_clicked, cursor="hand2", 
    width=22, bg="lightblue", 
    activebackground="lightgreen",
    relief=RAISED,
)

error_label = Label(root, fg="red")

img.grid(row=0,column=0, sticky='N')

uframe.grid(row=1,column=0)
pframe.grid(row=2,column=0)
ipframe.grid(row=3,column=0)
enter.grid(row=5,column=0, sticky='S')

error_label.grid(row=6, column=0)

root.mainloop()