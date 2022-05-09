###########################################################################
#
## @file sqlite3_wrapper.py
#
###########################################################################

import sqlite3
from tkinter.messagebox import showerror

###########################################################################
#
##   A wrapper around the sqlite3 python library.
#
#    The Database class is a high-level wrapper around the sqlite3
#    library. It allows users to create a database connection and
#    write to or fetch data from the selected database. It also has
#    various utility functions such as getLast(), which retrieves
#    only the very last item in the database, toCSV(), which writes
#    entries from a database to a CSV file, and summary(), a function
#    that takes a dataset and returns only the maximum, minimum and
#    average for each column. The Database can be opened either by passing
#    on the name of the sqlite database in the constructor, or optionally
#    after constructing the database without a name first, the open()
#    method can be used. Additionally, the Database can be opened as a
#    context method, using a 'with .. as' statement. The latter takes
#    care of closing the database.
#
###########################################################################
class Database:
    class Error(Exception):
        # Base class for other exceptions
        def __init__(self, number: int, message: str) -> None:
            showerror(title=f"Error {self.number}!", message=message)

    #######################################################################
    #
    ## The constructor of the Database class
    #
    #  The constructor can either be passed the name of the database to open
    #  or not, it is optional. The database can also be opened manually with
    #  the open() method or as a context manager.
    #
    #  @param name Optionally, the name of the database to open.
    #
    #  @see open()
    #
    #######################################################################
    def __init__(self, name=None):

        self.conn = None
        self.cursor = None

        if name:
            self.open(name)

    #######################################################################
    #
    ## Opens a new database connection.
    #
    #  This function manually opens a new database connection. The database
    #  can also be opened in the constructor or as a context manager.
    #
    #  @param name The name of the database to open.
    #
    #  @see \__init\__()
    #
    #######################################################################
    def open(self, name):
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()

    #######################################################################
    #
    ## Function to close a database connection.
    #
    #  The database connection needs to be closed before you exit a program,
    #  otherwise changes might be lost. You can also manage the database
    #  connection as a context manager, then the closing is done for you. If
    #  you opened the database connection with the open() method or with the
    #  constructor ( \__init\__() ), you must close the connection with this
    #  method.
    #
    #  @see open()
    #
    #  @see \__init\__()
    #
    #######################################################################
    def close(self):

        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self.close()

    #######################################################################
    #
    ## Function to fetch/query data from a database.
    #
    #  This is the main function used to query a database for data.
    #
    #  @param table The name of the database's table to query from.
    #
    #  @param columns The string of columns, comma-separated, to fetch.
    #
    #  @param limit Optionally, a limit of items to fetch.
    #
    #######################################################################
    def get(self, table, columns, limit=None):

        query = "SELECT {0} from {1};".format(columns, table)
        self.cursor.execute(query)

        # fetch data
        rows = self.cursor.fetchall()

        return rows[len(rows) - limit if limit else 0 :]

    #######################################################################
    #
    ## Utilty function to get the last row of data from a database.
    #
    #  @param table The database's table from which to query.
    #
    #  @param columns The columns which to query.
    #
    #######################################################################
    def get_last(self, table, columns):

        return self.get(table, columns, limit=1)[0]

    #######################################################################
    #
    ## Utility function that converts a dataset into CSV format.
    #
    #  @param data The data, retrieved from the get() function.
    #
    #  @param fname The file name to store the data in.
    #
    #  @see get()
    #
    #######################################################################
    @staticmethod
    def to_csv(data, fname="output.csv"):

        with open(fname, "a") as file:
            file.write(",".join([str(j) for i in data for j in i]))

    #######################################################################
    #
    ## Function to write data to the database.
    #
    #  The write() function inserts new data into a table of the database.
    #
    #  @param table The name of the database's table to write to.
    #
    #  @param columns The columns to insert into, as a list.
    #
    #  @param data The new data to insert, as a list.
    #
    #######################################################################
    def write(self, table, columns, data):
        columns = "".join([f", {column}" for column in columns]).lstrip(", ")
        data = "".join([f", '{line}'" for line in data]).lstrip(", ")

        query = f"INSERT INTO {table} ({columns}) VALUES ({data});"

        self.cursor.execute(query)

    #######################################################################
    #
    ## Function to create a table in the database
    # @param table The name of the database's table to create
    # @param columns The columns to add, as a list of tuple.
    #
    #######################################################################
    def create_table(self, table, columns):

        columns = ", ".join(
            [" ".join([f"{arg}" for arg in column]).lstrip(" ") for column in columns]
        ).lstrip(", ")

        query = f"CREATE TABLE {table}({columns})"

        self.cursor.execute(query)

    #######################################################################
    #
    ## Function to remove a table in the database
    # @param table The name of the database's table to remove
    #
    #######################################################################
    def remove_table(self, table):
        query = f"DROP TABLE if exists {table}"

        self.cursor.execute(query)

    #######################################################################
    #
    ## Function to add a column to a table
    # @param table The name of the database where the column will be added
    # @param column The name of the column to add to the table
    # @param data The data type of the column to add to the table
    #
    #######################################################################
    def add_column(self, table, column, data):
        query = f"ALTER TABLE {table} ADD COLUMN {column} {data}"

        self.cursor.execute(query)

    #######################################################################
    #
    ## Function to remove a column from a table
    # @param table The name of the database where the column will be removed
    # @param column The name of the column to remove from the table
    #
    #######################################################################
    def remove_column(self, table, column):
        query = f"ALTER TABLE {table} DROP COLUMN {column}"

        self.cursor.execute(query)

    #######################################################################
    #
    ## Function to change the type of a column in a table
    # @param table The name of the database where the column will be changed
    # @param column The name of the column to change
    # @param data The data type of the new column
    #
    #######################################################################
    def change_type(self, table, column, data):
        query = f"ALTER TABLE {table} ALTER COLUMN {column} {data}"

        self.cursor.execute(query)

    #######################################################################
    #
    ## Function to delete rows in a table depending on the condition
    # @param table The name of the database where to delete
    # @param condition The condition for deletion in the table
    #
    #######################################################################
    def delete_rows(self, table, condition):
        query = f"DELETE FROM {table} WHERE {condition}"

        self.cursor.execute(query)

    def select(self, table, columns, condition):
        query = f"SELECT {columns} FROM {table} WHERE {condition}"

        self.cursor.execute(query)

        return self.cursor.fetchall()

    #######################################################################
    #
    ## Function to query any other SQL statement.
    #
    #  This function is there in case you want to execute any other sql
    #  statement other than a write or get.
    #
    #  @param sql A valid SQL statement in string format.
    #
    #######################################################################
    def query(self, sql):
        self.cursor.execute(sql)

    #######################################################################
    #
    ## Utility function that summarizes a dataset.
    #
    #  This function takes a dataset, retrieved via the get() function, and
    #  returns only the maximum, minimum and average for each column.
    #
    #  @param rows The retrieved data.
    #
    #######################################################################
    @staticmethod
    def summary(rows):

        # split the rows into columns
        cols = [[r[c] for r in rows] for c in range(len(rows[0]))]

        # the time in terms of fractions of hours of how long ago
        # the sample was assumes the sampling period is 10 minutes
        t = lambda col: "{:.1f}".format((len(rows) - col) / 6.0)

        # return a tuple, consisting of tuples of the maximum,
        # the minimum and the average for each column and their
        # respective time (how long ago, in fractions of hours)
        # average has no time, of course
        ret = []

        for c in cols:
            hi = max(c)
            hi_t = t(c.index(hi))

            lo = min(c)
            lo_t = t(c.index(lo))

            avg = sum(c) / len(rows)

            ret.append(((hi, hi_t), (lo, lo_t), avg))
        return ret
