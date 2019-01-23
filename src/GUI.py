import graphics as gf
from tkinter import *
from tkinter import ttk


CIRCLE_R = 15


class GNode:
    def __init__(self, peer, name=""):
        self.peer = peer
        self.name = name
        self.neighbors = []
        self.location = None

    def show(self, graphics_window, location=None, color="white"):
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
window.title("")
window.geometry('650x450')


tabs = ttk.Notebook(window)
actions = ttk.Frame(tabs)
tabs.add(actions, text='actions')
tabs.pack(expand=1, fill='both')
page2 = ttk.Frame(tabs)
tabs.add(page2, text='console')
Label(actions).grid(column=0, row=0)  # blank


def add_client():
    Label(actions, text="added client: " + add_client_text.get()).grid(column=2, row=1)


add_client_button = Button(actions, text="add client", command=add_client)
add_client_button.grid(column=1, row=1)
add_client_text = Entry(actions)
add_client_text.grid(column=0, row=1)


def show_network():
    root = GNode(None, "R")
    a = GNode(None, "A")
    b = GNode(None, "B")
    c = GNode(None, "C")
    d = GNode(None, "D")
    e = GNode(None, "E")
    f = GNode(None, "F")

    root.neighbors.append(a)
    root.neighbors.append(b)
    a.neighbors.append(c)
    a.neighbors.append(d)
    b.neighbors.append(e)
    b.neighbors.append(f)

    tree = Tree(root)
    win = gf.GraphWin("main", 700, 500)
    win.setBackground('black')
    tree.show(win)
    while True:
        clicked_point = win.getMouse()
        if clicked_point is None:
            pass
        else:
            for node in tree.nodes:
                if node.is_inside(clicked_point):
                    print(node.name)
                    node.show(win, color="grey")
                    new_window = gf.GraphWin("SAG", 100, 100)
                    new_window.getMouse()
                    new_window.close()
                    node.show(win, color="white")

    """cir = gf.Circle(gf.Point(50, 50), 20)
    cir.setFill("white")
    cir.draw(win)
    message = gf.Text(gf.Point(50, 50), 'AB')
    message.setTextColor('red')
    message.setSize(15)
    message.draw(win)"""
    win.getMouse()
    win.close()


show_network_button = Button(actions, text="Show Network", command=show_network)
show_network_button.grid(column=0, row=2)

window.mainloop()






