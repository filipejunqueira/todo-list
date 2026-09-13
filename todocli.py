#!/home/filipejunqueira/miniforge3/envs/defpy/bin/python
# The first line is the shebang! Used to tell the system which interpreter to use to run the script.
# I only use this to create a symlink to the script in my bin folder and be able to call it from anywhere.

import typer
from rich.console import Console
from rich.table import Table
from model import Todo
from database import (
    get_all_todos,
    delete_todo,
    insert_todo,
    complete_todo,
    update_todo,
    incomplete_todo,
    move_todo,
)

"""The way you build this script is a little different. 
Ideally you would know what you want to do, 
then build the model and database first and then only you "go back" and finish building the cli.
"""

console = (
    Console()
)  # This is the rich console object. It is used to print the table and other things in a nice way.
app = (
    typer.Typer()
)  # This is the main app object. It is used to create the cli and add commands to it. (we need to run it later)


# The way these decorators work is by having the function name as the command name.
# So if you want to call the command "add" you just need to create a function called add and decorate it with @app.command()
@app.command(short_help="adds an item to the todo list")
def add(task: str, category: str):
    typer.echo(f"Added task: {task} in category: {category}")
    # Creates the object with a given task and category
    todo = Todo(task, category)
    # And then uses the function we created in the database.py file to insert the todo into the database.
    insert_todo(todo)
    # Shows the database again
    show()


@app.command(short_help="removes an item from the todo list")
def remove(position: int):
    typer.echo(f"Removed task: {position}")
    delete_todo(position - 1)
    show()


@app.command(short_help="updates the position of task")
def update(position: int, task: str = None, category: str = None):
    typer.echo(f"Updated task: {position} to {task} in category: {category}")
    update_todo(position - 1, task, category)
    show()


@app.command(short_help="completes a task")
def complete(position: int):
    typer.echo(f"Completed task: {position}")
    complete_todo(position - 1)
    show()


@app.command(short_help="marks a task as incomplete")
def incomplete(position: int):
    typer.echo(f"Marked task: {position} as incomplete")
    incomplete_todo(position - 1)  # This calls the new database function
    show()


@app.command(short_help="moves an item to a different position")
def move(current_position: int, new_position: int):
    """Moves a task from CURRENT_POSITION to NEW_POSITION."""
    typer.echo(f"Moving task from position {current_position} to {new_position}")
    # Convert 1-based user input to 0-based index for the database function
    move_todo(current_position - 1, new_position - 1)
    show()


@app.command(short_help="shows the table of todos")
def show():
    tasks = get_all_todos()

    console.print("[bold green]Todo List:[/bold green]")
    table = Table(title="", show_lines=False, title_justify="center")
    table.add_column("#", style="dim", width=6, justify="center")
    table.add_column("Todo", justify="right", min_width=20)
    table.add_column("Category", justify="right", min_width=12)
    table.add_column("Done?", justify="right", min_width=12)

    # add all the tasks to the table

    def get_category_color(category):
        colours = {
            "Dota": "red",
            "Work": "blue",
            "Personal": "green",
            "Shopping": "yellow",
            "FJ Educational": "cyan",
        }
        if category in colours:
            return colours[category]
        return "white"

    for i, task in enumerate(tasks, start=1):
        color = get_category_color(task.category)
        # hard coding the done status for now, emoji of a tick if done, emoji of a cross if not done
        is_done_string = "✅" if task.status == 2 else "❌"
        table.add_row(
            str(i), task.task, f"[{color}]{task.category}[/{color}]", is_done_string
        )
    console.print(table)


if __name__ == "__main__":
    app()  # this is running our app.
