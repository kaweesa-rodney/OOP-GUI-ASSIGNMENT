import sqlite3
import csv
import re
import sys
from tkinter import *
from tkinter.ttk import Frame, Button, Label, Entry, Style, Treeview
from tkinter import BOTH, END, messagebox, filedialog

# ------------------ VALIDATION FUNCTIONS ------------------

def validate_letters(new_value):
    """
    Live validation for first name while typing.
    Allow empty during typing (so user can erase), but reject non-letters.
    """
    if new_value == "":
        return True  # allow blank while typing
    return bool(re.match(r"^[A-Za-z]+$", new_value))


# ------------------ DATABASE FUNCTIONS ------------------

def init_db():
    conn = sqlite3.connect("feedback.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            email TEXT,
            electronics TEXT,
            sports TEXT,
            gardening TEXT,
            service_feedback TEXT,
            state TEXT,
            department TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_feedback(data):
    conn = sqlite3.connect("feedback.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO feedback (first_name, email, electronics, sports, gardening, service_feedback, state, department)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()


# ------------------ MAIN FEEDBACK WINDOW ------------------

class FeedBackDlg(Toplevel):

    def __init__(self):
        Toplevel.__init__(self)
        init_db()
        self.initUI()

    def initUI(self):
        self.title("Feedback Form")
        self.geometry("700x520")
        self.style = Style()
        self.style.theme_use("default")

        xpos = 40
        ypos = 30
        xpos2 = xpos + 150

        # register only the first-name validator for live validation
        vcmd = (self.register(validate_letters), "%P")

        Label(self, text="First Name", foreground="#ff0000", background="light blue", font="Arial 9").place(x=xpos, y=ypos)
        self.txtFirstName = Entry(self, validate="key", validatecommand=vcmd)
        self.txtFirstName.place(x=xpos2, y=ypos, width=180)

        ypos += 40
        Label(self, text="Email (validated on Submit)", foreground="#ff0000", background="light blue", font="Arial 9").place(x=xpos, y=ypos)
        # NOTE: no validatecommand for email — validation happens on submit
        self.txtEmail = Entry(self)
        self.txtEmail.place(x=xpos2, y=ypos, width=260)

        ypos += 40
        Label(self, text="Your interest in our products:", foreground="#ff0000", background="light blue", font="Arial 9").place(x=xpos, y=ypos)
        ypos += 30

        self.electronicsChoice = BooleanVar(value=False)
        self.chkElectronics = Checkbutton(self, text="Electronics", variable=self.electronicsChoice)
        self.chkElectronics.place(x=xpos2, y=ypos)

        self.sportsChoice = BooleanVar(value=False)
        self.chkSports = Checkbutton(self, text="Sports", variable=self.sportsChoice)
        self.chkSports.place(x=xpos2 + 120, y=ypos)

        self.gardeningChoice = BooleanVar(value=False)
        self.chkGardening = Checkbutton(self, text="Gardening", variable=self.gardeningChoice)
        self.chkGardening.place(x=xpos2 + 240, y=ypos)

        ypos += 50
        Label(self, text="Service Feedback:", foreground="#ff0000", background="light blue", font="Arial 9").place(x=xpos, y=ypos)

        serviceChoices = [("Disappointed", "0"), ("Satisfied", "1"), ("Good", "2"), ("Excellent", "3")]
        self.serviceFeedback = StringVar(value="2")
        inc = 0
        for text, val in serviceChoices:
            Radiobutton(self, text=text, variable=self.serviceFeedback, value=val).place(x=xpos2 + inc, y=ypos)
            inc += 120

        ypos += 50
        Label(self, text="Select State:", foreground="#ff0000", background="light blue", font="Arial 9").place(x=xpos, y=ypos)

        states = ["Connecticut", "New York", "New Jersey", "Massachusetts"]
        self.lb = Listbox(self, selectmode=SINGLE, height=len(states))
        self.lb.place(x=xpos2, y=ypos)
        for state in states:
            self.lb.insert(END, state)

        ypos += 110
        Label(self, text="Department:", foreground="#ff0000", background="light blue", font="Arial 9").place(x=xpos, y=ypos)
        departments = ["Sales", "Marketing", "HR", "Technology"]
        self.dept = StringVar(value="HR")
        OptionMenu(self, self.dept, *departments).place(x=xpos2, y=ypos)

        ypos += 70
        Button(self, text="Submit", command=self.btnSubmitClick).place(x=xpos2, y=ypos)
        Button(self, text="View Feedback", command=self.view_feedback).place(x=xpos2 + 110, y=ypos)

    # ------------------ SUBMIT FEEDBACK ------------------

    def btnSubmitClick(self):
        try:
            first_name = self.txtFirstName.get().strip()
            email = self.txtEmail.get().strip()
            electronics = "YES" if self.electronicsChoice.get() else "NO"
            sports = "YES" if self.sportsChoice.get() else "NO"
            gardening = "YES" if self.gardeningChoice.get() else "NO"
            service_feedback = self.serviceFeedback.get()
            sel = self.lb.curselection()
            state = self.lb.get(sel[0]) if sel else ""
            department = self.dept.get()

            # Validate name
            if not first_name:
                messagebox.showerror("Validation Error", "First name is required.")
                self.txtFirstName.focus_set()
                return
            if not re.match(r"^[A-Za-z]+$", first_name):
                messagebox.showerror("Validation Error", "First name must contain letters only.")
                self.txtFirstName.focus_set()
                return

            # Validate email
            if not email:
                messagebox.showerror("Validation Error", "Email is required.")
                self.txtEmail.focus_set()
                return
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
                messagebox.showerror("Validation Error", "Invalid email format.")
                self.txtEmail.focus_set()
                return

            # Insert if all validations pass
            insert_feedback((first_name, email, electronics, sports, gardening, service_feedback, state, department))
            messagebox.showinfo("Success", "Feedback submitted successfully!")

            # clear fields and return focus to first name
            self.txtFirstName.delete(0, END)
            self.txtEmail.delete(0, END)
            self.electronicsChoice.set(False)
            self.sportsChoice.set(False)
            self.gardeningChoice.set(False)
            self.lb.selection_clear(0, END)
            self.txtFirstName.focus_set()

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.focus_force()
            self.txtFirstName.focus_set()

    # ------------------ VIEW ALL FEEDBACK ------------------

    def view_feedback(self):
        win = Toplevel(self)
        win.title("All Feedback")
        win.geometry("900x400")

        tree = Treeview(win, columns=("first_name", "email", "electronics", "sports", "gardening", "service_feedback", "state", "department"), show="headings")
        headings = ["First Name", "Email", "Electronics", "Sports", "Gardening", "Service", "State", "Department"]
        for col, hd in zip(tree["columns"], headings):
            tree.heading(col, text=hd)
            tree.column(col, width=110)
        tree.pack(fill=BOTH, expand=True)

        conn = sqlite3.connect("feedback.db")
        cur = conn.cursor()
        cur.execute("SELECT first_name, email, electronics, sports, gardening, service_feedback, state, department FROM feedback")
        for row in cur.fetchall():
            tree.insert("", END, values=row)
        conn.close()

        Button(win, text="Export to CSV", command=self.export_csv).pack(pady=10)

    # ------------------ EXPORT TO CSV ------------------

    def export_csv(self):
        conn = sqlite3.connect("feedback.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM feedback")
        rows = cur.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("No Data", "No feedback records found.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filename:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "First Name", "Email", "Electronics", "Sports", "Gardening", "Service Feedback", "State", "Department"])
                writer.writerows(rows)
            #messagebox.showinfo("Success", f"Feedback exported to {filename}")
