
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
from datetime import date

# ---------------- DATABASE ----------------

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll TEXT UNIQUE,
    name TEXT NOT NULL,
    course TEXT,
    semester TEXT,
    phone TEXT,
    email TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll TEXT,
    attendance_date TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll TEXT,
    subject TEXT,
    marks REAL
)
""")

conn.commit()

# ---------------- MAIN WINDOW ----------------

root = tk.Tk()
root.title("Student Management System")
root.geometry("1100x700")
root.configure(bg="#eef2f7")

selected_roll = None

# ---------------- HEADER ----------------

header = tk.Frame(root, bg="#183153", height=75)
header.pack(fill="x")

tk.Label(
    header,
    text="STUDENT MANAGEMENT SYSTEM",
    font=("Arial", 22, "bold"),
    fg="white",
    bg="#183153"
).pack(pady=20)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=15, pady=15)

student_tab = tk.Frame(notebook, bg="white")
attendance_tab = tk.Frame(notebook, bg="white")
marks_tab = tk.Frame(notebook, bg="white")

notebook.add(student_tab, text="Students")
notebook.add(attendance_tab, text="Attendance")
notebook.add(marks_tab, text="Marks")

# ---------------- STUDENT FORM ----------------

form = tk.LabelFrame(
    student_tab,
    text="Student Details",
    font=("Arial", 12, "bold"),
    bg="white",
    padx=15,
    pady=10
)
form.pack(fill="x", padx=15, pady=10)

fields = ["Roll Number", "Name", "Course",
          "Semester", "Phone", "Email"]

entries = {}

for i, field in enumerate(fields):
    row = i // 3
    col = (i % 3) * 2

    tk.Label(
        form, text=field, bg="white",
        font=("Arial", 10)
    ).grid(row=row, column=col, padx=8, pady=10)

    entry = tk.Entry(form, width=22, font=("Arial", 10))
    entry.grid(row=row, column=col + 1, padx=8, pady=10)

    entries[field] = entry

# ---------------- STUDENT TABLE ----------------

table_frame = tk.Frame(student_tab, bg="white")
table_frame.pack(fill="both", expand=True, padx=15, pady=10)

columns = ("Roll", "Name", "Course", "Semester", "Phone", "Email")

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=12
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

tree.pack(fill="both", expand=True)

# ---------------- FUNCTIONS ----------------

def refresh_students():
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
        SELECT roll, name, course, semester, phone, email
        FROM students ORDER BY id DESC
    """)

    for row in cursor.fetchall():
        tree.insert("", "end", values=row)


def clear_fields():
    global selected_roll
    selected_roll = None

    for entry in entries.values():
        entry.delete(0, tk.END)


def add_student():
    values = [entries[f].get().strip() for f in fields]

    if not values[0] or not values[1]:
        messagebox.showwarning(
            "Warning", "Roll Number and Name are required."
        )
        return

    try:
        cursor.execute("""
            INSERT INTO students
            (roll, name, course, semester, phone, email)
            VALUES (?, ?, ?, ?, ?, ?)
        """, values)

        conn.commit()
        refresh_students()
        clear_fields()

        messagebox.showinfo("Success", "Student added successfully!")

    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Error", "This Roll Number already exists."
        )


def select_student(event):
    global selected_roll

    selected = tree.focus()

    if not selected:
        return

    values = tree.item(selected, "values")

    clear_fields()

    for field, value in zip(fields, values):
        entries[field].insert(0, value)

    selected_roll = values[0]


def update_student():
    global selected_roll

    if not selected_roll:
        messagebox.showwarning("Warning", "Select a student first.")
        return

    values = [entries[f].get().strip() for f in fields]

    if not values[0] or not values[1]:
        messagebox.showwarning("Warning", "Roll and Name are required.")
        return

    try:
        cursor.execute("""
            UPDATE students
            SET roll=?, name=?, course=?, semester=?, phone=?, email=?
            WHERE roll=?
        """, values + [selected_roll])

        conn.commit()
        refresh_students()
        clear_fields()

        messagebox.showinfo("Success", "Student updated successfully!")

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Roll Number already exists.")


def delete_student():
    global selected_roll

    if not selected_roll:
        messagebox.showwarning("Warning", "Select a student first.")
        return

    if messagebox.askyesno("Confirm", "Delete this student?"):
        cursor.execute(
            "DELETE FROM students WHERE roll=?",
            (selected_roll,)
        )
        cursor.execute(
            "DELETE FROM attendance WHERE roll=?",
            (selected_roll,)
        )
        cursor.execute(
            "DELETE FROM marks WHERE roll=?",
            (selected_roll,)
        )

        conn.commit()
        refresh_students()
        clear_fields()


def search_student():
    query = search_entry.get().strip()

    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
        SELECT roll, name, course, semester, phone, email
        FROM students
        WHERE roll LIKE ? OR name LIKE ?
    """, (f"%{query}%", f"%{query}%"))

    for row in cursor.fetchall():
        tree.insert("", "end", values=row)


def export_excel():
    cursor.execute("""
        SELECT roll, name, course, semester, phone, email
        FROM students
    """)

    data = cursor.fetchall()

    if not data:
        messagebox.showwarning("Warning", "No student data to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx")]
    )

    if file_path:
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Success", "Excel file exported!")


# ---------------- BUTTONS ----------------

button_frame = tk.Frame(student_tab, bg="white")
button_frame.pack(pady=10)

tk.Button(
    button_frame, text="Add Student",
    command=add_student, bg="#198754", fg="white",
    width=15
).grid(row=0, column=0, padx=5)

tk.Button(
    button_frame, text="Update",
    command=update_student, bg="#0d6efd", fg="white",
    width=15
).grid(row=0, column=1, padx=5)

tk.Button(
    button_frame, text="Delete",
    command=delete_student, bg="#dc3545", fg="white",
    width=15
).grid(row=0, column=2, padx=5)

tk.Button(
    button_frame, text="Clear",
    command=clear_fields, bg="#6c757d", fg="white",
    width=15
).grid(row=0, column=3, padx=5)

tk.Button(
    button_frame, text="Export Excel",
    command=export_excel, bg="#198754", fg="white",
    width=15
).grid(row=0, column=4, padx=5)

search_frame = tk.Frame(student_tab, bg="white")
search_frame.pack(pady=5)

tk.Label(search_frame, text="Search:", bg="white").pack(side="left")

search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side="left", padx=5)

tk.Button(
    search_frame, text="Search",
    command=search_student
).pack(side="left")

tk.Button(
    search_frame, text="Show All",
    command=refresh_students
).pack(side="left", padx=5)

tree.bind("<<TreeviewSelect>>", select_student)

# ---------------- ATTENDANCE ----------------

tk.Label(
    attendance_tab,
    text="Student Attendance Management",
    font=("Arial", 17, "bold"),
    bg="white"
).pack(pady=20)

att_roll = tk.Entry(attendance_tab, width=30)
att_roll.pack(pady=5)
att_roll.insert(0, "")

att_status = ttk.Combobox(
    attendance_tab,
    values=["Present", "Absent"],
    state="readonly",
    width=27
)
att_status.set("Present")
att_status.pack(pady=5)


def mark_attendance():
    roll = att_roll.get().strip()
    status = att_status.get()

    cursor.execute("SELECT roll FROM students WHERE roll=?", (roll,))

    if not cursor.fetchone():
        messagebox.showerror("Error", "Student not found.")
        return

    today = date.today().isoformat()

    cursor.execute("""
        SELECT id FROM attendance
        WHERE roll=? AND attendance_date=?
    """, (roll, today))

    if cursor.fetchone():
        messagebox.showwarning(
            "Warning", "Attendance already marked today."
        )
        return

    cursor.execute("""
        INSERT INTO attendance (roll, attendance_date, status)
        VALUES (?, ?, ?)
    """, (roll, today, status))

    conn.commit()
    messagebox.showinfo("Success", "Attendance marked!")


tk.Button(
    attendance_tab,
    text="Mark Attendance",
    command=mark_attendance,
    bg="#198754",
    fg="white",
    width=20
).pack(pady=15)


# ---------------- MARKS ----------------

tk.Label(
    marks_tab,
    text="Student Marks Management",
    font=("Arial", 17, "bold"),
    bg="white"
).pack(pady=20)

marks_roll = tk.Entry(marks_tab, width=30)
marks_roll.pack(pady=5)
marks_roll.insert(0, "")

subject_entry = tk.Entry(marks_tab, width=30)
subject_entry.pack(pady=5)
subject_entry.insert(0, "")

marks_entry = tk.Entry(marks_tab, width=30)
marks_entry.pack(pady=5)
marks_entry.insert(0, "")


def add_marks():
    roll = marks_roll.get().strip()
    subject = subject_entry.get().strip()
    marks_text = marks_entry.get().strip()

    if not roll or not subject or not marks_text:
        messagebox.showwarning("Warning", "Fill all fields.")
        return

    try:
        marks = float(marks_text)
        if not 0 <= marks <= 100:
            raise ValueError

        cursor.execute("SELECT roll FROM students WHERE roll=?", (roll,))

        if not cursor.fetchone():
            messagebox.showerror("Error", "Student not found.")
            return

        cursor.execute("""
            INSERT INTO marks (roll, subject, marks)
            VALUES (?, ?, ?)
        """, (roll, subject, marks))

        conn.commit()
        messagebox.showinfo("Success", "Marks saved successfully!")

    except ValueError:
        messagebox.showerror(
            "Error", "Enter valid marks between 0 and 100."
        )


tk.Button(
    marks_tab,
    text="Save Marks",
    command=add_marks,
    bg="#0d6efd",
    fg="white",
    width=20
).pack(pady=15)


# ---------------- START APPLICATION ----------------

refresh_students()

def close_app():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
