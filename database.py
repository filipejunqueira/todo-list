# Import the sqlite3 module for interacting with SQLite databases
# Import the datetime module to handle date and time information
# Import the todos class from the model module - This is the class from the other file
import sqlite3
from datetime import datetime
from model import Todo
from pathlib import Path  # <-- Import Path


# / "todos.db" joins the directory path with the filename
DB_PATH = Path(__file__).parent / "todos.db"

# Here first we import the sqlite3 module to interact with SQLite databases
connection = sqlite3.connect(DB_PATH)
# We create a cursor object to execute SQL commands
# (This is a pointer to the database that we can use to execute SQL commands)
cursor = connection.cursor()


# We initiate the database by creating a table if it doesn't exist
def create_table():
    # The sintax here is a little annoying. Remember that todos is the name of the database (aka the file todos.db).
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS todos (
            task TEXT,
            category TEXT,
            date_added TEXT,
            date_completed TEXT,
            status INTEGER,
            position INTEGER
        )"""
    )


# Here we actually create the table.
create_table()

# For eaach function bellow we will use the cursor object to execute SQL commands.
# The insert_todo function takes a Toddo object and insert in the next available position.
# It first checks how many todos are in the database and sets the position of the new todo to that number.
# If there are no todos, it sets the position to 0 (aka the first).
# Notice the atypical sintax on cursor.execute. This is to avoid SQL injection attacks.
# The :task, :category, etc. are placeholders for the values that we pass in the dictionary.
# The dictionary keys must match the placeholders in the SQL command.
# Never use string formatting to insert values into SQL commands. This is a common mistake that can lead to SQL injection attacks.


def insert_todo(todo: Todo):
    cursor.execute("select count(*) from todos")
    count = cursor.fetchone()[0]
    todo.position = count if count else 0
    with connection:
        cursor.execute(
            "INSERT INTO todos VALUES (:task, :category, :date_added, :date_completed, :status, :position)",
            {
                "task": todo.task,
                "category": todo.category,
                "date_added": todo.date_added,
                "date_completed": todo.date_completed,
                "status": todo.status,
                "position": todo.position,
            },
        )


# The get all_todos function returns a list of all todos in the database.
# It uses the cursor object to execute a SELECT command and fetches all the results and adds them to a list of toddo objects and returns that.
# Important to note that Todo(*result) is a little trick to unpack the result tuple into the Todo constructor.
# This is a common pattern in Python to create objects from tuples or lists.
# The method fetchall() returns all rows of a query result, and the result is a list of tuples. So each result is one row of the table.


def get_all_todos() -> list[Todo]:
    cursor.execute("SELECT * FROM todos ORDER BY position ASC")
    results = cursor.fetchall()
    todos = []
    for result in results:
        todos.append(Todo(*result))
    return todos


# The delete_todo function takes a position and deletes the todo at that position.
# It first checks how many todos are in the database and then deletes the todo at the given position.
# After that, it updates the position of all todos after the deleted one to fill the gap.
# It uses a for loop to iterate over the positions and calls the change_position function to update the position of each todo.
# The with connection: statement is used to ensure that the changes are committed to the database.
# It's a context manager that automatically commits the changes when the block is exited.


def delete_todo(position):
    cursor.execute("SELECT count(*) FROM todos")
    count = cursor.fetchone()[0]

    with connection:
        cursor.execute(
            "DELETE FROM todos WHERE position = :position", {"position": position}
        )
        # Update the position of all todos after the deleted one
        for pos in range(position + 1, count):
            change_position(pos, pos - 1, False)


"""


def delete_todo(position: int):  # position is 0-based index
    with connection:
        # Delete the item
        cursor.execute(
            "DELETE FROM todos WHERE position = :position", {"position": position}
        )
        cursor.execute(
            "UPDATE todos SET position = position - 1 WHERE position > :position",
            {"position: position"},
        )

"""

""
# The change_position function takes an old position and a new position and updates the position of the todo at the old position to the new position.
# It uses the with connection: statement to ensure that the changes are committed to the database.
# This is useful when we want to update the position of a todo after deleting another todo and we only use it in this context.


def change_position(old_position, new_position, commit=True):
    with connection:
        cursor.execute(
            "UPDATE todos SET position = :new_position WHERE position = :old_position",
            {"new_position": new_position, "old_position": old_position},
        )
        if commit:
            connection.commit()


# Update_todo function has the same logic as the delete_todo function but it has 3 "logical" branches.
# It first checks if the task and category are not None and updates both.
# If only one of them is not None, it updates only that one.
# It uses the with connection: statement to ensure that the changes are committed to the database.
# This is useful when we want to update the task or category of a task.


def move_todo(from_position: int, to_position: int):
    """Moves a todo item from one position to another, adjusting others."""
    if from_position == to_position:
        return  # Nothing to do

    with connection:
        # --- Transaction Start ---

        # Get the count to validate to_position later if needed, although bounds check is better
        cursor.execute("SELECT count(*) FROM todos")
        count = cursor.fetchone()[0]
        if not (0 <= to_position < count):
            print(
                f"Error: Target position {to_position+1} is out of range (1-{count})."
            )  # User-friendly index
            # Or raise an exception: raise IndexError("Target position out of range")
            return  # Stop execution if target is invalid

        # Temporarily move the target item out of the way
        # Using a unique temporary position like -1
        cursor.execute(
            "UPDATE todos SET position = -1 WHERE position = :from_pos",
            {"from_pos": from_position},
        )

        if from_position < to_position:
            # Moving Down: Shift items between from_position and to_position UP by 1
            cursor.execute(
                """UPDATE todos
                   SET position = position - 1
                   WHERE position > :from_pos AND position <= :to_pos""",
                {"from_pos": from_position, "to_pos": to_position},
            )
        else:  # from_position > to_position
            # Moving Up: Shift items between to_position and from_position DOWN by 1
            cursor.execute(
                """UPDATE todos
                   SET position = position + 1
                   WHERE position >= :to_pos AND position < :from_pos""",
                {"to_pos": to_position, "from_pos": from_position},
            )

        # Place the target item in its final position
        cursor.execute(
            "UPDATE todos SET position = :to_pos WHERE position = -1",
            {"to_pos": to_position},
        )

        # --- Transaction End (Commit happens automatically) ---


def update_todo(position: int, task: str, category: str):
    with connection:
        if task is not None and category is not None:
            cursor.execute(
                "UPDATE todos SET task = :task, category = :category WHERE position = :position",
                {"task": task, "category": category, "position": position},
            )
        elif task is not None:
            cursor.execute(
                "UPDATE todos SET task = :task WHERE position = :position",
                {"task": task, "position": position},
            )
        elif category is not None:
            cursor.execute(
                "UPDATE todos SET category = :category WHERE position = :position",
                {"category": category, "position": position},
            )


# The complete_todo function takes a position and updates the status of the todo at that position to 2 (completed).
# It also updates the date_completed to the current date and time.
# It uses the with connection: statement to ensure that the changes are committed to the database.
def complete_todo(position: int):
    with connection:
        cursor.execute(
            "UPDATE todos SET status = 2, date_completed = :date_completed WHERE position = :position",
            {"date_completed": datetime.now().isoformat(), "position": position},
        )


def incomplete_todo(position: int):
    """Sets a todo item back to imcomplete status"""
    with connection:
        cursor.execute(
            "UPDATE todos SET status = 1, date_completed = NULL WHERE position = :position",
            {"position": position},
        )
