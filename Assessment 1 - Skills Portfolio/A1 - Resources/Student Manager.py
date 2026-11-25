import tkinter as tk                                  # main GUI library
from tkinter import ttk, messagebox, simpledialog     # ttk = styled widgets (table), messagebox = popups, simpledialog = input popups
import csv                                            # used to read and write CSV files
import os                                             # used to check if a file exists

# STUDENT MANAGER - MAIN SETTINGS
# Create the main window of the program
root = tk.Tk()
root.title("Student Management System")
root.geometry("1100x720")                  # starting size: width x height
root.minsize(950, 650)                     # the window cannot be made smaller than this
root.configure(bg="#F0F4FA")               # light blue-grey background colour

# WINDOW ICON 
# Build the full path to the icon file (it must be in the same folder as this program)
ICON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo 3.ico")

# Only set the icon if the file really exists, otherwise warn the user
if os.path.exists(ICON_FILE):
    root.iconbitmap(ICON_FILE)
else:
    messagebox.showwarning("Icon Not Found", "Logo 3.ico was not found in the program folder.")

# COLOURS
# Colours are saved in variables so we can reuse them and change them easily
BG = "#F0F4FA"        # page background
NAVY = "#172554"      # header, headings and dark buttons
BLUE = "#2563EB"      # main accent colour
PURPLE = "#7C3AED"    # secondary accent colour
WHITE = "#FFFFFF"     # panels and button text
DARK = "#1E293B"      # normal text colour
GREEN = "#16A34A"     # success / save buttons
RED = "#DC2626"       # delete button
ORANGE = "#EA580C"    # lowest total button
GREY = "#64748B"      # small hint text

# FILE LOCATION
# BASE_DIR is the folder where this program is saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Two places where the data file might be stored
RESOURCE_FILE = os.path.join(BASE_DIR, "resources", "studentMarks.txt")   # inside a "resources" folder
SAME_FOLDER_FILE = os.path.join(BASE_DIR, "studentMarks.txt")             # next to the program

# Use the "resources" file if it exists, otherwise use the one in the same folder
FILE_PATH = (
    RESOURCE_FILE
    if os.path.exists(RESOURCE_FILE)
    else SAME_FOLDER_FILE
)

# This list keeps all students in memory while the program runs.
# Each student is a dictionary like:
# {"code": "1001", "name": "Ali", "coursework1": 15, "coursework2": 18, "coursework3": 12, "exam": 75}
students = []

# FILE HANDLING
def loadStudents():
    # Read studentMarks.txt, check every row, and fill the students list
    global students                        # we are changing the main list, not making a new local one
    students = []                          # start with an empty list every time

    # Stop early if the data file is missing
    if not os.path.exists(FILE_PATH):
        messagebox.showerror("Error", "studentMarks.txt could not be found.")
        return

    try:
        # Open the file and read all rows as lists of text values
        with open(FILE_PATH, "r", newline="", encoding="utf-8") as file:
            rows = list(csv.reader(file))

        # An empty file is not allowed
        if not rows:
            raise ValueError("The file is empty.")

        # The first row must be a single number: how many student records the file should have
        if not rows[0] or not rows[0][0].strip().isdigit():
            raise ValueError("The first row must contain the number of student records.")
        expected = int(rows[0][0])

        # Go through every row after the first one (n = the real line number in the file)
        for n, row in enumerate(rows[1:], start=2):
            if not row:                    # skip blank lines
                continue
            if len(row) != 6:              # code, name, 3 coursework marks and exam = 6 values
                raise ValueError(f"Row {n} must contain 6 values.")

            # Turn the row into a student dictionary (int() will fail if a mark is not a number)
            s = {
                "code": row[0].strip(),
                "name": row[1].strip(),
                "coursework1": int(row[2]),
                "coursework2": int(row[3]),
                "coursework3": int(row[4]),
                "exam": int(row[5])
            }

            # Validate the data before accepting this student
            if not s["code"].isdigit() or not 1000 <= int(s["code"]) <= 9999:
                raise ValueError(f"Invalid student code on row {n}.")
            if not s["name"]:
                raise ValueError(f"Missing name on row {n}.")
            if any(not 0 <= s[k] <= 20 for k in ("coursework1", "coursework2", "coursework3")):
                raise ValueError(f"Invalid coursework marks on row {n}.")
            if not 0 <= s["exam"] <= 100:
                raise ValueError(f"Invalid exam mark on row {n}.")
            if any(x["code"] == s["code"] for x in students):
                raise ValueError(f"Duplicate student code: {s['code']}.")

            # Everything is valid, so add the student to the list
            students.append(s)

        # Warn if the number at the top of the file does not match the rows loaded
        if expected != len(students):
            messagebox.showwarning("Warning", f"Expected {expected} records, loaded {len(students)}.")

    except (ValueError, IndexError, OSError) as e:
        # Any problem in the file: clear the list and show the error message
        students = []
        messagebox.showerror("File Error", str(e))

def save_students():
    # Save all student records in the same CSV format used by loadStudents().
    try:
        # Make sure the folder exists before writing the file
        folder = os.path.dirname(FILE_PATH)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(FILE_PATH, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([len(students)])       # first row = number of students

            # Write one row for each student
            for student in students:
                writer.writerow([
                    student["code"],
                    student["name"],
                    student["coursework1"],
                    student["coursework2"],
                    student["coursework3"],
                    student["exam"]
                ])

        return True                                # saving worked

    except (OSError, KeyError) as e:
        messagebox.showerror("Error", f"Could not save student records:\n{e}")
        return False                               # saving failed

def refresh_table(data=None):
    # Clear the table before displaying the selected records.
    for item in tree.get_children():
        tree.delete(item)

    # If no list is given, show all students; otherwise show only the given list
    records = students if data is None else data

    for student in records:
        # Total = all three coursework marks + the exam mark
        total = (
            student["coursework1"]
            + student["coursework2"]
            + student["coursework3"]
            + student["exam"]
        )

        # Add one row at the end of the table
        tree.insert(
            "",
            "end",
            values=(
                student["code"],
                student["name"],
                student["coursework1"],
                student["coursework2"],
                student["coursework3"],
                student["exam"],
                total
            )
        )

    # The counter always shows the real number of students, even when the table is filtered
    count_label.config(text=f"TOTAL STUDENTS: {len(students)}")

# MENU 1 - VIEW ALL STUDENTS
def view_all():
    # Show every student in the table
    refresh_table()
    status_label.config(text="Showing all student records")

# MENU 2 - VIEW INDIVIDUAL STUDENT
def view_individual():
    # Ask for a name or code and show only the matching student(s)
    search = simpledialog.askstring(
        "Find Student",
        "Enter student name or student code:"
    )

    # If the user pressed Cancel or typed nothing, do nothing
    if not search:
        return

    # Make the text lowercase so the search ignores capital letters
    search = search.strip().lower()

    # Keep every student whose code or name matches exactly
    results = [
        s for s in students
        if search == s["code"].lower()
        or search == s["name"].lower()
    ]

    # Nothing matched, so tell the user
    if not results:
        messagebox.showwarning(
            "Not Found",
            "Student record not found!"
        )
        return

    # Show only the matching students and update the status bar
    refresh_table(results)
    status_label.config(text=f"Found {len(results)} matching record(s)")

# MENU 3 - HIGHEST TOTAL
def highest_total():
    # Find the student with the biggest total and show only that student
    if not students:
        messagebox.showwarning("No Records", "No students available.")
        return

    def total_marks(student):
        # Helper: add the three coursework marks and the exam mark
        return (
            student["coursework1"]
            + student["coursework2"]
            + student["coursework3"]
            + student["exam"]
        )

    # max() uses total_marks to compare students and returns the best one
    highest = max(students, key=total_marks)
    refresh_table([highest])

    messagebox.showinfo(
        "Highest Student",
        f'Name: {highest["name"]}\n'
        f'Code: {highest["code"]}\n'
        f'Total Marks: {total_marks(highest)}'
    )

# MENU 4 - LOWEST TOTAL
def lowest_total():
    # Find the student with the smallest total and show only that student
    if not students:
        messagebox.showwarning("No Records", "No students available.")
        return

    def total_marks(student):
        # Helper: add the three coursework marks and the exam mark
        return (
            student["coursework1"]
            + student["coursework2"]
            + student["coursework3"]
            + student["exam"]
        )

    # min() works like max(), but returns the student with the lowest total
    lowest = min(students, key=total_marks)
    refresh_table([lowest])

    messagebox.showinfo(
        "Lowest Student",
        f'Name: {lowest["name"]}\n'
        f'Code: {lowest["code"]}\n'
        f'Total Marks: {total_marks(lowest)}'
    )

# MENU 5 - SORT RECORDS
def sort_students():
    # Open a small window where the user chooses A-Z or Z-A
    if not students:
        messagebox.showwarning("No Records", "No students available.")
        return

    # Toplevel = a new window on top of the main window
    sort_window = tk.Toplevel(root)
    sort_window.title("Sort Student Records")
    sort_window.geometry("380x260")
    sort_window.configure(bg=BG)
    sort_window.resizable(False, False)    # the user cannot resize this small window

    # Title of the small window
    tk.Label(
        sort_window,
        text="SORT STUDENT RECORDS",
        font=("Arial", 17, "bold"),
        bg=BG,
        fg=NAVY
    ).pack(pady=25)

    # Instruction text
    tk.Label(
        sort_window,
        text="Choose sorting order:",
        font=("Arial", 12),
        bg=BG,
        fg=DARK
    ).pack(pady=10)

    def apply_sort(reverse):
        # reverse=False means A to Z, reverse=True means Z to A
        sorted_data = sorted(
            students,
            key=lambda s: s["name"].lower(),   # sort by name, ignoring capital letters
            reverse=reverse
        )

        # Show the sorted list (the original list is not changed)
        refresh_table(sorted_data)

        order = "Descending" if reverse else "Ascending"
        status_label.config(text=f"Sorted by name: {order}")

        # Close the small window
        sort_window.destroy()

    # Button for A to Z
    tk.Button(
        sort_window,
        text="↑  Ascending Order (A - Z)",
        bg=BLUE,
        fg=WHITE,
        font=("Arial", 11, "bold"),
        width=27,
        pady=10,
        command=lambda: apply_sort(False)      # lambda lets us pass a value to the function
    ).pack(pady=7)

    # Button for Z to A
    tk.Button(
        sort_window,
        text="Descending Order (Z - A)",
        bg=PURPLE,
        fg=WHITE,
        font=("Arial", 11, "bold"),
        width=27,
        pady=10,
        command=lambda: apply_sort(True)
    ).pack(pady=7)

# STUDENT FORM - ADD AND UPDATE
def student_form(title, existing=None, callback=None):
    # Shared form for adding and updating student records.
    # title    = text shown at the top of the window
    # existing = old student details (only used when updating)
    # callback = function to run with the new details when Save is clicked
    window = tk.Toplevel(root)
    window.title(title)
    window.geometry("440x560")
    window.configure(bg=WHITE)
    window.resizable(False, False)

    # Dark blue title bar at the top of the form
    tk.Label(
        window,
        text=title.upper(),
        font=("Arial", 19, "bold"),
        bg=NAVY,
        fg=WHITE,
        pady=18
    ).pack(fill="x")

    # White area that holds all the input boxes
    form = tk.Frame(window, bg=WHITE, padx=35, pady=20)
    form.pack(fill="both", expand=True)

    entries = {}                           # stores each input box so we can read it later

    # Each field: (text shown to the user, key used in the student dictionary)
    fields = [
        ("Student Code", "code"),
        ("Student Name", "name"),
        ("Coursework 1 (0-20)", "coursework1"),
        ("Coursework 2 (0-20)", "coursework2"),
        ("Coursework 3 (0-20)", "coursework3"),
        ("Exam (0-100)", "exam")
    ]

    # When adding, there are no old values, so use an empty dictionary
    values = existing if existing else {}

    # Create a label and an input box for every field
    for label_text, key in fields:
        tk.Label(
            form,
            text=label_text,
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(anchor="w", pady=(7, 2))

        entry = tk.Entry(form, font=("Arial", 11), relief="solid", bd=1)
        entry.pack(fill="x", ipady=6)

        # When updating, fill the box with the old value
        if key in values:
            entry.insert(0, str(values[key]))

        entries[key] = entry

    def submit():
        # Runs when the user clicks the Save button: check the input, then pass it to the callback
        code_value = entries["code"].get().strip()
        name = entries["name"].get().strip()

        # Code and name cannot be empty
        if not code_value or not name:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the student code and name.",
                parent=window
            )
            return

        # Code must be a 4-digit number (1000 - 9999)
        if not code_value.isdigit() or not 1000 <= int(code_value) <= 9999:
            messagebox.showerror(
                "Invalid Code",
                "Student code must be a 4-digit number.",
                parent=window
            )
            return

        try:
            # int() raises a ValueError if the text is not a whole number
            coursework1 = int(entries["coursework1"].get())
            coursework2 = int(entries["coursework2"].get())
            coursework3 = int(entries["coursework3"].get())
            exam = int(entries["exam"].get())

            # Check the allowed ranges for every mark
            coursework_marks = [coursework1, coursework2, coursework3]
            if any(mark < 0 or mark > 20 for mark in coursework_marks):
                raise ValueError("Coursework marks must be between 0 and 20.")

            if not 0 <= exam <= 100:
                raise ValueError("Exam mark must be between 0 and 100.")

        except ValueError as e:
            # Show our own message if we raised it, otherwise a general one
            message = str(e) or "Please enter whole numbers only."
            messagebox.showerror("Invalid Marks", message, parent=window)
            return

        # Everything is valid, so build the new student dictionary
        new_student = {
            "code": code_value,
            "name": name,
            "coursework1": coursework1,
            "coursework2": coursework2,
            "coursework3": coursework3,
            "exam": exam
        }

        # Give the student to the callback; close the form only if it returns True
        if callback and callback(new_student):
            window.destroy()

    # Green save button at the bottom of the form
    tk.Button(
        form,
        text="SAVE STUDENT RECORD",
        bg=GREEN,
        fg=WHITE,
        font=("Arial", 11, "bold"),
        pady=11,
        cursor="hand2",
        command=submit
    ).pack(fill="x", pady=22)

# MENU 6 - ADD STUDENT
def add_student():
    def add_record(new_student):
        # Called by the form when the user clicks Save

        # Every student code must be unique
        if any(s["code"] == new_student["code"] for s in students):
            messagebox.showerror(
                "Duplicate Code",
                "This student code already exists!"
            )
            return False

        # Add the new student to the list
        students.append(new_student)

        # Save to the file; if it works, update the screen
        if save_students():
            refresh_table()
            status_label.config(text="New student added successfully!")
            messagebox.showinfo(
                "Success",
                "Student record added and saved!"
            )
            return True

        # Saving failed, so undo the add by removing the last student
        students.pop()
        return False

    # Open the form in "add" mode
    student_form("Add New Student", callback=add_record)

# MENU 7 - DELETE STUDENT
def delete_student():
    # Ask which student to delete, confirm, then remove and save
    search = simpledialog.askstring(
        "Delete Student",
        "Enter student name or student code:"
    )

    # User pressed Cancel or typed nothing
    if not search:
        return

    search = search.strip().lower()

    # Find students whose code or name matches
    matches = [
        s for s in students
        if search == s["code"].lower()
        or search == s["name"].lower()
    ]

    if not matches:
        messagebox.showwarning(
            "Not Found",
            "Student record not found!"
        )
        return

    # Two students can have the same name, so we make sure only one is chosen
    if len(matches) > 1:
        messagebox.showwarning(
            "Multiple Matches",
            "More than one student found. Please use their unique student code."
        )
        return

    student = matches[0]

    # Ask "Are you sure?" before deleting
    confirm = messagebox.askyesno(
        "Confirm Delete",
        f'Are you sure you want to delete:\n\n'
        f'{student["name"]} ({student["code"]})?'
    )

    if confirm:
        # Remove the student from the list
        students.remove(student)

        # Save the new list to the file
        if save_students():
            refresh_table()
            status_label.config(text="Student record deleted!")
            messagebox.showinfo(
                "Deleted",
                "Student record deleted successfully!"
            )
        else:
            # Saving failed, so put the student back
            students.append(student)

# MENU 8 - UPDATE STUDENT
def update_student():
    # Ask which student to change, then open the form with their old details
    search = simpledialog.askstring(
        "Update Student",
        "Enter student name or student code:"
    )

    # User pressed Cancel or typed nothing
    if not search:
        return

    search = search.strip().lower()

    # Find students whose code or name matches
    matches = [
        s for s in students
        if search == s["code"].lower()
        or search == s["name"].lower()
    ]

    if not matches:
        messagebox.showwarning(
            "Not Found",
            "Student record not found!"
        )
        return

    # Only one student can be updated at a time
    if len(matches) > 1:
        messagebox.showwarning(
            "Multiple Matches",
            "Please search using the unique student code."
        )
        return

    # The student we are going to change
    old_student = matches[0]

    def update_record(new_student):
        # Called by the form when the user clicks Save

        # The new code must not belong to a different student
        for student in students:
            if (
                student is not old_student
                and student["code"] == new_student["code"]
            ):
                messagebox.showerror(
                    "Duplicate Code",
                    "This student code belongs to another student."
                )
                return False

        # Make a backup of the old data so we can undo if saving fails
        old_data = old_student.copy()

        # Replace the old details with the new ones
        old_student.update(new_student)

        # Save to the file; if it works, update the screen
        if save_students():
            refresh_table()
            status_label.config(text="Student record updated!")
            messagebox.showinfo(
                "Updated",
                "Student record updated successfully!"
            )
            return True

        # Saving failed, so go back to the old details
        old_student.update(old_data)
        return False

    # Open the form with the old details already filled in
    student_form(
        "Update Student Record",
        existing=old_student,
        callback=update_record
    )

# MAIN HEADER
# Dark blue bar at the top of the window
header = tk.Frame(root, bg=NAVY, height=110)
header.pack(fill="x")
header.pack_propagate(False)               # keep the bar at exactly 110 pixels high

# Big title
tk.Label(
    header,
    text="STUDENT MANAGER",
    font=("Arial", 27, "bold"),
    bg=NAVY,
    fg=WHITE
).pack(pady=(18, 3))

# Small subtitle
tk.Label(
    header,
    text="STUDENT RECORD MANAGEMENT SYSTEM",
    font=("Arial", 10, "bold"),
    bg=NAVY,
    fg="#93C5FD"
).pack()

# DASHBOARD
# Row under the header with the student counter and a small text
dashboard = tk.Frame(root, bg=BG)
dashboard.pack(fill="x", padx=25, pady=15)

# Blue box that shows how many students there are
count_label = tk.Label(
    dashboard,
    text="TOTAL STUDENTS: 0",
    font=("Arial", 13, "bold"),
    bg=BLUE,
    fg=WHITE,
    padx=20,
    pady=12
)
count_label.pack(side="left")

# Small grey text on the right side
tk.Label(
    dashboard,
    text="Manage • View • Sort • Update",
    font=("Arial", 11, "bold"),
    bg=BG,
    fg=GREY
).pack(side="right", pady=12)

# MAIN CONTENT
# Big area that holds the menu (left) and the table (right)
content = tk.Frame(root, bg=BG)
content.pack(fill="both", expand=True, padx=25, pady=5)

# LEFT MENU
# White panel with all the menu buttons
menu = tk.Frame(content, bg=WHITE, width=245)
menu.pack(side="left", fill="y", padx=(0, 18))
menu.pack_propagate(False)                 # keep the panel at exactly 245 pixels wide

# Title of the menu panel
tk.Label(
    menu,
    text="MAIN MENU",
    font=("Arial", 15, "bold"),
    bg=WHITE,
    fg=NAVY
).pack(pady=18)

# MENU BUTTON FUNCTION
def menu_button(text, color, command):
    # Make one menu button so we do not repeat the same code 8 times
    tk.Button(
        menu,
        text=text,
        bg=color,
        fg=WHITE,
        activebackground=NAVY,             # colour while the button is pressed
        activeforeground=WHITE,
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2",                    # mouse turns into a hand when over the button
        anchor="w",                        # put the text on the left side
        padx=15,
        pady=11,
        command=command                    # function to run when clicked
    ).pack(fill="x", padx=13, pady=4)


# Create the 8 menu buttons (text, colour, function to run)
menu_button("01  View All Students", BLUE, view_all)
menu_button("02  Individual Student", PURPLE, view_individual)
menu_button("03  Highest Total", GREEN, highest_total)
menu_button("04  Lowest Total", ORANGE, lowest_total)
menu_button("05  Sort Records", "#0891B2", sort_students)
menu_button("06  Add Student", "#059669", add_student)
menu_button("07  Delete Student", RED, delete_student)
menu_button("08  Update Student", "#6D28D9", update_student)

# Exit button placed at the bottom of the menu
tk.Button(
    menu,
    text="EXIT APPLICATION",
    bg=NAVY,
    fg=WHITE,
    font=("Arial", 10, "bold"),
    relief="flat",
    pady=12,
    cursor="hand2",
    command=root.destroy                   # closes the whole program
).pack(side="bottom", fill="x", padx=13, pady=15)

# RIGHT SIDE - STUDENT TABLE
# White panel that holds the table
table_frame = tk.Frame(content, bg=WHITE)
table_frame.pack(side="right", fill="both", expand=True)

# Title above the table
tk.Label(
    table_frame,
    text="STUDENT RECORDS",
    font=("Arial", 17, "bold"),
    bg=WHITE,
    fg=NAVY
).pack(anchor="w", padx=18, pady=15)

# Names of the table columns
columns = (
    "Code",
    "Name",
    "Coursework 1",
    "Coursework 2",
    "Coursework 3",
    "Exam",
    "Total"
)

# Style the table (colours, row height, fonts)
style = ttk.Style()
style.theme_use("clam")                    # "clam" theme lets us change colours easily

# Style for the table rows
style.configure(
    "Treeview",
    background=WHITE,
    foreground=DARK,
    rowheight=38,
    fieldbackground=WHITE,
    font=("Arial", 10)
)

# Style for the table heading row
style.configure(
    "Treeview.Heading",
    background=NAVY,
    foreground=WHITE,
    font=("Arial", 10, "bold"),
    padding=10
)

# Colours used when a row is clicked (selected)
style.map(
    "Treeview",
    background=[("selected", "#BFDBFE")],
    foreground=[("selected", NAVY)]
)

# Create the table itself (show="headings" hides the extra empty first column)
tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

# Set up each column: heading text, width and text alignment
for col in columns:
    tree.heading(col, text=col.upper())

    if col == "Name":
        tree.column(col, width=150, anchor="w")        # name is aligned left
    else:
        tree.column(col, width=75, anchor="center")    # everything else is centred

# Scroll bar on the right side of the table
scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview                     # scrolling the bar moves the table up and down
)

# Connect the table and the scroll bar so they move together
tree.configure(yscrollcommand=scrollbar.set)

# Place the table and the scroll bar side by side
tree.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=5)
scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=5)

# STATUS BAR
# Light blue bar at the bottom that shows what the program just did
status_label = tk.Label(
    root,
    text="Welcome to Student Manager!",
    font=("Arial", 10, "bold"),
    bg="#DBEAFE",
    fg=NAVY,
    anchor="w",
    padx=20,
    pady=12
)
status_label.pack(fill="x", side="bottom")

# START APPLICATION
# Read the file, fill the table, then keep the window open
loadStudents()                             # load the records from studentMarks.txt
refresh_table()                            # show them in the table

root.mainloop()                            # keep the window open and wait for the user's clicks
