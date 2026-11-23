import tkinter as tk                                  # main GUI library
from tkinter import ttk, messagebox, simpledialog     # ttk = nicer widgets (table), messagebox = pop-up messages, simpledialog = small input box
import os                                             # used to check if a file exists

# STUDENT MANAGER - MAIN SETTINGS
# Create the main window of the program
root = tk.Tk()
root.title("Student Manager | Management System")
root.geometry("1100x720")                  # starting size: width x height
root.minsize(950, 650)                     # the window cannot be made smaller than this
root.configure(bg="#F0F4FA")

# Name of the text file where student records are stored
FILE_NAME = "studentMarks.txt"

# This list keeps all students in memory while the program runs.
# Each student is a dictionary like: {"code": "S1", "name": "Ali", "marks": [50, 60, 70, 80]}
students = []

# COLOURS
# Colours are saved in variables so we can reuse them and change them easily
BG = "#F0F4FA"
NAVY = "#172554"
BLUE = "#2563EB"
PURPLE = "#7C3AED"
WHITE = "#FFFFFF"
DARK = "#1E293B"
GREEN = "#16A34A"
RED = "#DC2626"
ORANGE = "#EA580C"
GREY = "#64748B"

# FILE HANDLING
def load_students():
    # Read the student records from the text file into the students list
    global students                        # "global" lets us change the list defined outside the function
    students = []                          # start with an empty list each time

    # If the file is not there, show an error and stop
    if not os.path.exists(FILE_NAME):
        messagebox.showerror(
            "File Missing",
            "studentMarks.txt was not found!\n"
            "Please place it in the same folder as this Python file."
        )
        return

    try:
        # Open the file and read all lines into a list
        with open(FILE_NAME, "r") as file:
            lines = file.readlines()

        # The first line is the number of students, so we skip it (lines[1:])
        for line in lines[1:]:
            line = line.strip()            # remove extra spaces and the new line

            # Skip empty lines
            if not line:
                continue

            # Split at the LAST space: left side = code and name, right side = marks
            parts = line.rsplit(" ", 1)

            # If the line does not have exactly 2 parts, it is not valid, so skip it
            if len(parts) != 2:
                continue

            # Split the left side at the FIRST space: code and name
            details = parts[0].split(maxsplit=1)

            if len(details) != 2:
                continue

            code = details[0]
            name = details[1]

            # Turn the marks text "50,60,70,80" into a list of numbers
            marks = [int(x) for x in parts[1].split(",")]

            # Only keep the student if there are exactly 4 marks
            if len(marks) == 4:
                students.append({
                    "code": code,
                    "name": name,
                    "marks": marks
                })

    # ValueError = marks are not numbers, OSError = file cannot be read
    except (ValueError, OSError):
        messagebox.showerror(
            "File Error",
            "Could not read studentMarks.txt.\n"
            "Check the student record format."
        )


def save_students():
    # Write all students back to the text file. Returns True if it worked.
    try:
        # "w" means write: this replaces the old file content
        with open(FILE_NAME, "w") as file:
            # First line is the total number of students
            file.write(str(len(students)) + "\n")

            # Write one line for each student
            for student in students:
                # Join the marks with commas, e.g. [50, 60] becomes "50,60"
                marks = ",".join(map(str, student["marks"]))

                file.write(
                    f'{student["code"]} '
                    f'{student["name"]} {marks}\n'
                )

        return True

    except OSError:
        # Something went wrong while saving (for example, the file is locked)
        messagebox.showerror("Error", "Could not save student records.")
        return False

# STUDENT TABLE
def refresh_table(data=None):
    # Clear the table and fill it again.
    # If data is given, show only that data. Otherwise show all students.

    # Delete every row that is currently in the table
    for item in tree.get_children():
        tree.delete(item)

    # Choose which students to show
    records = students if data is None else data

    for student in records:
        # Add up the 4 marks to get the total
        total = sum(student["marks"])

        # Add one new row at the end of the table
        tree.insert(
            "",
            "end",
            values=(
                student["code"],
                student["name"],
                *student["marks"],         # the * spreads the 4 marks into separate columns
                total
            )
        )

    # Update the blue counter at the top (always shows all students)
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

    refresh_table(results)
    status_label.config(text=f"Found {len(results)} matching record(s)")

# MENU 3 - HIGHEST TOTAL
def highest_total():
    # Find the student with the biggest total marks
    if not students:
        messagebox.showwarning("No Records", "No students available.")
        return

    # max() looks at the total of each student and picks the largest
    highest = max(students, key=lambda s: sum(s["marks"]))

    # Show only that student in the table
    refresh_table([highest])

    messagebox.showinfo(
        "Highest Student",
        f'Name: {highest["name"]}\n'
        f'Code: {highest["code"]}\n'
        f'Total Marks: {sum(highest["marks"])}'
    )

# MENU 4 - LOWEST TOTAL
def lowest_total():
    # Find the student with the smallest total marks
    if not students:
        messagebox.showwarning("No Records", "No students available.")
        return

    # min() picks the student with the smallest total
    lowest = min(students, key=lambda s: sum(s["marks"]))

    refresh_table([lowest])

    messagebox.showinfo(
        "Lowest Student",
        f'Name: {lowest["name"]}\n'
        f'Code: {lowest["code"]}\n'
        f'Total Marks: {sum(lowest["marks"])}'
    )

# MENU 5 - SORT STUDENT RECORDS
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
    sort_window.resizable(False, False)

    tk.Label(
        sort_window,
        text="SORT STUDENT RECORDS",
        font=("Arial", 17, "bold"),
        bg=BG,
        fg=NAVY
    ).pack(pady=25)

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
        command=lambda: apply_sort(False)
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
    # One form used for both adding and updating a student.
    # existing = the student to edit (None when adding a new one)
    # callback = the function to run when the user clicks Save

    # Create a new window for the form
    window = tk.Toplevel(root)
    window.title(title)
    window.geometry("440x520")
    window.configure(bg=WHITE)
    window.resizable(False, False)

    # Title bar at the top of the form
    tk.Label(
        window,
        text=title.upper(),
        font=("Arial", 19, "bold"),
        bg=NAVY,
        fg=WHITE,
        pady=18
    ).pack(fill="x")

    # Frame that holds all the input boxes
    form = tk.Frame(window, bg=WHITE, padx=35, pady=20)
    form.pack(fill="both", expand=True)

    # This dictionary will store each input box so we can read it later
    entries = {}

    # The input boxes to create: (text shown to the user, key name)
    fields = [
        ("Student Code", "code"),
        ("Student Name", "name"),
        ("Mark 1", "mark1"),
        ("Mark 2", "mark2"),
        ("Mark 3", "mark3"),
        ("Mark 4", "mark4")
    ]

    # Old values to fill in the boxes (stays empty when adding a new student)
    values = {}

    if existing:
        values = {
            "code": existing["code"],
            "name": existing["name"],
            "mark1": existing["marks"][0],
            "mark2": existing["marks"][1],
            "mark3": existing["marks"][2],
            "mark4": existing["marks"][3]
        }

    # Create a label and an input box for every field
    for label_text, key in fields:
        tk.Label(
            form,
            text=label_text,
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(anchor="w", pady=(7, 2))

        entry = tk.Entry(
            form,
            font=("Arial", 11),
            relief="solid",
            bd=1
        )
        entry.pack(fill="x", ipady=6)

        # When updating, put the old value inside the box
        if key in values:
            entry.insert(0, str(values[key]))

        # Save the box in the dictionary using its key name
        entries[key] = entry

    def submit():
        # Runs when the user clicks "SAVE STUDENT RECORD"

        # Read the text from the boxes and remove extra spaces
        code = entries["code"].get().strip()
        name = entries["name"].get().strip()

        # Code and name are required
        if not code or not name:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the student code and name.",
                parent=window
            )
            return

        try:
            # Read the 4 marks and turn them into whole numbers
            marks = [
                int(entries[f"mark{i}"].get())
                for i in range(1, 5)
            ]

            # Marks must be between 0 and 100, otherwise raise an error on purpose
            if any(mark < 0 or mark > 100 for mark in marks):
                raise ValueError

        except ValueError:
            # Either a mark was not a number or it was out of range
            messagebox.showerror(
                "Invalid Marks",
                "Enter whole numbers between 0 and 100.",
                parent=window
            )
            return

        # Put everything together as one student record
        new_student = {
            "code": code,
            "name": name,
            "marks": marks
        }

        # Give the new student to the callback (add or update function).
        # If it says True (it worked), close the form.
        if callback:
            if callback(new_student):
                window.destroy()

    # Save button at the bottom of the form
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

    if not search:
        return

    search = search.strip().lower()

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
        old_data["marks"] = old_student["marks"][:]     # [:] makes a separate copy of the list

        # Replace the old details with the new ones
        old_student.update(new_student)

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
        cursor="hand2",
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
    "Mark 1",
    "Mark 2",
    "Mark 3",
    "Mark 4",
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
    command=tree.yview
)

# Connect the table and the scroll bar so they move together
tree.configure(yscrollcommand=scrollbar.set)

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
load_students()
refresh_table()

root.mainloop()