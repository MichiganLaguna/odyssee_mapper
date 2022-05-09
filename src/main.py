# %%
from tkinter import Button, Entry, Label, Toplevel, StringVar, Frame, Tk, Menu
from tkinter.filedialog import askopenfilename as fname, asksaveasfilename as sname
from tkinter.messagebox import showinfo
from dataclasses import dataclass, field
import nodes as nd


@dataclass(slots=True)
class File:
    PATH: str = field(init=False, repr=False)
    DIR: str = field(default="./", init=False, repr=False)
    TYPE: str = field(default=".paths", init=False, repr=False)


def create_file(file: File) -> None:
    filetypes = (("PATH", f"*{file.TYPE}"),)
    filename = sname(
        title="Create a file",
        initialdir=file.DIR,
        filetypes=filetypes,
    )
    file.PATH = filename
    with nd.Database(file.PATH + file.TYPE):
        showinfo(
            title="File successfully created!",
            message=f"{file.PATH}{file.TYPE} has been created!",
        )


def open_file(file: File) -> None:
    filetypes = (("PATH", file.TYPE),)
    filename = fname(
        title="Open a file",
        initialdir=file.DIR,
        filetypes=filetypes,
    )
    file.PATH = filename


class BetterEntry(Entry):
    def __init__(self, master=None, **kwargs) -> None:
        self.var = StringVar()
        Entry.__init__(self, master, textvariable=self.var, **kwargs)

    def get(self) -> str:
        result = super().get()
        self.var.set(str())
        return result


class OnlyIntEntry(BetterEntry):
    def __init__(self, master=None, **kwargs) -> None:
        BetterEntry.__init__(self, master, **kwargs)
        self.old_value = ""
        self.var.trace("w", self.check)

    def check(self, *args) -> None:
        if self.var.get().isdigit() or self.var.get() == "":
            # the current value is only digits; allow this
            self.old_value = self.var.get()
        else:
            # there's non-digit characters in the input; reject this
            self.var.set(self.old_value)


class MainWindow(Tk):
    def __init__(self, **kwargs):
        Tk.__init__(self, **kwargs)
        self.title("Odyssee pathfinder")
        self.geometry("400x400")
        self.resizable(0, 0)
        self.frame = Frame(self, bg="#f25252")
        self.frame.pack()
        self.main_menu = Menu(self.frame)
        self.config(menu=self.main_menu, bg="#f25252")
        self.cursor = File()

        self.file_menu = Menu(self.main_menu, tearoff=0)
        self.file_menu.add_command(
            label="Create a file", command=lambda: create_file(self.cursor)
        )
        self.file_menu.add_command(
            label="Open a file", command=lambda: open_file(self.cursor)
        )
        self.file_menu.add_command(label="View...")

        self.paths_menu = Menu(self.main_menu, tearoff=0)
        self.paths_menu.add_command(
            label="Add a path...", command=lambda: AddPathWindow(self)
        )
        self.paths_menu.add_command(label="Remove a path...")

        self.question_mark_menu = Menu(self.main_menu, tearoff=0)
        self.question_mark_menu.add_command(label="Help!")
        self.question_mark_menu.add_command(label="About us...")

        self.main_menu.add_cascade(label="File", menu=self.file_menu)
        self.main_menu.add_cascade(label="Paths", menu=self.paths_menu)
        self.main_menu.add_cascade(label="?", menu=self.question_mark_menu)


class Window(Toplevel):
    def __init__(self, master: MainWindow = None, **kwargs) -> None:
        Toplevel.__init__(self, master, **kwargs)
        self.geometry("300x300")
        self.resizable(0, 0)
        self.config(bg="#f25252")
        self.frame = Frame(self, bg="#f25252")
        self.frame.pack(expand=True)


class AddPathWindow(Window):
    def __init__(self, master: MainWindow = None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.title("Add a path...")
        self.construct_body()
        self.master = master

    def add_path(self) -> None:
        starting_node = self.start_entry.get()
        ending_node = self.end_entry.get()
        length = self.length_entry.get()
        print(self.master.cursor.PATH)

    def construct_body(self) -> None:
        self.start_label = Label(self.frame, text="Starting node", width=44)
        self.start_entry = BetterEntry(self.frame, width=50)
        self.start_label.pack()
        self.start_entry.pack()

        self.end_label = Label(self.frame, text="Ending node", width=44)
        self.end_entry = BetterEntry(self.frame, width=50)
        self.end_label.pack()
        self.end_entry.pack()

        self.length_label = Label(self.frame, text="Length", width=44)
        self.length_entry = OnlyIntEntry(self.frame, width=50)
        self.length_label.pack()
        self.length_entry.pack()

        self.submit = Button(self.frame, text="Submit!", command=self.add_path)
        self.submit.pack()


# %%
root = MainWindow()
root.mainloop()
# %%
