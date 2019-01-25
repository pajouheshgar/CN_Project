import threading
import time
from tkinter import *
from tkinter import ttk, scrolledtext


class Log:
    def __init__(self, log):
        self.log = log


class Application(Frame):

    def __init__(self, window, buffer, log_class):
        self.tabs = ttk.Notebook(window)
        actions = ttk.Frame(self.tabs)
        self.tabs.add(actions, text='actions')
        self.log_tab = ttk.Frame(self.tabs)
        self.log_tab.pack(expand=1, fill='both')
        self.tabs.add(self.log_tab, text='log')
        self.tabs.pack(expand=1, fill='both')
        Frame.__init__(self, actions)
        self.pack(expand=1, fill='both')
        self.__buffer = buffer
        self.log_class = log_class
        self.output = Label(self)
        self.input = Entry(self)
        self.output['text'] = 'Hello'

    def show(self):
        self.pack()
        self.add_actions()
        self.log()

    def log(self):
        def refresh_trigger():
            log_text = self.log_class.log
            while True:
                # time.sleep(0.1)
                if log_text != self.log_class.log:
                    refresh()
                    log_text = self.log_class.log

        def refresh():
            text.config(state="normal")
            text.delete('1.0', END)
            text.insert(INSERT, self.log_class.log)
            text.config(state=DISABLED)

        threading.Thread(target=refresh_trigger).start()
        # Button(self.log_tab, text="refresh", command=refresh).pack()
        text = scrolledtext.ScrolledText(master=self.log_tab, wrap=WORD, width=400, height=300)
        text.config(state="normal")
        text.insert(INSERT, self.log_class.log)
        text.config(state=DISABLED)
        text.pack()

    def add_actions(self):
        def advertise():
            self.__buffer.append('Advertise')
            self.output['text'] = 'Advertised'

        def disconnect():
            self.__buffer.append('Disconnect')
            self.output['text'] = 'disconnected!'

        def register():
            self.__buffer.append('Register')
            self.output['text'] = 'registered!'

        def send_message():
            self.__buffer.append('Message ' + self.input.get())
            self.output['text'] = 'message sent: ' + self.input.get()

        Label(self).grid()  # blank first line
        disconnect_button = Button(self, width=10)
        disconnect_button["text"] = "Disconnect"
        disconnect_button["command"] = disconnect
        disconnect_button.grid(row=1)  # sticky="W"

        advertise_button = Button(self, width=10)
        advertise_button["text"] = "Advertise"
        advertise_button["command"] = advertise
        advertise_button.grid(row=3)

        register_button = Button(self, width=10)
        register_button["text"] = "Register"
        register_button["command"] = register
        register_button.grid(row=2)

        self.output.grid(row=5, column=0, sticky="W")

        send_button = Button(self)
        send_button["text"] = "Broadcast"
        send_button["command"] = send_message
        send_button.grid(row=6, column=2)
        # Label(self, text="message:").grid(column=0, row=6)
        self.input.grid(row=6, column=0, sticky="W")


class UserInterface(threading.Thread):


    def __init__(self):
        super().__init__()
        self.peer_log = Log("")
        self.buffer = []
        self.window = None
        self.window_open = False
        self.name = ""

    def close_window(self):
        self.window.withdraw()
        self.window_open = False

    def open_window(self):
        self.window.deiconify()
        self.window_open = True

    def clear_buffer(self):
        self.buffer.clear()

    def run(self):
        """
        Which the user or client sees and works with.
        This method runs every time to see whether there are new messages or not.
        """
        self.window = Tk()
        self.window.title(self.name)
        self.window.geometry("400x300")
        self.window.resizable(0, 0)
        self.window.protocol('WM_DELETE_WINDOW', self.close_window)
        self.close_window()
        self.app = Application(self.window, self.buffer, self.peer_log)
        self.app.show()
        self.app.mainloop()

        # while True:
        #   if self.window_open:

        #      if app is None:
        #         app = Application(self.window, self.buffer)
        #     app.show()
        #    app.mainloop()

        # window.destroy()
