
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from io import BytesIO

# DATABASE
con = sqlite3.connect("students.db", check_same_thread=False)
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS students(
roll TEXT PRIMARY KEY, name TEXT, course TEXT,
semester TEXT, phone TEXT, email TEXT)""")

cur.execute("""CREATE TABLE IF NOT EXISTS attendance(
roll TEXT, date TEXT, status TEXT)""")

cur.execute("""CREATE TABLE IF NOT EXISTS marks(
roll TEXT, subject TEXT, marks REAL)""")
con.commit()

# FUNCTIONS
def get_data(table):
    return pd.read_sql(f"SELECT * FROM {table}", con)

st.set_page_config(page_title="Student Management", page_icon="🎓",
                   layout="wide")

st.title("🎓 Student Management System")
st.sidebar.title("Main Menu")

menu = st.sidebar.radio("Select Option", [
    "Dashboard", "Add Student", "View Students",
    "Attendance", "Marks"
])

# DASHBOARD
if menu == "Dashboard":
    students = get_data("students")
    attendance = get_data("attendance")
    marks = get_data("marks")

    a, b, c = st.columns(3)
    a.metric("Total Students", len(students))
    b.metric("Attendance Records", len(attendance))
    c.metric("Marks Records", len(marks))

    st.subheader("Student Details")
    st.dataframe(students, use_container_width=True)

# ADD STUDENT
elif menu == "Add Student":
    st.header("Add New Student")

    with st.form("student_form"):
        roll = st.text_input("Roll Number")
        name = st.text_input("Student Name")
        course = st.selectbox("Course", ["BCA", "BBA", "BSc", "BCom"])
        semester = st.selectbox("Semester", ["1", "2", "3", "4", "5", "6"])
        phone = st.text_input("Phone")
        email = st.text_input("Email")

        submit = st.form_submit_button("Add Student")

        if submit:
            if not roll.strip() or not name.strip():
                st.error("Enter Roll Number and Name")
            else:
                try:
                    cur.execute(
                        "INSERT INTO students VALUES(?,?,?,?,?,?)",
                        (roll, name, course, semester, phone, email)
                    )
                    con.commit()
                    st.success("Student Added Successfully!")
                except sqlite3.IntegrityError:
                    st.error("Roll Number Already Exists!")

# VIEW, SEARCH, UPDATE AND DELETE
elif menu == "View Students":
    st.header("Student Records")

    df = get_data("students")
    search = st.text_input("Search by Name or Roll Number")

    if search:
        df = df[
            df["name"].str.contains(search, case=False, na=False) |
            df["roll"].str.contains(search, case=False, na=False)
        ]

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "students.csv",
        "text/csv"
    )

    if not df.empty:
        roll = st.selectbox("Select Student", df["roll"].tolist())
        student = df[df["roll"] == roll].iloc[0]

        with st.form("update_form"):
            name = st.text_input("Name", student["name"])
            course = st.text_input("Course", student["course"])
            semester = st.text_input("Semester", student["semester"])
            phone = st.text_input("Phone", student["phone"])
            email = st.text_input("Email", student["email"])

            if st.form_submit_button("Update Student"):
                cur.execute("""
                    UPDATE students SET name=?, course=?, semester=?,
                    phone=?, email=? WHERE roll=?
                """, (name, course, semester, phone, email, roll))
                con.commit()
                st.success("Student Updated!")
                st.rerun()

        if st.button("Delete Student"):
            cur.execute("DELETE FROM students WHERE roll=?", (roll,))
            cur.execute("DELETE FROM attendance WHERE roll=?", (roll,))
            cur.execute("DELETE FROM marks WHERE roll=?", (roll,))
            con.commit()
            st.success("Student Deleted!")
            st.rerun()

# ATTENDANCE
elif menu == "Attendance":
    st.header("Attendance Management")

    students = get_data("students")

    if not students.empty:
        roll = st.selectbox("Select Roll Number", students["roll"])
        status = st.selectbox("Status", ["Present", "Absent"])

        if st.button("Mark Attendance"):
            today = str(date.today())

            cur.execute("""
                SELECT * FROM attendance WHERE roll=? AND date=?
            """, (roll, today))

            if cur.fetchone():
                st.warning("Attendance already marked today!")
            else:
                cur.execute(
                    "INSERT INTO attendance VALUES(?,?,?)",
                    (roll, today, status)
                )
                con.commit()
                st.success("Attendance Saved!")

    else:
        st.warning("Add students first.")

    st.subheader("Attendance Records")
    st.dataframe(get_data("attendance"), use_container_width=True)

# MARKS
elif menu == "Marks":
    st.header("Marks Management")

    students = get_data("students")

    if not students.empty:
        roll = st.selectbox("Student Roll Number", students["roll"])
        subject = st.text_input("Subject")
        marks = st.number_input("Marks", 0.0, 100.0)

        if st.button("Save Marks"):
            if subject.strip():
                cur.execute(
                    "INSERT INTO marks VALUES(?,?,?)",
                    (roll, subject, marks)
                )
                con.commit()
                st.success("Marks Saved!")
            else:
                st.error("Enter Subject Name")

    else:
        st.warning("Add students first.")

    st.subheader("Marks Records")
    st.dataframe(get_data("marks"), use_container_width=True)
