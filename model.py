import datetime

# This class represents a Todo item.
# The main idea here is that this is a data model for a todo item. If you want to add more fields to the todo item, you can do it here.
# The constructor takes the task, category, date_added, date_completed, status and position as arguments.
# Position is important because it is used to order the todos in the database.
# The date_added and date_completed are optional and default to None.
# The status is also optional and defaults to 1 (not done).

class Todo:
    def __init__(self, task, category, date_added=None, date_completed=None,status=None,position=None):
        self.task = task
        self.category = category
        self.date_added = date_added if date_added is not None else datetime.datetime.now().isoformat()
        self.date_completed = date_completed if date_completed is not None else None
        self.status = status if status is not None else 1 # 1 for not done, 2 for done
        self.position = position if position is not None else None

    def __repr__(self):
        return f"({self.task}, {self.category}, {self.date_added}, {self.date_completed}, {self.status}, {self.position})"
