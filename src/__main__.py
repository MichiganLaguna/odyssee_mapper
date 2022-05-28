from tkinter.filedialog import askopenfilename as fname, asksaveasfilename as sname
from tkinter.messagebox import showinfo, showerror
from dataclasses import dataclass, field
from hashlib import sha256
from tkinter import (
    DISABLED,
    Button,
    Checkbutton,
    Entry,
    Label,
    Toplevel,
    StringVar,
    Frame,
    Tk,
    Menu,
    IntVar,
)
from sqlite3 import IntegrityError as IE
from ttkwidgets.autocomplete import AutocompleteCombobox
import nodes as nd


@dataclass(slots=True)
class File:
    PATH: StringVar = field(repr=False)
    DIR: str = field(default="./", init=False, repr=False)
    TYPE: str = field(default=".db", init=False, repr=False)


@dataclass(slots=True)
class DatabaseStructure:
    TABLE_NAME: str = field(default="Paths", init=False, repr=False)
    COLUMNS: tuple[tuple[str]] = (
        ("ID", "text", "PRIMARY KEY"),
        ("Start", "text", "NOT NULL"),
        ("End", "text", "NOT NULL"),
        ("Length", "integer", "NOT NULL"),
    )
    COLUMNS_NAMES: list[str] = ("ID", "Start", "End", "Length")


class BetterAutocompleteCombobox(AutocompleteCombobox):
    def __init__(self, master=None, completevalues=None, **kwargs):
        super().__init__(master, completevalues, **kwargs)

    def get_val(self):
        result = self.get()
        self.set(str())
        return result


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


def id_generator(input_string: str) -> int:
    """
    Function to generate a unique id for a given string
    @param input The string to generate an id for
    @returns The id for the given string
    """
    return sha256(input_string.encode("utf-8")).hexdigest()


class MainWindow(Tk):
    def init_graph(self) -> dict[str, dict[str, int]]:
        with nd.Database(self.cursor.PATH.get()) as db:
            self.list_all = db.get(self.struct.TABLE_NAME, "Start, End, Length")
            self.graph = nd.build_graph(self.list_all)

    def update_points(self, *args) -> None:
        with nd.Database(self.cursor.PATH.get()) as db:
            if self.cursor.PATH.get() == str():
                self.paths_menu.entryconfig(0, state=DISABLED)
                self.paths_menu.entryconfig(1, state=DISABLED)
            else:
                self.paths_menu.entryconfig(0, state="normal")
                self.paths_menu.entryconfig(1, state="normal")
                self.init_graph()
                self.start_point["values"] = [key for key in self.graph.keys()]

    def update_end_point(self, arg):
        self.dist, self.precedent = nd.dijkstra(
            self.graph, self.start_point.get(), self.list_all
        )
        self.end_point["values"] = [
            node
            for node in self.dist.keys()
            if self.dist[node] < 999 and self.dist[node] != 0
        ]

    def find_path(self) -> None:
        start = self.start_point.get()
        end = self.end_point.get()
        start_values = self.start_point["values"]
        end_values = self.end_point["values"]
        if start not in start_values or start == "":
            showerror(
                title="Error!",
                message="The start point is not in the database!",
            )
        elif end not in end_values or end == "":
            showerror(
                title="Error!",
                message="The end point is not in the database!",
            )
        else:
            shortest_path = nd.find_shortest_path(start, end, self.precedent)
            if shortest_path is None:
                showerror(
                    title="Error!",
                    message="There is no path between the two points!",
                )
            else:
                shortest_path.reverse()
                showinfo(
                    title="Path found!",
                    message=f"The shortest path between {start} and {end} is:\n{shortest_path}\n and is {self.dist[end]} long",
                )

    def create_file(self) -> None:
        filetypes = (("PATH", f"*{self.cursor.TYPE}"),)
        filename = sname(
            title="Create a file",
            initialdir=self.cursor.DIR,
            filetypes=filetypes,
        )
        if filename != "":
            filename = filename.strip(".db")
            with nd.Database(filename + self.cursor.TYPE) as db:
                db.create_table(
                    table=self.struct.TABLE_NAME, columns=self.struct.COLUMNS
                )
                showinfo(
                    title="File successfully created!",
                    message=f"{filename}{self.cursor.TYPE} has been created!",
                )
                self.cursor.PATH.set(filename + self.cursor.TYPE)

    def open_file(self) -> None:
        filetypes = (("PATH", self.cursor.TYPE),)
        filename = fname(
            title="Open a file",
            initialdir=self.cursor.DIR,
            filetypes=filetypes,
        )
        self.cursor.PATH.set(filename)
        self.update_points()

    def __init__(self, **kwargs):
        Tk.__init__(self, **kwargs)
        self.title("Odyssee pathfinder")
        self.geometry("300x300")
        self.resizable(0, 0)
        self.frame = Frame(self, bg="#f25252")
        self.frame.pack()
        self.main_menu = Menu(self.frame)
        self.config(menu=self.main_menu, bg="#f25252")
        self.cursor = File(StringVar())
        self.struct = DatabaseStructure()
        self.cursor.PATH.trace_add("write", self.update_points)
        self.graph: dict[str, dict[str, int]] = dict()
        self.dist: dict[str, int] = dict()
        self.precedent: dict[str, str] = dict()
        self.list_all: list[tuple[str, str, int]] = list()

        self.file_menu = Menu(self.main_menu, tearoff=0)
        self.file_menu.add_command(label="Create a file", command=self.create_file)
        self.file_menu.add_command(label="Open a file", command=self.open_file)
        self.file_menu.add_command(label="View...")

        self.paths_menu = Menu(self.main_menu, tearoff=0)
        self.paths_menu.add_command(
            label="Add a path...", command=lambda: AddPathWindow(self), state=DISABLED
        )
        self.paths_menu.add_command(
            label="Remove a path...",
            command=lambda: DeletePathWindow(self),
            state=DISABLED,
        )

        self.question_mark_menu = Menu(self.main_menu, tearoff=0)
        self.question_mark_menu.add_command(label="Help!")
        self.question_mark_menu.add_command(label="About us...")

        self.main_menu.add_cascade(label="File", menu=self.file_menu)
        self.main_menu.add_cascade(label="Paths", menu=self.paths_menu)
        self.main_menu.add_cascade(label="?", menu=self.question_mark_menu)

        self.start_label = Label(self.frame, text="Starting Node", width=44)
        self.start_point = BetterAutocompleteCombobox(self.frame, width=48)

        self.end_label = Label(self.frame, text="Ending Node", width="44")
        self.end_point = BetterAutocompleteCombobox(self.frame, width=48)

        self.button = Button(
            self.frame, text="Find shortest path !", command=self.find_path
        )
        self.start_point.bind("<<ComboboxSelected>>", self.update_end_point)

        self.start_label.pack()
        self.start_point.pack()
        self.end_label.pack()
        self.end_point.pack()
        self.button.pack()


class Window(Toplevel):
    def __init__(self, master: MainWindow = None, **kwargs) -> None:
        Toplevel.__init__(self, master, **kwargs)
        self.geometry("300x300")
        self.resizable(0, 0)
        self.config(bg="#f25252")
        self.frame = Frame(self, bg="#f25252")
        self.frame.pack(expand=True)
        self.grab_set()

        def handler():
            self.master.update_points()
            self.destroy()

        self.protocol("WM_DELETE_WINDOW", handler)


class AddPathWindow(Window):
    def __init__(self, master: MainWindow = None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.title("Add a path...")
        self.construct_body()
        self.master = master

    def update_combo(
        self,
    ) -> None:
        self.master.update_points()
        tmp = dict()
        for i in self.master.list_all:
            tmp[i[0]] = 1
            tmp[i[1]] = 1
        self.start_combo["values"] = [key for key in tmp]

    def update_end_combo(self, event) -> None:
        self.end_combo["values"] = [
            key for key in self.start_combo["values"] if key != self.start_combo.get()
        ]

    def add_path(self) -> None:
        starting_node = self.start_combo.get().strip()
        ending_node = self.end_combo.get().strip()
        length = self.length_entry.get().strip()
        if starting_node and ending_node and length:
            if starting_node == ending_node:
                showinfo(
                    title="Error",
                    message="Starting and ending node cannot be the same!",
                )
            else:
                with nd.Database(self.master.cursor.PATH.get()) as db:
                    try:
                        if self.check_var.get() == 1:
                            sep = "<-"
                            ID = id_generator(ending_node + starting_node)
                            db.write(
                                self.master.struct.TABLE_NAME,
                                self.master.struct.COLUMNS_NAMES,
                                [
                                    ID,
                                    ending_node,
                                    starting_node,
                                    length,
                                ],
                            )
                        else:
                            sep = "-"
                        ID = id_generator(starting_node + ending_node)
                        db.write(
                            self.master.struct.TABLE_NAME,
                            self.master.struct.COLUMNS_NAMES,
                            [
                                ID,
                                starting_node,
                                ending_node,
                                length,
                            ],
                        )

                        showinfo(
                            title="Path successfully added!",
                            message=f"{starting_node}{sep}{length}->{ending_node} has been added!",
                        )
                    except IE:
                        showinfo(
                            title="Path already exists!",
                            message=f"{starting_node}{sep}{length}->{ending_node} already exists!",
                        )
                self.update_combo()
        else:
            showerror(
                title="Incomplete entry!",
                message="Make sure to submit every argument...",
            )

    def construct_body(self) -> None:

        self.check_var = IntVar()
        self.check_button = Checkbutton(
            self.frame,
            text="Two-way",
            variable=self.check_var,
            onvalue=1,
            offvalue=0,
        )
        self.check_button.pack()
        self.start_label = Label(self.frame, text="Starting node", width=44)
        self.start_combo = BetterAutocompleteCombobox(self.frame, width=48)
        self.start_label.pack()
        self.start_combo.pack()

        self.end_label = Label(self.frame, text="Ending node", width=44)
        self.end_combo = BetterAutocompleteCombobox(self.frame, width=48)
        self.end_label.pack()
        self.end_combo.pack()
        self.update_combo()
        self.start_combo.bind("<<ComboboxSelected>>", self.update_end_combo)

        self.length_label = Label(self.frame, text="Length", width=44)
        self.length_entry = OnlyIntEntry(self.frame, width=50)
        self.length_label.pack()
        self.length_entry.pack()

        self.submit = Button(self.frame, text="Submit!", command=self.add_path)
        self.submit.pack()


class DeletePathWindow(Window):
    def __init__(self, master: MainWindow = None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.geometry("300x300")
        self.title("Remove a path...")
        self.construct_body()
        self.master = master

    @staticmethod
    def graph_to_list(graph) -> None:
        list_graph = []
        for node in graph:
            for neighbours in graph[node].items():
                list_graph.append(f"{node}-{neighbours[1]}->{neighbours[0]}")
        return list_graph

    def update_combo(
        self,
    ) -> None:
        self.master.update_points()
        self.combo["values"] = self.graph_to_list(self.master.graph)

    def delete_path(self) -> None:
        start = self.combo.get().strip()
        start, end = start.split("->")
        start, length = start.split("-")
        print(start, end, length)

        with nd.Database(self.master.cursor.PATH.get()) as db:
            db.delete_rows(
                self.master.struct.TABLE_NAME, f"ID = {id_generator(start + end)} "
            )
            showinfo(
                title="Path successfully deleted!",
                message=f"{start}-{length}->{end} has been deleted!",
            )
        self.update_combo()

    def construct_body(self) -> None:
        self.label = Label(self.frame, text="Nodes", width=44)
        self.combo = BetterAutocompleteCombobox(self.frame, width=48)
        self.button = Button(self.frame, text="Delete", command=self.delete_path)
        self.label.pack()
        self.combo.pack()
        self.button.pack()

        self.update_combo()


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
