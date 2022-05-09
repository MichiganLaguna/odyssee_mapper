"""@file sqlite3_wrapper.py"""

import sqlite3


class Database:
    """A wrapper around the sqlite3 python library.
    The Database class is a high-level wrapper around the sqlite3
    library. It allows users to create a database connection and
    write to or fetch data from the selected database. It also has
    various utility functions such as getLast(), which retrieves
    only the very last item in the database, toCSV(), which writes
    entries from a database to a CSV file, and summary(), a function
    that takes a dataset and returns only the maximum, minimum and
    average for each column. The Database can be opened either by passing
    on the name of the sqlite database in the constructor, or optionally
    after constructing the database without a name first, the open()
    method can be used. Additionally, the Database can be opened as a
    context method, using a 'with .. as' statement. The latter takes
    care of closing the database."""

    def __init__(self, name: str = None) -> None:
        """The constructor of the Database class

        The constructor can either be passed the name of the database to open
        or not, it is optional. The database can also be opened manually with
        the open() method or as a context manager.

        @param name Optionally, the name of the database to open.

        @see open()"""

        self.conn = None
        self.cursor = None

        if name:
            self.open(name)

    def open(self, name: str) -> None:
        """Opens a new database connection.

        This function manually opens a new database connection. The database
        can also be opened in the constructor or as a context manager.

        @param name The name of the database to open.

        @see \__init\__()"""
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()

    def close(self):
        """Function to close a database connection.

        The database connection needs to be closed before you exit a program,
        otherwise changes might be lost. You can also manage the database
        connection as a context manager, then the closing is done for you. If
        you opened the database connection with the open() method or with the
        constructor ( \__init\__() ), you must close the connection with this
        method.

        @see open()

        @see \__init\__()"""

        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self.close()

    def get(self, table: str, columns: str, limit: str = None) -> list[str]:
        """Function to fetch/query data from a database.

        This is the main function used to query a database for data.

        @param table The name of the database's table to query from.

        @param columns The string of columns, comma-separated, to fetch.

        @param limit Optionally, a limit of items to fetch."""

        query = f"SELECT {columns} from {table};"
        self.cursor.execute(query)

        rows = self.cursor.fetchall()

        return rows[len(rows) - limit if limit else 0 :]

    def get_last(self, table: str, columns: str) -> list[str]:
        """Utilty function to get the last row of data from a database.

        @param table The database's table from which to query.

        @param columns The columns which to query."""

        return self.get(table, columns, limit=1)[0]

    @staticmethod
    def to_csv(data, fname: str = "output.csv") -> None:
        """Utility function that converts a dataset into CSV format.

        @param data The data, retrieved from the get() function.

        @param fname The file name to store the data in.

        @see get()"""

        with open(fname, "a", encoding="utf8") as file:
            file.write(",".join([str(j) for i in data for j in i]))

    def write(self, table: str, columns: list[tuple], data: list[tuple]) -> None:
        """Function to write data to the database.

        The write() function inserts new data into a table of the database.

        @param table The name of the database's table to write to.

        @param columns The columns to insert into, as a list of tuples.

        @param data The new data to insert, as a list."""
        columns = "".join([f", {column}" for column in columns]).lstrip(", ")
        data = "".join([f", '{line}'" for line in data]).lstrip(", ")

        query = f"INSERT INTO {table} ({columns}) VALUES ({data});"

        self.cursor.execute(query)

    def create_table(self, table: str, columns: list[tuple]) -> None:
        """Function to create a table in the database
        @param table The name of the database's table to create
        @param columns The columns to add, as a list of tuple."""

        columns = ", ".join(
            [" ".join([f"{arg}" for arg in column]).lstrip(" ") for column in columns]
        ).lstrip(", ")

        query = f"CREATE TABLE {table}({columns})"

        self.cursor.execute(query)

    def remove_table(self, table: str) -> None:
        """Function to remove a table in the database
        @param table The name of the database's table to remove"""
        query = f"DROP TABLE if exists {table}"

        self.cursor.execute(query)

    def add_column(self, table: str, column: str, data: str) -> None:
        """Function to add a column to a table
        @param table The name of the database where the column will be added
        @param column The name of the column to add to the table
        @param data The data type of the column to add to the table"""
        query = f"ALTER TABLE {table} ADD COLUMN {column} {data}"

        self.cursor.execute(query)

    def remove_column(self, table: str, column: str) -> None:
        """Function to remove a column from a table
        @param table The name of the database where the column will be removed
        @param column The name of the column to remove from the table"""
        query = f"ALTER TABLE {table} DROP COLUMN {column}"

        self.cursor.execute(query)

    def change_type(self, table: str, column: str, data: str) -> None:
        """Function to change the type of a column in a table
        @param table The name of the database where the column will be changed
        @param column The name of the column to change
        @param data The data type of the new column"""
        query = f"ALTER TABLE {table} ALTER COLUMN {column} {data}"

        self.cursor.execute(query)

    def delete_rows(self, table: str, condition: str) -> None:
        """Function to delete rows in a table depending on the condition
        @param table The name of the database where to delete
        @param condition The condition for deletion in the table"""
        query = f"DELETE FROM {table} WHERE {condition}"

        self.cursor.execute(query)

    def select(self, table: str, columns: str, condition: str) -> None:
        """Function to select rows in a table depending on the condition
        @param table The name of the database where to select
        @param condition The condition for deletion in the table"""
        query = f"SELECT {columns} FROM {table} WHERE {condition}"

        self.cursor.execute(query)

        return self.cursor.fetchall()

    def query(self, sql: str) -> None:
        """Function to query any other SQL statement.

        This function is there in case you want to execute any other sql
        statement other than a write or get.

        @param sql A valid SQL statement in string format."""
        self.cursor.execute(sql)

    @staticmethod
    def summary(rows) -> list:
        """Utility function that summarizes a dataset.

        This function takes a dataset, retrieved via the get() function, and
        returns only the maximum, minimum and average for each column.

        @param rows The retrieved data."""

        # split the rows into columns
        cols = [[r[c] for r in rows] for c in range(len(rows[0]))]

        # the time in terms of fractions of hours of how long ago
        # the sample was assumes the sampling period is 10 minutes
        timing = lambda col: f"{(len(rows) - col) / 6.0:.1f}"

        # return a tuple, consisting of tuples of the maximum,
        # the minimum and the average for each column and their
        # respective time (how long ago, in fractions of hours)
        # average has no time, of course
        ret = []

        for col in cols:
            hi_ = max(col)
            hi_t = timing(col.index(hi_))

            lo_ = min(col)
            lo_t = timing(col.index(lo_))

            avg = sum(col) / len(rows)

            ret.append(((hi_, hi_t), (lo_, lo_t), avg))
        return ret
