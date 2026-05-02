import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt


class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f4f6f8")

        self.conn = sqlite3.connect("library_gui.db")
        self.cursor = self.conn.cursor()

        self.current_user = None

        self.colors = {
            "bg": "#f4f6f8",
            "card": "#ffffff",
            "primary": "#1f4e79",
            "secondary": "#2e86c1",
            "success": "#1e8449",
            "danger": "#c0392b",
            "text": "#1f1f1f",
            "muted": "#5f6b7a"
        }

        self.setup_styles()
        self.create_tables()
        self.seed_admin()
        self.show_login_screen()

    # ---------------- DATABASE ----------------
    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'student'))
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity >= 0)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS issued_books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            fine INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
        """)
        self.conn.commit()

    def seed_admin(self):
        self.cursor.execute("SELECT * FROM users WHERE name=?", ("admin",))
        admin = self.cursor.fetchone()
        if not admin:
            self.cursor.execute(
                "INSERT INTO users (name, password, role) VALUES (?, ?, ?)",
                ("admin", "admin123", "admin")
            )
            self.conn.commit()

    # ---------------- STYLE ----------------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=28,
                        fieldbackground="white",
                        font=("Segoe UI", 10))

        style.configure("Treeview.Heading",
                        background=self.colors["primary"],
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))

        style.map("Treeview", background=[("selected", "#d6eaf8")])

    # ---------------- BASIC UI HELPERS ----------------
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_header(self, title, subtitle=""):
        header = tk.Frame(self.root, bg=self.colors["primary"], height=90)
        header.pack(fill="x")

        tk.Label(
            header,
            text=title,
            bg=self.colors["primary"],
            fg="white",
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w", padx=25, pady=(15, 2))

        tk.Label(
            header,
            text=subtitle,
            bg=self.colors["primary"],
            fg="#d6eaf8",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=25)

    def create_card(self, parent):
        return tk.Frame(
            parent,
            bg=self.colors["card"],
            highlightthickness=1,
            highlightbackground="#d9dee3"
        )

    # ---------------- LOGIN / REGISTER ----------------
    def show_login_screen(self):
        self.clear_window()
        self.create_header("Library Management System", "Login to continue")

        outer = tk.Frame(self.root, bg=self.colors["bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        card = self.create_card(outer)
        card.place(relx=0.5, rely=0.45, anchor="center", width=420, height=360)

        tk.Label(
            card,
            text="Login",
            font=("Segoe UI", 20, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).pack(pady=(25, 20))

        tk.Label(card, text="Username", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", padx=40)
        self.login_name = tk.Entry(card, font=("Segoe UI", 11), width=30)
        self.login_name.pack(padx=40, pady=(5, 15), ipady=6)

        tk.Label(card, text="Password", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", padx=40)
        self.login_password = tk.Entry(card, font=("Segoe UI", 11), width=30, show="*")
        self.login_password.pack(padx=40, pady=(5, 20), ipady=6)

        btn_frame = tk.Frame(card, bg=self.colors["card"])
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Login",
            width=14,
            bg=self.colors["secondary"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            pady=8,
            command=self.login_user
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            btn_frame,
            text="Register",
            width=14,
            bg=self.colors["success"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            pady=8,
            command=self.show_register_screen
        ).grid(row=0, column=1, padx=8)

        tk.Label(
            card,
            text="Default Admin Login:\nUsername: admin\nPassword: admin123",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9)
        ).pack(pady=18)

    def show_register_screen(self):
        self.clear_window()
        self.create_header("Register New User", "Create an account")

        outer = tk.Frame(self.root, bg=self.colors["bg"])
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        card = self.create_card(outer)
        card.place(relx=0.5, rely=0.45, anchor="center", width=450, height=420)

        tk.Label(
            card,
            text="Register",
            font=("Segoe UI", 20, "bold"),
            bg=self.colors["card"],
            fg=self.colors["text"]
        ).pack(pady=(25, 20))

        tk.Label(card, text="Username", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", padx=40)
        self.reg_name = tk.Entry(card, font=("Segoe UI", 11), width=32)
        self.reg_name.pack(padx=40, pady=(5, 12), ipady=6)

        tk.Label(card, text="Password", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", padx=40)
        self.reg_password = tk.Entry(card, font=("Segoe UI", 11), width=32, show="*")
        self.reg_password.pack(padx=40, pady=(5, 12), ipady=6)

        tk.Label(card, text="Role", bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", padx=40)
        self.reg_role = ttk.Combobox(card, values=["admin", "student"], state="readonly", width=29, font=("Segoe UI", 10))
        self.reg_role.pack(padx=40, pady=(5, 18), ipady=4)
        self.reg_role.set("student")

        btn_frame = tk.Frame(card, bg=self.colors["card"])
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame,
            text="Create Account",
            width=16,
            bg=self.colors["success"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            pady=8,
            command=self.register_user
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            btn_frame,
            text="Back",
            width=12,
            bg=self.colors["danger"],
            fg="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            pady=8,
            command=self.show_login_screen
        ).grid(row=0, column=1, padx=8)

    def register_user(self):
        name = self.reg_name.get().strip()
        password = self.reg_password.get().strip()
        role = self.reg_role.get().strip()

        if not name or not password:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        try:
            self.cursor.execute(
                "INSERT INTO users (name, password, role) VALUES (?, ?, ?)",
                (name, password, role)
            )
            self.conn.commit()
            messagebox.showinfo("Success", "User registered successfully.")
            self.show_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")

    def login_user(self):
        name = self.login_name.get().strip()
        password = self.login_password.get().strip()

        self.cursor.execute(
            "SELECT * FROM users WHERE name=? AND password=?",
            (name, password)
        )
        user = self.cursor.fetchone()

        if user:
            self.current_user = user
            messagebox.showinfo("Success", f"Welcome, {user[1]}!")
            if user[3] == "admin":
                self.show_admin_dashboard()
            else:
                self.show_student_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    # ---------------- DASHBOARDS ----------------
    def show_admin_dashboard(self):
        self.clear_window()
        self.create_header("Admin Dashboard", f"Logged in as: {self.current_user[1]} (Admin)")

        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=20)

        left = self.create_card(main)
        left.pack(side="left", fill="y", padx=(0, 15), ipadx=8, ipady=8)

        right = self.create_card(main)
        right.pack(side="right", fill="both", expand=True, ipadx=8, ipady=8)

        tk.Label(left, text="Navigation", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 14, "bold")).pack(pady=15, padx=20)

        buttons = [
            ("Add Book", self.add_book_window, self.colors["secondary"]),
            ("View Books", self.view_books_window, self.colors["primary"]),
            ("Issued Records", self.view_issued_books_window, self.colors["secondary"]),
            ("Analytics Graph", self.show_graph, self.colors["success"]),
            ("Logout", self.show_login_screen, self.colors["danger"])
        ]

        for text, cmd, color in buttons:
            tk.Button(left, text=text, command=cmd, width=18, bg=color, fg="white",
                      font=("Segoe UI", 10, "bold"), bd=0, pady=10).pack(pady=8, padx=20)

        self.admin_content = right
        self.show_home_panel(right, "Admin can add books, view inventory, monitor issued records, and see analytics.")

    def show_student_dashboard(self):
        self.clear_window()
        self.create_header("Student Dashboard", f"Logged in as: {self.current_user[1]} (Student)")

        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=20)

        left = self.create_card(main)
        left.pack(side="left", fill="y", padx=(0, 15), ipadx=8, ipady=8)

        right = self.create_card(main)
        right.pack(side="right", fill="both", expand=True, ipadx=8, ipady=8)

        tk.Label(left, text="Navigation", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 14, "bold")).pack(pady=15, padx=20)

        buttons = [
            ("View Books", self.view_books_window, self.colors["primary"]),
            ("Issue Book", self.issue_book_window, self.colors["secondary"]),
            ("Return Book", self.return_book_window, self.colors["success"]),
            ("My Issued Books", self.my_issued_books_window, self.colors["secondary"]),
            ("Logout", self.show_login_screen, self.colors["danger"])
        ]

        for text, cmd, color in buttons:
            tk.Button(left, text=text, command=cmd, width=18, bg=color, fg="white",
                      font=("Segoe UI", 10, "bold"), bd=0, pady=10).pack(pady=8, padx=20)

        self.student_content = right
        self.show_home_panel(right, "Student can browse books, issue books, return books, and check personal records.")

    def show_home_panel(self, parent, text):
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text="Welcome", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 24, "bold")).pack(pady=(70, 10))

        tk.Label(parent, text=text, bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 12), wraplength=600, justify="center").pack(pady=10)

        stats = tk.Frame(parent, bg=self.colors["card"])
        stats.pack(pady=35)

        self.cursor.execute("SELECT COUNT(*) FROM books")
        total_books = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM users")
        total_users = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM issued_books WHERE return_date IS NULL")
        active_issues = self.cursor.fetchone()[0]

        data = [
            ("Total Books", total_books, self.colors["secondary"]),
            ("Total Users", total_users, self.colors["primary"]),
            ("Active Issues", active_issues, self.colors["success"])
        ]

        for title, value, color in data:
            box = tk.Frame(stats, bg=color, width=180, height=100)
            box.pack(side="left", padx=12)
            box.pack_propagate(False)

            tk.Label(box, text=title, bg=color, fg="white",
                     font=("Segoe UI", 11, "bold")).pack(pady=(20, 6))
            tk.Label(box, text=str(value), bg=color, fg="white",
                     font=("Segoe UI", 20, "bold")).pack()

    # ---------------- TABLE ----------------
    def draw_table(self, parent, columns, rows, heading):
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text=heading, bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(20, 10))

        container = tk.Frame(parent, bg=self.colors["card"])
        container.pack(fill="both", expand=True, padx=20, pady=10)

        tree = ttk.Treeview(container, columns=columns, show="headings")
        y_scroll = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        x_scroll = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)

        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor="center")

        for row in rows:
            tree.insert("", "end", values=row)

        tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")

    # ---------------- BOOK FEATURES ----------------
    def add_book_window(self):
        parent = self.admin_content
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text="Add New Book", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(20, 15))

        form = tk.Frame(parent, bg=self.colors["card"])
        form.pack(padx=30, pady=20, anchor="w")

        tk.Label(form, text="Title", bg=self.colors["card"], fg=self.colors["muted"]).grid(row=0, column=0, sticky="w", pady=8)
        title_entry = tk.Entry(form, font=("Segoe UI", 11), width=35)
        title_entry.grid(row=0, column=1, padx=15, pady=8, ipady=5)

        tk.Label(form, text="Author", bg=self.colors["card"], fg=self.colors["muted"]).grid(row=1, column=0, sticky="w", pady=8)
        author_entry = tk.Entry(form, font=("Segoe UI", 11), width=35)
        author_entry.grid(row=1, column=1, padx=15, pady=8, ipady=5)

        tk.Label(form, text="Quantity", bg=self.colors["card"], fg=self.colors["muted"]).grid(row=2, column=0, sticky="w", pady=8)
        quantity_entry = tk.Entry(form, font=("Segoe UI", 11), width=35)
        quantity_entry.grid(row=2, column=1, padx=15, pady=8, ipady=5)

        def save_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            quantity = quantity_entry.get().strip()

            if not title or not author or not quantity.isdigit():
                messagebox.showerror("Error", "Enter valid book details.")
                return

            self.cursor.execute(
                "INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)",
                (title, author, int(quantity))
            )
            self.conn.commit()
            messagebox.showinfo("Success", "Book added successfully.")
            self.view_books_window()

        tk.Button(parent, text="Save Book", command=save_book, bg=self.colors["success"],
                  fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=10, width=18).pack(padx=30, anchor="w")

    def view_books_window(self):
        target = self.admin_content if self.current_user[3] == "admin" else self.student_content
        self.cursor.execute("SELECT id, title, author, quantity FROM books")
        rows = self.cursor.fetchall()
        self.draw_table(target, ("ID", "Title", "Author", "Quantity"), rows, "Available Books")

    # ---------------- ISSUE BOOK ----------------
    def issue_book_window(self):
        parent = self.student_content
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text="Issue Book", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(20, 15))

        self.cursor.execute("SELECT id, title, author, quantity FROM books")
        books = self.cursor.fetchall()

        form = tk.Frame(parent, bg=self.colors["card"])
        form.pack(padx=30, pady=20, anchor="w")

        tk.Label(form, text="Select Book", bg=self.colors["card"], fg=self.colors["muted"]).grid(row=0, column=0, sticky="w", pady=8)

        book_map = {}
        book_values = []

        for book in books:
            display = f"{book[0]} | {book[1]} by {book[2]} | Qty: {book[3]}"
            book_values.append(display)
            book_map[display] = book

        selected_book = ttk.Combobox(form, values=book_values, state="readonly", width=45, font=("Segoe UI", 10))
        selected_book.grid(row=0, column=1, padx=15, pady=8, ipady=4)

        def issue_selected_book():
            choice = selected_book.get()
            if not choice:
                messagebox.showerror("Error", "Please select a book.")
                return

            book = book_map[choice]
            book_id, _, _, quantity = book

            if quantity <= 0:
                messagebox.showwarning("Unavailable", "This book is currently not available.")
                return

            issue_date = datetime.now()
            due_date = issue_date + timedelta(days=7)

            self.cursor.execute("""
                INSERT INTO issued_books (user_id, book_id, issue_date, due_date)
                VALUES (?, ?, ?, ?)
            """, (
                self.current_user[0],
                book_id,
                issue_date.strftime("%Y-%m-%d"),
                due_date.strftime("%Y-%m-%d")
            ))

            self.cursor.execute(
                "UPDATE books SET quantity = quantity - 1 WHERE id=?",
                (book_id,)
            )
            self.conn.commit()

            messagebox.showinfo("Book Issued", f"Book issued successfully.\nDue Date: {due_date.strftime('%Y-%m-%d')}")
            self.my_issued_books_window()

        tk.Button(parent, text="Issue Book", command=issue_selected_book, bg=self.colors["secondary"],
                  fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=10, width=18).pack(padx=30, anchor="w")

    # ---------------- RETURN BOOK ----------------
    def return_book_window(self):
        parent = self.student_content
        for widget in parent.winfo_children():
            widget.destroy()

        tk.Label(parent, text="Return Book", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(20, 15))

        self.cursor.execute("""
            SELECT ib.id, b.title, ib.issue_date, ib.due_date
            FROM issued_books ib
            JOIN books b ON ib.book_id = b.id
            WHERE ib.user_id=? AND ib.return_date IS NULL
        """, (self.current_user[0],))
        active_records = self.cursor.fetchall()

        form = tk.Frame(parent, bg=self.colors["card"])
        form.pack(padx=30, pady=20, anchor="w")

        tk.Label(form, text="Issued Record", bg=self.colors["card"], fg=self.colors["muted"]).grid(row=0, column=0, sticky="w", pady=8)

        record_map = {}
        record_values = []

        for rec in active_records:
            display = f"Issue ID {rec[0]} | {rec[1]} | Issued: {rec[2]} | Due: {rec[3]}"
            record_values.append(display)
            record_map[display] = rec

        selected_record = ttk.Combobox(form, values=record_values, state="readonly", width=50, font=("Segoe UI", 10))
        selected_record.grid(row=0, column=1, padx=15, pady=8, ipady=4)

        def return_selected_book():
            choice = selected_record.get()
            if not choice:
                messagebox.showerror("Error", "Please select an issued record.")
                return

            issue_id, _, _, due_date_str = record_map[choice]

            self.cursor.execute("SELECT book_id, due_date FROM issued_books WHERE id=?", (issue_id,))
            row = self.cursor.fetchone()

            if not row:
                messagebox.showerror("Error", "Invalid issued record.")
                return

            book_id, due_date = row
            return_date = datetime.now()
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")

            fine = 0
            if return_date.date() > due_date_obj.date():
                late_days = (return_date.date() - due_date_obj.date()).days
                fine = late_days * 5

            self.cursor.execute("""
                UPDATE issued_books
                SET return_date=?, fine=?
                WHERE id=?
            """, (
                return_date.strftime("%Y-%m-%d"),
                fine,
                issue_id
            ))

            self.cursor.execute(
                "UPDATE books SET quantity = quantity + 1 WHERE id=?",
                (book_id,)
            )
            self.conn.commit()

            messagebox.showinfo("Book Returned", f"Book returned successfully.\nFine: ₹{fine}")
            self.my_issued_books_window()

        tk.Button(parent, text="Return Book", command=return_selected_book, bg=self.colors["success"],
                  fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=10, width=18).pack(padx=30, anchor="w")

    # ---------------- RECORDS ----------------
    def my_issued_books_window(self):
        parent = self.student_content
        self.cursor.execute("""
            SELECT ib.id, b.title, ib.issue_date, ib.due_date,
                   COALESCE(ib.return_date, 'Not Returned'),
                   ib.fine
            FROM issued_books ib
            JOIN books b ON ib.book_id = b.id
            WHERE ib.user_id=?
            ORDER BY ib.id DESC
        """, (self.current_user[0],))
        rows = self.cursor.fetchall()

        self.draw_table(
            parent,
            ("Issue ID", "Book Title", "Issue Date", "Due Date", "Return Date", "Fine"),
            rows,
            "My Issued Books"
        )

    def view_issued_books_window(self):
        parent = self.admin_content
        self.cursor.execute("""
            SELECT ib.id, u.name, b.title, ib.issue_date, ib.due_date,
                   COALESCE(ib.return_date, 'Not Returned'), ib.fine
            FROM issued_books ib
            JOIN users u ON ib.user_id = u.id
            JOIN books b ON ib.book_id = b.id
            ORDER BY ib.id DESC
        """)
        rows = self.cursor.fetchall()

        self.draw_table(
            parent,
            ("Issue ID", "Student", "Book", "Issue Date", "Due Date", "Return Date", "Fine"),
            rows,
            "Issued Book Records"
        )

    # ---------------- GRAPH ----------------
    def show_graph(self):
        self.cursor.execute("""
            SELECT b.title, COUNT(ib.book_id) AS total
            FROM issued_books ib
            JOIN books b ON b.id = ib.book_id
            GROUP BY b.title
            ORDER BY total DESC
        """)
        data = self.cursor.fetchall()

        if not data:
            messagebox.showwarning("No Data", "No issued book data available for analytics.")
            return

        titles = [row[0] for row in data]
        counts = [row[1] for row in data]

        plt.figure(figsize=(10, 5))
        plt.bar(titles, counts)
        plt.xlabel("Books")
        plt.ylabel("Times Issued")
        plt.title("Most Read Books")
        plt.xticks(rotation=20)
        plt.tight_layout()
        plt.show()

    # ---------------- CLOSE ----------------
    def close(self):
        self.conn.commit()
        self.conn.close()
        self.root.destroy()


# ---------------- MAIN ----------------
def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()


if __name__ == "__main__":
    main()