# %%
from email import message
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from ttkwidgets.autocomplete import AutocompleteCombobox
import nodes as nd
import re
# %%
pad_buttons = 5

# %%
root = Tk()
root.title('Odyssee pathfinder')
root.geometry('400x400')
root.resizable(0, 0)
root.config(bg = '#f25252')

# %%
frame = Frame(root, bg='#f25252')
frame.pack(expand=True)

# %%
main_menu = Menu(frame)
root.config(menu= main_menu)

class Lotfi(Entry):
    def __init__(self, master=None, **kwargs):
        self.var = StringVar()
        Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace('w', self.check)
        self.get, self.set = self.var.get, self.var.set

    def check(self, *args):
        if self.get().isdigit() or self.get() == '': 
            # the current value is only digits; allow this
            self.old_value = self.get()
        else:
            # there's non-digit characters in the input; reject this 
            self.set(self.old_value)
# %%
#Add a node(str) in the file containing all nodes, return None if sucessfull and -1 if node already exist
def add_node(node):
    list_all_nodes = nd.open_csv(nd.FILE_NODES,1)
    if [node] in list_all_nodes:
        return -1    
    else:
        nd.write_csv(nd.FILE_NODES, [[node]])
        return None

#Return an updated generator without node in it
def update_node(node):
    list_all_nodes = nd.open_csv(nd.FILE_NODES, 1)
    for node_ in list_all_nodes:
        if node == node_[0]:
            continue
        yield node_

#Remove node from the file containing all the nodes
def remove_node(node):
    gen_all_nodes = update_node(node)
    list_all_nodes = []
    for node_ in gen_all_nodes:
        list_all_nodes.append(node_[0])
    nd.rem_file(nd.FILE_NODES)
    for node_ in list_all_nodes:
        nd.write_csv(nd.FILE_NODES, [[node_]])

#Add a path[starting_node, ending_node, length] in the file containing all paths, return None if sucessfull and -1 if path already exist
def add_path(node_a, node_b, length):
    list_all_paths = nd.open_csv(nd.FILE_PATHS)
    for path in list_all_paths:
        if (re.search(f'({node_a})',path[0]) is not None and re.search(f'({node_b})',path[1]) is not None) or (re.search(f'({node_b})',path[0]) is not None and re.search(f'({node_a})',path[1]) is not None):
            return -1
    nd.write_csv(nd.FILE_PATHS, [[node_a, node_b,length]])
    return None

#Return an updated generator containing a list of all paths
def update_paths(node_a, node_b, length=0, remove=None):
    list_all_paths = nd.open_csv(nd.FILE_PATHS)
    if remove is None:
        for path in list_all_paths:
            if (re.search(f'({node_a})',path[0]) is not None and re.search(f'({node_b})',path[1]) is not None) or (re.search(f'({node_b})',path[0]) is not None and re.search(f'({node_a})',path[1]) is not None):
                yield [node_a, node_b, length]
            else:
                yield path
    else:
        for path in list_all_paths:
            if (re.search(f'({node_a})',path[0]) is not None and re.search(f'({node_b})',path[1]) is not None) or (re.search(f'({node_b})',path[0]) is not None and re.search(f'({node_a})',path[1]) is not None):
                continue
            else:
                yield path

#Remove a path from the file containing all paths
def remove_path(node_a, node_b):
    list_all_paths = update_paths(node_a, node_b, remove=1)
    paths= []
    for path in list_all_paths:
        paths.append(path)
    nd.rem_file(nd.FILE_PATHS)
    for path in paths:
        nd.write_csv(nd.FILE_PATHS, path)


#Modify a path in the file containing all paths, return None if sucessfull and return -1 if path didn't exist and add it.
def change_path(node_a, node_b, length):
    if add_path(node_a, node_b, length) is not None:
        return -1
    else:
        list_all_paths = update_paths(node_a, node_b, length)
        paths = []
        for path in list_all_paths:
            paths.append(path)
        nd.rem_file(nd.FILE_PATHS)
        for path in paths:
            nd.write_csv(nd.FILE_PATHS, path)
        return None

# %%
def open_add_node_window():

    add_node_root = Toplevel()
    add_node_root.title('Add a node')
    add_node_root.geometry('300x300')
    add_node_root.resizable(0, 0)
    add_node_root.config(bg = '#f25252')

    add_node_frame = Frame(add_node_root, bg='#f25252')
    add_node_frame.pack(expand=True)

    def add_node_verif(node_name):
        if add_node(node_name) is not None:
            messagebox.showerror(title='Node Error', message="I'm afraid this node already exist !")
        entry_update(add_node_entry)

    add_node_entry = Entry(add_node_frame)
    add_node_button = Button(add_node_frame, text='Add', command=lambda:add_node_verif(add_node_entry.get()))
    add_node_quit = Button(add_node_frame, text='Quit !', command=add_node_root.destroy)

    add_node_entry.pack()
    add_node_button.pack()
    add_node_quit.pack()

def list_nodes_update(combobox, value = None, empty=None):
        list_nodes = []
        if empty is not None:
            combobox.config(completevalues=list_nodes)
        else:
            for node in nd.open_csv(nd.FILE_NODES, 1):
                if node[0] == value:
                    continue
                else:
                    list_nodes.append(node[0])
            combobox.config(completevalues=list_nodes)
        try:
            combobox.delete(0, len(combobox.get()))
        except TclError:
            pass

def list_paths_update(combobox, value=None, empty=None):
    list_paths = []
    if empty is not None:
        combobox.config(completevalues=list_paths)
    else:
        for path in nd.open_csv(nd.FILE_PATHS):
            if f'{path[0]},{path[1]},{path[2]}' == value:
                continue
            else:
                list_paths.append(f'{path[0]},{path[1]},{path[2]}')
        combobox.config(completevalues=list_paths)
    try:
        combobox.delete(0, len(combobox.get()))
    except TclError:
        pass
                
def entry_update(entry):
    try:
        entry.delete(0, len(entry.get()))
    except TclError:
        pass

# %%
def open_remove_node_window():

    remove_node_root = Toplevel()
    remove_node_root.title('Remove a node')
    remove_node_root.geometry('300x300')
    remove_node_root.resizable(0, 0)
    remove_node_root.config(bg = '#f25252')

    remove_node_frame = Frame(remove_node_root, bg='#f25252')
    remove_node_frame.pack(expand=True)

    remove_node_combobox = AutocompleteCombobox(remove_node_frame)

    list_nodes_update(remove_node_combobox)
    def rem_node_verif():
        node_ = remove_node_combobox.get()
        remove_node(node_)
        list_nodes_update(remove_node_combobox)

    remove_node_button = Button(remove_node_frame, text='Remove', command= rem_node_verif)
    remove_node_combobox.pack()
    remove_node_button.pack()  

# %%
def open_add_path_window():

    add_path_root = Toplevel()
    add_path_root.title('Add a path')
    add_path_root.geometry('300x300')
    add_path_root.resizable(0, 0)
    add_path_root.config(bg = '#f25252')

    add_path_frame = Frame(add_path_root, bg='#f25252')
    add_path_frame.pack(expand=True)

    def end_node_init(event):
        list_nodes_update(add_path_combobox_end, add_path_combobox_start.get())
    


    add_path_label_start = Label(add_path_frame, text='Start')
    add_path_combobox_start = AutocompleteCombobox(add_path_frame)
    add_path_label_end = Label(add_path_frame, text='End')
    add_path_combobox_end = AutocompleteCombobox(add_path_frame)
    add_path_label_length = Label(add_path_frame, text='Length')
    add_path_entry = Lotfi(add_path_frame)
    add_path_combobox_start.bind("<<ComboboxSelected>>", end_node_init)
    

    list_nodes_update(add_path_combobox_start)
    def add_path_verif():
        node_start = add_path_combobox_start.get()
        node_end = add_path_combobox_end.get()
        length = add_path_entry.get()
        if node_start == node_end:
            messagebox.showerror(title='Path Error', message="I'm afraid you can't make a path between the same point !")
        if node_start is None or node_end is None:
            messagebox.showerror(title='Path Error', message="I'm afraid you need to select more nodes !")
        if add_path(node_start, node_end, length) is not None:
            messagebox.showerror(title='Path Error', message="I'm afraid this path already exist !")
        list_nodes_update(add_path_combobox_start)
        list_nodes_update(add_path_combobox_end, empty=1)
        entry_update(add_path_entry)

    add_path_button = Button(add_path_frame, text='Add a path', command=add_path_verif)


    add_path_label_start.pack()
    add_path_combobox_start.pack()
    add_path_label_end.pack()
    add_path_combobox_end.pack()
    add_path_label_length.pack()
    add_path_entry.pack()
    add_path_button.pack()

def open_main_windows():
    main_window_combobox_start = AutocompleteCombobox(frame)
    main_window_label_start = Label(frame, text= 'Start')

    def end_node_init(event):
        list_nodes_update(main_window_combobox_end, main_window_combobox_start.get())


    def shortest_path():
        list_all_paths = []
        start = main_window_combobox_start.get()
        end = main_window_combobox_end.get()
        shortest_path_str = ''
        for path in nd.open_csv(nd.FILE_PATHS):
            list_all_paths.append(path)
        graph = nd.build_graph(list_all_paths)
        del list_all_paths
        dijkstra_list = nd.dijkstra(graph, start)
        shortest_path = nd.find_shortest_path(start, end, dijkstra_list[1])
        for node in shortest_path:
            shortest_path_str+=' -> ' + node
        messagebox.showinfo(title='Shortest path', message=f'{shortest_path_str}\n{dijkstra_list[0][end]}')
        list_nodes_update(main_window_combobox_start)
        list_nodes_update(main_window_combobox_end, empty=1)

    main_window_label_end = Label(frame, text='End')
    main_window_combobox_end = AutocompleteCombobox(frame)
    list_nodes_update(main_window_combobox_start)
    main_window_combobox_start.bind("<<ComboboxSelected>>", end_node_init)
    main_window_button = Button(frame, text='Find Shortest Path', command=shortest_path)

    main_window_label_start.pack()
    main_window_combobox_start.pack()
    main_window_label_end.pack()
    main_window_combobox_end.pack()
    main_window_button.pack()

def open_remove_path_window():
    remove_path_root = Toplevel()
    remove_path_root.title('Remove a path')
    remove_path_root.geometry('300x300')
    remove_path_root.resizable(0, 0)
    remove_path_root.config(bg ='#f25252')

    remove_path_frame = Frame(remove_path_root, bg='#f25252')
    remove_path_frame.pack(expand=True)
        
    def verif_remove_path():
        path_string = remove_path_combobox.get()
        path = path_string.split(',')
        remove_path(path[0], path[1])
        list_paths_update(remove_path_combobox)

    remove_path_combobox = AutocompleteCombobox(remove_path_frame)
    list_paths_update(remove_path_combobox)
    remove_path_button = Button(remove_path_frame, text='Remove', command=verif_remove_path)
    
    
    remove_path_combobox.pack()
    remove_path_button.pack()
# %%
nodes_menu = Menu(
    main_menu,
    tearoff=0
    )
nodes_menu.add_command(
    label='Add a node...',
    command= open_add_node_window
    )
nodes_menu.add_command(
    label='Remove a node...',
    command= open_remove_node_window
    )

paths_menu = Menu(
    main_menu,
    tearoff=0
)
paths_menu.add_command(
    label='Add a path...',
    command=open_add_path_window
)
paths_menu.add_command(
    label='Remove a path...',
    command=open_remove_path_window
)
question_mark_menu = Menu(
    main_menu,
    tearoff=0
    )
question_mark_menu.add_command(
    label='Help !'
    )
question_mark_menu.add_command(
    label='About us...'
)

# %%
main_menu.add_cascade(
    label = 'Nodes',
    menu=nodes_menu
)
main_menu.add_cascade(
    label='Paths',
    menu= paths_menu
)
main_menu.add_cascade(
    label = '?',
    menu=question_mark_menu
)

open_main_windows()
# %%
root.mainloop()


