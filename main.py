import tkinter as tk
import csv
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from Hashmap_Openaddressing import HashMap
from Stack import Stack
from tkinter.font import Font

SPACE = " "
BLANK = ""
# Creation of all tables for the database

def create_db():
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS supervisors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    firstname TEXT,
                    surname TEXT,
                    password TEXT,
                    username TEXT
                )""")

    c.execute("""CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT,
                    last_name TEXT,
                    age INTEGER,
                    gender TEXT,
                    position TEXT,
                    supervisor_id INTEGER,
                    FOREIGN KEY (supervisor_id) REFERENCES supervisors (id)
                )""")

    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT,
                    due_date TEXT,
                    priority INTEGER,
                    employee_id INTEGER,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )""")
    conn.commit()

    c.execute("""CREATE TABLE IF NOT EXISTS behavior_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        employee_id INTEGER,
                        report_date TEXT,
                        report TEXT,
                        FOREIGN KEY (employee_id) REFERENCES employees (id)
                    )""")
    conn.commit()
    conn.close()


# --------------------------LOGIN SYSTEM SUBROUTINES--------------------------------#

hash_map = HashMap(256)

def hash_password(password):
    global hash_map
    try:
        hash_map.assign(password, password)
        #hash_map.test()
        #print(hash_map.retrieve(password))
        return hash_map.retrieve(password)
    except:
        pass


# User_ID is used to get the ID of the user(manager) -- Important for getting the users employees
user_ID = ""



def loading_screen():

    # create a new window for the loading screen
    loading_screen = tk.Toplevel()

    # set the window title
    loading_screen.title("Loading Screen")
    loading_screen.config(bg='#E6E6E6')

    # --------------------------STYLE----------------------------------------------#
    style = ttk.Style(loading_screen)

    style.theme_use("clam")

    style.configure(".", background="#E6E6E6")
    style.configure("TFrame", background="#E6E6E6")
    style.configure("TLabedl", foreground="#3E3E3E", background="#E6E6E6", )
    style.configure("TButton", foreground="#3E3E3E", background="#D9D9D9", )
    style.configure("TCombobox", foreground="#3E3E3E", background="#E6E6E6", fieldbackground="blue")
    style.configure("TMenubutton", foreground="#3E3E3E", background="#E6E6E6", )
    style.configure("TRadiobutton", foreground="#3E3E3E", background="#E6E6E6", )
    style.configure("TCheckbutton", foreground="#3E3E3E", background="#E6E6E6", )
    style.configure("TScrollbar", background="#3E3E3E", troughcolor="#D9D9D9")
    style.configure("TEntry", foreground="#3E3E3E", background="#E6E6E6", fieldbackground="white")
    style.configure("red.Horizontal.TProgressbar", foreground='DodgerBlue2', background='DodgerBlue2')

    # ---------------------------STYLE---------------------------------------------#

    # set the window size
    loading_screen.geometry("700x350")

    logo_image = tk.PhotoImage(file="Logo.png")

    # create a label with the image for the loading screen
    logo_label = tk.Label(loading_screen, image=logo_image)
    logo_label.pack(pady=5)

    # create a label for the loading screen
    loading_label = ttk.Label(loading_screen, text="Loading...")
    loading_label.pack(pady=10)

    # create a progress bar for the loading screen
    progress_bar = ttk.Progressbar(loading_screen,style="red.Horizontal.TProgressbar", orient="horizontal", length=700, mode="determinate")
    progress_bar.pack(pady=10)

    # simulate a loading process by incrementing the progress bar value
    for i in range(150):
        progress_bar["value"] = i
        loading_screen.update()
        loading_screen.after(10)

    # destroy the loading screen window once the loading process is complete
    loading_screen.destroy()

def login():
    # This is error handling to stop crash from the login() taking the entries as Nonetype
    try:
        username = username_entry.get()
        password = password_entry.get()
    except:
        return True

    # Connect to the database
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()

    # Check if the username exists in the supervisors table
    try:
        c.execute("SELECT * FROM supervisors WHERE username=?", (username,))
        supervisor = c.fetchone()
        global user_ID
        user_ID = supervisor[0]
    except:
        login_status_label.config(text="Invalid login.")


    if supervisor:
        # If the supervisor exists, check the password hash value
        hashed_password = hash_password(password)
        if hashed_password == supervisor[3]:
            # If the password is correct, display a message and close the window
            login_status_label.config(text="Login successful.")
            login_window.after(2500,login_window.destroy)
            loading_screen()
            return True
        else:
            # If the password is incorrect, display an error message
            login_status_label.config(text="Invalid login.")
    else:
        # If the user does not exist, display an error message
        login_status_label.config(text="Invalid login.")

    conn.close()

    return False


def register():
    # Get registration data from the input fields
    firstname = firstname_entry.get()
    surname = surname_entry.get()
    username = reg_username_entry.get()
    password = reg_password_entry.get()

    # Connect to the database
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()

    # Check if the username already exists in the supervisor table
    c.execute("SELECT * FROM supervisors WHERE username=?", (username,))
    supervisor = c.fetchone()

    if len(firstname) ==0 or len(surname) ==0 or len(username) ==0 or len(firstname) ==0 or len(password) == 0:
        reg_status_label.config(text="Cannot have any empty fields")

    elif supervisor:
        # Simple check to see if the username exists
        reg_status_label.config(text="Username already taken.")

    else:
        # sends the details into the table if the username is unique
        hashed_password = hash_password(password)
        c.execute("INSERT INTO supervisors (firstname, surname, password, username) VALUES (?, ?, ?, ?)",
                  (firstname, surname, hashed_password, username))
        conn.commit()

        # display a message and clear the input fields
        reg_status_label.config(text="Registration successful.")
        firstname_entry.delete(0, tk.END)
        surname_entry.delete(0, tk.END)
        reg_username_entry.delete(0, tk.END)
        reg_password_entry.delete(0, tk.END)

    conn.close()

def on_closing():
    login_window.destroy()
    exit()

# Login Window
login_window = tk.Tk()
login_window.protocol("WM_DELETE_WINDOW", on_closing)
login_window.title("Supervisor Login")
login_window.config(bg='#E6E6E6')
login_window.geometry("270x400")
# --------------------------STYLE----------------------------------------------#
style = ttk.Style(login_window)

style.theme_use("clam")

style.configure(".", background="#E6E6E6")
style.configure("TFrame", background="#E6E6E6")
style.configure("TLabedl", foreground="#3E3E3E", background="#E6E6E6", )
style.configure("TButton", foreground="#3E3E3E", background="#D9D9D9", )
style.configure("TCombobox", foreground="#3E3E3E", background="#E6E6E6", fieldbackground="blue")
style.configure("TMenubutton", foreground="#3E3E3E", background="#E6E6E6", )
style.configure("TRadiobutton", foreground="#3E3E3E", background="#E6E6E6", )
style.configure("TCheckbutton", foreground="#3E3E3E", background="#E6E6E6", )
style.configure("TScrollbar", background="#3E3E3E", troughcolor="#D9D9D9")
style.configure("TEntry", foreground="#3E3E3E", background="#E6E6E6", fieldbackground="white")
style.configure("red.Horizontal.TProgressbar", foreground='DodgerBlue2', background='DodgerBlue2')

# ---------------------------STYLE---------------------------------------------#
# Input Fields (login)
username_label = ttk.Label(login_window, text="Username:")
username_label.pack()
username_entry = ttk.Entry(login_window)
username_entry.pack()

password_label = ttk.Label(login_window, text="Password:")
password_label.pack()
password_entry = ttk.Entry(login_window, show="*")
password_entry.pack()

login_button = ttk.Button(login_window, text="Login", command=login)
login_button.pack()

# text for login success or failure
login_status_label = ttk.Label(login_window, text="")
login_status_label.pack()

# Line that separates register and login
separator = ttk.Separator(login_window, orient='horizontal')
separator.pack(fill='x', padx=10, pady=10)

# input fields for registration
reg_label = ttk.Label(login_window, text="Register a new supervisor:")
reg_label.pack()

firstname_label = ttk.Label(login_window, text="First name:")
firstname_label.pack()
firstname_entry = ttk.Entry(login_window)
firstname_entry.pack()

surname_label = ttk.Label(login_window, text="Surname:")
surname_label.pack()
surname_entry = ttk.Entry(login_window)
surname_entry.pack()

reg_username_label = ttk.Label(login_window, text="Username:")
reg_username_label.pack()
reg_username_entry = ttk.Entry(login_window)
reg_username_entry.pack()

reg_password_label = ttk.Label(login_window, text="Password:")
reg_password_label.pack()
reg_password_entry = ttk.Entry(login_window, show="*")
reg_password_entry.pack()

register_button = ttk.Button(login_window, text="Register", command=register)
register_button.pack()

reg_status_label = ttk.Label(login_window, text="")
reg_status_label.pack()

valid_login = False
while not valid_login:
    login_window.mainloop()
    valid_login = login()



# --------------------------MAIN PROGRAM SUBROUTINES--------------------------------#
employee_stack = Stack()

def add_employee():
    age = age_entry.get()
    try:
        x = int(age)
    except ValueError:
        messagebox.showinfo("Invalid Input",
                            f"Age is not a valid input")
        return

    if len(first_name_entry.get()) ==0 or len(last_name_entry.get()) ==0 or len(age_entry.get()) == BLANK or len(age_entry.get()) == SPACE:
        messagebox.showinfo("Invalid Input",
                            f"The Employee information inputted was incorrect")
    else:
        global user_ID
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute("INSERT INTO employees VALUES (:id, :first_name, :last_name, :age, :gender, :position, :supervisor_id)",
                  {
                      'id': None,
                      'first_name': first_name_entry.get(),
                      'last_name': last_name_entry.get(),
                      'age': age_entry.get(),
                      'gender': gender.get(),
                      'position': position_combo.get(),
                      'supervisor_id': user_ID
                  })

        conn.commit()
        conn.close()
        view_employee()


# This is a merge sort subroutine used in the display of employees (this makes sure that they are sorted by ID in ascending order)

def merge_sort_by_age(array):
    if len(array) > 1:
        mid = len(array) // 2
        left_half = array[:mid]
        right_half = array[mid:]

        merge_sort_by_age(left_half)
        merge_sort_by_age(right_half)

        i = j = k = 0

        while i < len(left_half) and j < len(right_half):
            if left_half[i][3] < right_half[j][3]:
                array[k] = left_half[i]
                i += 1
            else:
                array[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            array[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            array[k] = right_half[j]
            j += 1
            k += 1

def view_employee():
    global user_ID
    try:
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM employees WHERE supervisor_id = '{user_ID}'")

        employeedata = c.fetchall()

        # Sort the employee data by age using merge sort
        merge_sort_by_age(employeedata)

        # Clear the treeview before inserting new data
        employeetree.delete(*employeetree.get_children())

        # Insert data into the Treeview
        for employee in employeedata:
            employeetree.insert('', 'end', text=employee[0], values=(employee[1], employee[2], employee[3], employee[4], employee[5]))

        # Bind a function to the TreeviewSelect event to set the employee_var variable
        def set_employee_var(event):

            selected_item = employeetree.selection()[0]
            employee_id = employeetree.item(selected_item, "text")
            employee_var.set(employee_id)

            # Push the selected employee onto the stack
            employee_stack.push(employee_id)

        employeetree.bind("<<TreeviewSelect>>", set_employee_var)
    except:
        # Handle any exceptions that might occur
        print("An error occurred while viewing the employee.")


def add_position_to_dropdown():
    new_position = add_position_entry.get()
    if len(new_position) == 0 or new_position[0] == SPACE or new_position[len(new_position) - 1] == SPACE:
        messagebox.showinfo("Invalid Input",
                            f"The new position provided is not valid due to being blank, or having a leading or trailing space")
    else:
        position_options.append(new_position)
        position_combo['values'] = position_options

def add_task():
    if len(task_entry.get())== 0 or len(due_date_entry.get()) == 0 or priority_var.get() == 0 or len(employee_var.get()) == 0:

        messagebox.showinfo("Ivalid Input",
                            f"One of the task inputs were blank.")
    else:
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute("INSERT INTO tasks VALUES (:id, :task, :due_date, :priority, :employee_id)",
                  {
                      'id': None,
                      'task': task_entry.get(),
                      'due_date': due_date_entry.get(),
                      'priority': priority_var.get(),
                      'employee_id': employee_var.get(),
                  })
        conn.commit()
        conn.close()
        get_employee_tasks()


def delete_employee():
    try:
        # Pop the previous employee off the stack
        employee_stack.pop()
        selected_employee = employee_stack.pop()

        if selected_employee is None:
            selected_employee = employeetree.item(employeetree.get_children()[0], "text")

        employee_var.set(selected_employee)

        # delete the selected employee from the database
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute(f"DELETE FROM employees WHERE id = '{selected_employee}'")
        conn.commit()

        # removes all tasks and reports linked to an employee
        c.execute(f"DELETE FROM tasks WHERE employee_id = '{selected_employee}'")
        c.execute(f"DELETE FROM behavior_reports WHERE employee_id = '{selected_employee}'")
        conn.commit()
        conn.close()

        # Refreshes the treeview
        view_employee()
    except:
        messagebox.showinfo("Deletion Error",
                            f"No Employee was selected to be deleted")


# -------------------------Report Subroutines----------------------------#

# export reports to a CSV file
def export_reports():
    # get the selected employee from the employee_var variable
    selected_employee = employee_var.get()

    # queries the database to get all reports for the selected employee
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM behavior_reports WHERE employee_id = '{selected_employee}'")
    reports = c.fetchall()

    # exports the reports of a given employee as a CSV -- writing to the file
    with open(f"{selected_employee}_reports.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Report ID", "Report Date", "Report Details"])
        for report in reports:
            writer.writerow([report[0], report[2], report[3]])

    # message to tell the user that export was successful
    messagebox.showinfo("Export Complete",
                        f"The reports for employee ID {selected_employee} have been exported as a CSV file.")

    conn.close()



def get_employee_reports():
    # get the selected employee from the employee_var variable
    selected_employee = employee_var.get()

    # queries the database for an employee's linked reports
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM behavior_reports WHERE employee_id = '{selected_employee}'")
    reports = c.fetchall()

    # Report window
    report_window = tk.Toplevel(root)
    report_window.title("Reports for Employee ID: " + selected_employee)

    report_table = ttk.Treeview(report_window)
    report_table.pack()

    # columns for the table created
    report_table["columns"] = ("Report ID", "Report Date", "Report Details", "Delete")
    report_table.column("#0", width=0, stretch=tk.NO)
    report_table.column("Report ID", anchor=tk.CENTER, width=100)
    report_table.column("Report Date", anchor=tk.CENTER, width=200)
    report_table.column("Report Details", anchor=tk.CENTER, width=200)
    report_table.column("Delete", anchor=tk.CENTER, width=100)

    def delete_report():
        # taking users selection
        selected_item = report_table.selection()[0]
        report_id = report_table.item(selected_item, "values")[0]

        # SQL delete from the database
        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute(f"DELETE FROM behavior_reports WHERE id = '{report_id}'")
        conn.commit()
        conn.close()

        report_window.destroy()
        # calls itself to update display
        get_employee_reports()

    report_table.heading("#0", text="", anchor=tk.CENTER)
    report_table.heading("Report ID", text="Report ID", anchor=tk.CENTER)
    report_table.heading("Report Date", text="Report Date", anchor=tk.CENTER)
    report_table.heading("Report Details", text="Report Details", anchor=tk.CENTER)
    report_table.heading("Delete", text="Delete", anchor=tk.CENTER)

    for report in reports:
        report_table.insert("", 'end', values=(report[0], report[2], report[3], "Delete"))

    report_table.bind("<Button-1>", lambda event: delete_report() if report_table.identify_region(event.x,
                                                                                                  event.y) == "cell" else None)
    export_button = ttk.Button(report_window, text="Export as CSV", command=export_reports)
    export_button.pack()


def add_report():
    selected_employee = employee_var.get()

    if len(selected_employee) == 0:
        messagebox.showinfo("Selection Error",
                            f"No Employee was selected to add reports.")
    else:
        report_window = tk.Toplevel(root)
        report_window.title("Add Report for " + selected_employee)

        report_label = ttk.Label(report_window, text="Report:")
        report_label.pack(pady=10)

        report_entry = ttk.Entry(report_window, width=30)
        report_entry.pack()

        report_date_label = ttk.Label(report_window, text="Report Date:")
        report_date_label.pack(pady=10)

        report_date_entry = ttk.Entry(report_window, width=30)
        report_date_entry.pack()

        def save_report():
            if len(report_date_entry.get()) == 0 or report_date_entry.get()[0] == SPACE or [len(report_date_entry.get()) - 1] == SPACE or len(report_entry.get()) == 0 or report_entry.get()[0] == SPACE or [len(report_entry.get()) - 1] == SPACE:
                messagebox.showinfo("Invalid Input",
                                    f"The report provided is not valid due to one of the fields being blank, or having a leading or trailing space")
            else:
                conn = sqlite3.connect('employees.db')
                c = conn.cursor()
                c.execute("INSERT INTO behavior_reports VALUES (:id, :employee_id, :report_date, :report)",
                          {
                              'id': None,
                              'employee_id': selected_employee,
                              'report_date': report_date_entry.get(),
                              'report': report_entry.get(),
                          })
                conn.commit()
                conn.close()
                report_window.destroy()

        save_button = ttk.Button(report_window, text="Save", command=save_report)
        save_button.pack(pady=20)


# --------------------------------TASK Subroutines---------------------------------#

def get_employee_tasks():
    # get the selected employee from the employee_var variable
    selected_employee = employee_var.get()

    # queries the database to get all tasks for the employee selected on the treeview
    conn = sqlite3.connect('employees.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM tasks WHERE employee_id = '{selected_employee}'")
    tasks = c.fetchall()

    # Task window
    task_window = tk.Toplevel(root)
    task_window.title("Tasks for Employee ID: " + selected_employee)

    # Creates a table similar to the reports
    table = ttk.Treeview(task_window)
    table.pack()

    # table columns created
    table["columns"] = ("Task ID", "Task", "Due Date", "Priority", "Delete")
    table.column("#0", width=0, stretch=tk.NO)
    table.column("Task ID", anchor=tk.CENTER, width=100)
    table.column("Task", anchor=tk.CENTER, width=300)
    table.column("Due Date", anchor=tk.CENTER, width=100)
    table.column("Priority", anchor=tk.CENTER, width=200)
    table.column("Delete", anchor=tk.CENTER, width=100)

    def delete_task():
        # Similar embedded subroutine as used on reports
        selected_item = table.selection()[0]
        task_id = table.item(selected_item, "values")[0]

        conn = sqlite3.connect('employees.db')
        c = conn.cursor()
        c.execute(f"DELETE FROM tasks WHERE id = '{task_id}'")
        conn.commit()
        conn.close()

        # Refreshes table
        task_window.destroy()
        get_employee_tasks()

    # headings for table
    table.heading("#0", text="", anchor=tk.CENTER)
    table.heading("Task ID", text="Task ID", anchor=tk.CENTER)
    table.heading("Due Date", text="Due Date", anchor=tk.CENTER)
    table.heading("Task", text="Task Name", anchor=tk.CENTER)
    table.heading("Priority", text="Priority", anchor=tk.CENTER)
    table.heading("Delete", text="Delete", anchor=tk.CENTER)

    # Get tasks for the selected employee from the main treeview
    c.execute(f"SELECT * FROM tasks WHERE employee_id = '{selected_employee}'")
    tasks = c.fetchall()

    # adds tasks
    for task in tasks:
        table.insert("", 'end', values=(task[0], task[1], task[2], task[3], "Delete"))

    table.bind("<Button-1>", lambda event: delete_task() if table.identify_region(event.x, event.y) == "cell" else None)


# --------------------------Front End GUI stuff (Employee_Var is defined her)---------------------------#


root = tk.Tk()
root.title("CURO")
root.config(bg='#E6E6E6')
root.geometry("1250x900")
create_db()

# --------------------------STYLE----------------------------------------------#
style = ttk.Style(root)

style.theme_use("clam")

style.configure(".", background="#E6E6E6")
style.configure("TFrame", background="#E6E6E6")
style.configure("TLabel", foreground="#3E3E3E", background="#E6E6E6", )
style.configure("TButton", foreground="#3E3E3E", background="#D9D9D9", )
style.configure("TCombobox", foreground="#3E3E3E", background="#E6E6E6", fieldbackground="blue")
style.configure("TMenubutton", foreground="#3E3E3E", background="#E6E6E6", )
style.configure("TRadiobutton", foreground="#3E3E3E", background="#E6E6E6", )
style.configure("TCheckbutton", foreground="#3E3E3E", background="#E6E6E6", )
style.configure("TScrollbar", background="#3E3E3E", troughcolor="#D9D9D9")
style.configure("TEntry", foreground="#3E3E3E", background="#E6E6E6", fieldbackground="white")
style.configure("red.Horizontal.TProgressbar", foreground='blue', background='blue')

# ---------------------------STYLE---------------------------------------------#
# the three frames created for the gui
main_frame = ttk.Frame(root)
main_frame.pack(pady=40)

left_frame = ttk.Frame(main_frame)
mid_frame = ttk.Frame(main_frame)
right_frame = ttk.Frame(main_frame)

left_frame.pack(side="left", padx=60)
mid_frame.pack(side="left", padx=60)
right_frame.pack(side="left", padx=60)

# beneath is all buttons and entries
conn = sqlite3.connect('employees.db')
c = conn.cursor()
c.execute(f"SELECT firstname FROM supervisors WHERE id = '{user_ID}'")
name = c.fetchall()[0][0]
conn.commit()
conn.close()
title_style = Font(family="Verdana", size=15, weight="normal")
title_label = ttk.Label(mid_frame, text="Welcome, {}!".format(name), font=title_style)
title_label.pack(pady=5)

main_menu_logo = tk.PhotoImage(file="Logo2.png")

logo_label = tk.Label(mid_frame, image=main_menu_logo)
logo_label.pack(pady=5)

first_name_label = ttk.Label(left_frame, text="First Name:")
first_name_label.pack()
first_name_entry = ttk.Entry(left_frame)
first_name_entry.pack()

last_name_label = ttk.Label(left_frame, text="Last Name:")
last_name_label.pack()
last_name_entry = ttk.Entry(left_frame)
last_name_entry.pack()

age_label = ttk.Label(left_frame, text="Age:")
age_label.pack()
age_entry = ttk.Entry(left_frame)
age_entry.pack()

gender = tk.StringVar()
gender_label = ttk.Label(left_frame, text="Gender:")
gender_label.pack()
gender_male = ttk.Radiobutton(left_frame, text="Male", variable=gender, value="Male")
gender_male.pack()
gender_female = ttk.Radiobutton(left_frame, text="Female", variable=gender, value="Female")
gender_female.pack()
gender_other = ttk.Radiobutton(left_frame, text="Other", variable=gender, value="Other")
gender_other.pack()

position_options = ["Manager", "Marketing Director", "Assistant Manager", "Employee"]
position_var = tk.StringVar()
position_label = ttk.Label(left_frame, text="Position:")
position_label.pack()
position_combo = ttk.Combobox(left_frame, values=position_options)
position_combo['state'] = 'readonly'
position_combo.pack()

add_position_label = ttk.Label(mid_frame, text="Add A New Position")
add_position_label.pack()
add_position_entry = ttk.Entry(mid_frame)
add_position_entry.pack()
add_position_button = ttk.Button(mid_frame, text="Add Position",
                                 command=add_position_to_dropdown)
add_position_button.pack()

add_employee_button = ttk.Button(left_frame, text="Add Employee", command=add_employee)
add_employee_button.pack()

employee_var = tk.StringVar()
employee_label = ttk.Label(text="Selected employee ID:")
employee_label.pack()
employee_combo = ttk.Entry(textvariable=employee_var, state='disabled')
employee_combo.pack()

display_label_EMP = ttk.Label(left_frame, text="Employee Information:")
display_label_EMP.pack()
display_label_2EMP = ttk.Label(left_frame, text="")
display_label_2EMP.pack()

view_employee_button = ttk.Button(text="View Employees", command=view_employee)
view_employee_button.pack()

task_label = ttk.Label(right_frame, text="Task:")
task_label.pack()
task_entry = ttk.Entry(right_frame)
task_entry.pack()

due_date_label = ttk.Label(right_frame, text="Due Date:")
due_date_label.pack()
due_date_entry = ttk.Entry(right_frame)
due_date_entry.pack()

priority_var = tk.IntVar()
priority_label_main = ttk.Label(right_frame, text="Priority:")
priority_label_main.pack()
priority_scale = ttk.Scale(right_frame, from_=1, to=3, orient="horizontal", variable=priority_var,
                           command=lambda x: priority_label_mini.config(text="Value: " + str(priority_var.get())))
priority_scale.pack()
priority_label_mini = ttk.Label(right_frame, text="Value: " + str(priority_var.get()))
priority_label_mini.pack()

add_task_button = ttk.Button(right_frame, text="Add Task", command=add_task)
add_task_button.pack()

display_label_Task = ttk.Label(right_frame, text="Tasks:")
display_label_Task.pack()

display_label_Taskspace = ttk.Label(right_frame, text="")
display_label_Taskspace.pack()

# creation of the main treeview that displays all employees linked to the user

employeetree = ttk.Treeview(columns=('firstname', 'secondname', 'age', 'gender', 'position'))
employeetree.heading('#0', text='ID')
employeetree.heading('firstname', text='First Name')
employeetree.heading('secondname', text='Second Name')
employeetree.heading('age', text='Age')
employeetree.heading('gender', text='Gender')
employeetree.heading('position', text='Position')
employeetree.pack(padx=10, pady=10)

button_tasks = ttk.Button(right_frame, text="Get Employee's Tasks", command=get_employee_tasks)
button_tasks.pack(padx=5)

delete_employee_button = ttk.Button(text="Delete Employee", command=delete_employee)
delete_employee_button.pack()

view_report_button = ttk.Button(mid_frame, text="View Reports", command=get_employee_reports)
view_report_button.pack()

add_report_button = ttk.Button(mid_frame, text="Add Report", command=add_report)
add_report_button.pack()

root.mainloop()


