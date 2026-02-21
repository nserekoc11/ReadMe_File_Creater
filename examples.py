
"""
#even numbers 

list1 = [ 1, 2, 3, 4, 5, 6]
list2 = [ ]
def even_nums():
    for i in list1:
        if i % 2 == 0 :
            list2.append(i)
    print(list2)
even_nums()

# cheak if name if 5 chars long
user_name = input("Name: ")
char_count = len (user_name)
def verifyer ():
    if char_count >= 5:
        print("Valid")
    else : 
        print("too short")
verifyer()

#function for returning a number of words in a list 
word = ("i love jun good programing")
sp = word.split()
def num ():
    print(len(sp))
num()
"""


"""
To Do List app cli
>Show menu
>Add task
>View tasks
>Delete tasks
>Saves tasks to file
>Load tasks when program starts
"""
#TODO:Add tasks
#TODO:Delete tasks
#TODO:Saves tasks
#TODO:Loads tasks

tasks = []
def show_menu():
    print("\n1. View Tasks")
    print("2. Add task")
    print("3. Delete task")
    print("4. Exit")

def main():
    while True:
        show_menu()
        choice = input("Choose an option: ")
        if choice == "1":
            if not tasks:
                print("No tasks yet.")
            else:
                for index, task in enumerate(tasks, start=1):
                    print(f"{index}. {task}")

        elif choice == "2":
            add_task()
            save_tasks()
            print("Task added succefuly")

        elif choice == "3":
            delete_task()
            save_tasks()
        elif choice == "4":
            break
        else:
            print("Invalid choice")
def add_task():
    task = input("Enter task: ")
    tasks.append(task)


def delete_task():
    if not tasks:
        print("No tasks to delete.")
        return
    for index, task in enumerate(tasks, start=1):
        print(f"{index}. {task}")
    try:
        num = int(input("Enter task number to delete: "))
        removed = tasks.pop(num - 1)
        print(f'"{removed}" has been deleted.')
    except (ValueError, IndexError):
        print("Invalid selection")

def save_tasks():
    with open("tasks.txt", "w") as file:
        for task in tasks:
            file.write(task + "\n")

def load_tasks():
    try:
        with open("tasks.txt", "r") as file:
            for line in file:
                tasks.append(line.strip())
    except FileNotFoundError:
        pass

load_tasks()
main()
