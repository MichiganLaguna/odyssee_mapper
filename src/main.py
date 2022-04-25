# %%
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
    nd.write_csv(nd.FILE_PATHS, [[node_a, node_b, length]])
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
    nd.rm_file(nd.FILE_PATHS)
    nd.write_csv(nd.FILE_PATHS, list_all_paths)


#Modify a path in the file containing all paths, return None if sucessfull and return -1 if path didn't exist and add it.
def change_path(node_a, node_b, length):
    if add_path(node_a, node_b, length) is not None:
        return -1
    else:
        list_all_paths = update_paths(node_a, node_b, length)
        nd.rm_file(nd.FILE_PATHS)
        nd.write_csv(nd.FILE_PATHS, list_all_paths)
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
            messagebox.showerror(title='Node Error', message="I'm afraid this node already exist")
        add_node_entry.delete(0,len(node_name))

    add_node_entry = Entry(add_node_frame)
    add_node_button = Button(add_node_frame, text='Add', command=lambda:add_node_verif(add_node_entry.get()))
    add_node_quit = Button(add_node_frame, text='Quit !', command=add_node_root.destroy)

    add_node_entry.pack()
    add_node_button.pack()
    add_node_quit.pack()


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

    def list_nodes_update():
        list_nodes = []
        for node in nd.open_csv(nd.FILE_NODES, 1):
            list_nodes.append(node[0])
        remove_node_combobox.config(completevalues=list_nodes)
    list_nodes_update()
    def rem_node_verif():
        node_ = remove_node_combobox.get()
        remove_node(node_)
        list_nodes_update()
        remove_node_combobox.delete(0, len(node_))

    remove_node_button = Button(remove_node_frame, text='Remove', command= rem_node_verif)
    remove_node_combobox.pack()
    remove_node_button.pack()  

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
    label = '?',
    menu=question_mark_menu
)

# %%
root.mainloop()


