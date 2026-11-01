
import tkinter as tk
from tkinter import messagebox
import sqlite3

# Database connection
db = sqlite3.connect("students.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students(
    roll INTEGER PRIMARY KEY,
    name TEXT,
    course TEXT,
    phone TEXT
)
""")
db.commit()


root = tk.Tk()
root.title("Student Management System")
root.geometry("600x500")

tk.Label(root, text="STUDENT MANAGEMENT SYSTEM",
         font=("Arial", 18, "bold")).pack(pady=15)

# Input fields
tk.Label(root, text="Roll Number").pack()
roll = tk.Entry(root)
roll.pack()

tk.Label(root, text="Student Name").pack()
name = tk.Entry(root)
name.pack()

tk.Label(root, text="Course").pack()
course = tk.Entry(root)
course.pack()

tk.Label(root, text="Phone").pack()
phone = tk.Entry(root)
phone.pack()


# Add student
def add_student():
    try:
        cur.execute("INSERT INTO students VALUES(?,?,?,?)",
                    (roll.get(), name.get(), course.get(), phone.get()))
        db.commit()
        messagebox.showinfo("Success", "Student Added!")
        clear()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Roll Number already exists!")


# View students
def view_students():
    cur.execute("SELECT * FROM students")
    records = cur.fetchall()

    result = ""
    for student in records:
        result += str(student) + "\n"

    messagebox.showinfo("Student Records", result or "No Records Found")


# Delete student
def delete_student():
    cur.execute("DELETE FROM students WHERE roll=?", (roll.get(),))
    db.commit()
    messagebox.showinfo("Success", "Student Deleted!")
    clear()


# Clear input fields
def clear():
    roll.delete(0, tk.END)
    name.delete(0, tk.END)
    course.delete(0, tk.END)
    phone.delete(0, tk.END)


# Buttons
tk.Button(root, text="Add Student",
          command=add_student, width=20).pack(pady=5)

tk.Button(root, text="View Students",
          command=view_students, width=20).pack(pady=5)

tk.Button(root, text="Delete Student",
          command=delete_student, width=20).pack(pady=5)

tk.Button(root, text="Clear",
          command=clear, width=20).pack(pady=5)


# Run application
root.mainloop()

db.close()
