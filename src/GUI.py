from graphics import *
from src.Peer import Peer
import graphics as gf
import time
from tkinter import *
from tkinter import ttk, messagebox
import threading
from src.UserInterface import UserInterface


def exit_program():
    window.destroy()
    window.quit()
    os._exit(10)
    return


class MyGraphWin(gf.GraphWin):
    def getMouse(self):
        """Wait for mouse click and return Point object representing
        the click"""
        self.mouseX = None
        self.mouseY = None
        while self.mouseX == None or self.mouseY == None:
            self.update()
            #_tkCall(self.update)
            if self.isClosed():
                return 0
            time.sleep(.1)  # give up thread
        x, y = self.toWorld(self.mouseX, self.mouseY)
        self.mouseX = None
        self.mouseY = None
        return gf.Point(x, y)


"""  
azed variables: 
    Peer.network_graph 
    right_child, left_child
    root_address=("127.0.0.1", 10000)    
"""  #  COPS FROM AZED


CIRCLE_R = 15
root = None


class GNode:
    def __init__(self, address=None, name="", is_root=False):
        self.port = None
        self.address = None
        self.name = name
        if address is None:
            self.peer = None
        else:
            if is_root:
                if root is not None:
                    print("Root Already Exists")
                    return
                self.create_server()
            else:
                self.port = int(address[1])
                self.create_client()

        #self.address = (str(address[0]), str(address[1]))
        self.neighbors = []
        self.location = None

    def create_server(self):
        self.peer = Peer("127.0.0.1", 10000, is_root=True)
        self.port = self.peer.server_port
        self.address = (self.peer.server_ip, self.peer.server_port)
        self.peer.UI.name = self.name
        print("SERVER ADDED")
        thread = threading.Thread(target=self.peer.run)
        thread.start()

    def create_client(self):
        self.peer = Peer("127.0.0.1", self.port, is_root=False, root_address=("127.0.0.1", 10000))
        self.port = self.peer.server_port
        self.address = (self.peer.server_ip, self.peer.server_port)
        self.peer.UI.name = self.name
        print("CLIENT ADDED")
        thread = threading.Thread(target=self.peer.run)
        thread.start()

    def connect_to(self, g_node):
        if g_node in self.neighbors:
            pass
        else:
            self.neighbors.append(g_node)
            g_node.connect_to(self)

    def show(self, graphics_window, location=None, color=None):
        if color is None:
            if self.peer.registered:
                color = "green"
            else:
                color = "white"

        if location is None:
            location = self.location
        else:
            self.location = location
        circle = gf.Circle(location, CIRCLE_R)
        circle.setFill(color)
        circle.setOutline("yellow")
        circle.draw(graphics_window)
        label = gf.Text(location, self.name)
        label.setTextColor('red')
        label.setSize(CIRCLE_R - CIRCLE_R//4)
        label.draw(graphics_window)

    def is_inside(self, point):
        if (point.x - self.location.x)**2 + (point.y - self.location.y)**2 <= (CIRCLE_R + 1)**2:
            return True
        return False


class Tree:
    def __init__(self, root):
        self.root = root
        self.nodes = None

    def show(self, graphics_window):
        marked = [self.root]
        x, y = graphics_window.width/2, CIRCLE_R + 10
        queue = [(self.root, gf.Point(x, y), 0)]
        self.root.show(graphics_window, gf.Point(x, y))
        while len(queue) > 0:
            node, location, depth = queue.pop(0)
            i = 0
            for child in node.neighbors:
                if child not in marked:
                    marked.append(child)
                    new_location = gf.Point(location.x + (2*i-1)*graphics_window.width/(2**(depth+2)),
                                            location.y + 50)
                    queue.append((child, new_location, depth+1))
                    line = gf.Line(gf.Point(location.x, location.y + CIRCLE_R),
                                   gf.Point(new_location.x, new_location.y - CIRCLE_R))
                    line.setFill('yellow')
                    line.setOutline('yellow')
                    line.draw(graphics_window)
                    child.show(graphics_window, new_location)
                    i += 1
        self.nodes = marked


window = Tk()
window.protocol('WM_DELETE_WINDOW', exit_program)
window.title("")
window.geometry('650x450')
nodes = {}
tabs = ttk.Notebook(window)
actions = ttk.Frame(tabs)
tabs.add(actions, text='actions')
#page2 = ttk.Frame(tabs)
#tabs.add(page2, text='console')
tabs.pack(expand=1, fill='both')
Label(actions).grid(column=0, row=0)  # blank


def add_client():
    if PORT.get() == "":
        messagebox.showinfo("No Port Given!", "please fill the port field")
        return
    for address in nodes:
        if address[1] == PORT.get():
            messagebox.showinfo("Client Already Exists!", "the input port is in use")
            #Label(actions, text="client with IP:'127.0.0.1' and PORT:'" + PORT.get() + "' already exists!").grid(column=5, row=1)
            return
    name = "N" + len(nodes).__str__()
    node = GNode((IP.get(), PORT.get()), name)
    nodes[node.address] = node
    #nodes.append(GNode((IP.get(), PORT.get()), name))
    Label(actions, text="added client with IP:'127.0.0.1' and PORT:'" + PORT.get() + "' as " + name).grid(
        column=5, row=1)


def add_root():
    global root
    if root is not None:
        messagebox.showinfo("Root Already Exists!", "can't add more than one root")
        return
    root = GNode(("127.000.000.001", "10000"), "R", is_root=True)  # needs checking if IP and PORT are valid
    Label(actions, text="added root with IP:'127.0.0.1' and PORT:'10000' as R").grid(
        column=5, row=1)
    #messagebox.showinfo("Root Added!", "added root with IP:'127.0.0.1' and PORT:'10000' as R")
    nodes[root.address] = root
    nodes[root.address] = root
    #nodes.append(root)


Label(actions, text="IP:").grid(column=0, row=1)
Label(actions, text="PORT:").grid(column=0, row=2)
IP = Entry(actions)
IP.insert(END, "(optional)")
IP.grid(column=1, row=1)
PORT = Entry(actions)
PORT.grid(column=1, row=2)


add_client_button = Button(actions, text="add client", command=add_client)
add_client_button.grid(column=3, row=1)

add_root_button = Button(actions, text="add root", command=add_root)
add_root_button.grid(column=4, row=1)


class RefreshButton:
    def __init__(self):
        self.x1 = 10
        self.x2 = 80
        self.y1 = 10
        self.y2 = 30
        self.rect = gf.Rectangle(gf.Point(self.x1, self.y1), gf.Point(self.x2, self.y2))
        self.rect.setOutline("red")
        self.message = gf.Text(Point(45, 20), "REFRESH")
        self.message.setTextColor('black')
        self.message.setSize(10)

    def show(self, graph_win, color="white"):
        try:
            self.rect.undraw()
            self.message.undraw()
        except Exception:
            pass
        self.rect.setFill(color)
        self.rect.draw(graph_win)
        self.message.draw(graph_win)

    def is_inside(self, point):
        if point.x > self.x1 and point.y > self.y1 and point.x < self.x2 and point.y < self.y2:
            return True
        return False


def build_root_tree(root_node):
    network_graph = root.peer.graph
    for address in nodes:
        if network_graph.nodes.__contains__(address):
            if network_graph.nodes[address].left_child is not None:
                nodes[address].connect_to(nodes[network_graph.nodes[address].left_child.address])
            if network_graph.nodes[address].right_child is not None:
                nodes[address].connect_to(nodes[network_graph.nodes[address].right_child.address])
    return Tree(root_node)


def show_network():
    win = gf.GraphWin("main", 700, 500, autoflush=False)
    win.setBackground('black')
    exit = False
    while exit is False:
        win.update()
        refresh = RefreshButton()
        refresh.show(win)
        if root is not None:
            tree = build_root_tree(root)
            tree.show(win)
            tree_nodes = tree.nodes
        else:
            tree_nodes = []
        i = 0
        for address in nodes:
            is_in_tree = False
            for node in tree_nodes:
                if address == node.address:
                    is_in_tree = True
            if not is_in_tree:
                nodes[address].show(win, gf.Point(3*(i+1)*CIRCLE_R, win.height - (CIRCLE_R + 10)))
                i += 1
        try:
            clicked_point = win.getMouse()
            if clicked_point is None:
                pass
            elif refresh.is_inside(clicked_point):
                refresh.show(win, "grey")
                for item in win.items[:]:
                    item.undraw()
                win.update()
                refresh.show(win, "white")
            else:
                for address in nodes:
                    if nodes[address].is_inside(clicked_point):
                        print(nodes[address].name)
                        nodes[address].show(win, color="grey")
                        nodes[address].peer.UI.name = nodes[address].name
                        nodes[address].peer.UI.open_window()

                        """
                        new_window = MyGraphWin("SAG", 100, 100)
                        new_window.getMouse()
                        new_window.close()
                        """
                        nodes[address].show(win)
        except gf.GraphicsError as err:
            exit = True
            break
    win.close()


show_network_button = Button(actions, text="Show Network", command=show_network)
show_network_button.grid(column=1, row=3)

exit_button = Button(actions, text="Exit", command=exit_program)
exit_button.place(relx=1.0, rely=1.0, anchor=SE)

window.mainloop()




