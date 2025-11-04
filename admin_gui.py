import tkinter as tk
from tkinter import ttk, messagebox
from database_config import get_connection

class AdminGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Admin Dashboard")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")

        title = tk.Label(self.root, text="🎟️ Admin Panel - Manage Movies & Shows", font=("Arial", 20, "bold"), bg="#333", fg="white")
        title.pack(fill="x")

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=10)

        tk.Label(frame, text="Movie Name:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
        self.movie_name = tk.Entry(frame, font=("Arial", 12))
        self.movie_name.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Price:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=2, padx=5)
        self.price = tk.Entry(frame, font=("Arial", 12))
        self.price.grid(row=0, column=3, padx=5)

        tk.Label(frame, text="Show Time:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=4, padx=5)
        self.show_time = tk.Entry(frame, font=("Arial", 12))
        self.show_time.grid(row=0, column=5, padx=5)

        tk.Button(frame, text="Add Movie", command=self.add_movie, bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).grid(row=0, column=6, padx=10)
        tk.Button(frame, text="Delete Movie", command=self.delete_movie, bg="#F44336", fg="white", font=("Arial", 12, "bold")).grid(row=0, column=7, padx=10)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Movie", "Price", "ShowTime"), show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Movie", text="Movie Name")
        self.tree.heading("Price", text="Price")
        self.tree.heading("ShowTime", text="Show Time")

        self.tree.column("ID", width=50)
        self.tree.column("Movie", width=200)
        self.tree.column("Price", width=100)
        self.tree.column("ShowTime", width=150)

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.view_movies()

    def get_conn(self):
        return get_connection()

    def view_movies(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT movie_id, movie_name, price FROM movie")
        data = cur.fetchall()
        cur.execute("SELECT show_name, show_time FROM shows")
        show_data = cur.fetchall()
        conn.close()
        for i, movie in enumerate(data):
            st = show_data[i]["show_time"] if i < len(show_data) else "N/A"
            self.tree.insert("", "end", values=(movie["movie_id"], movie["movie_name"], movie["price"], st))

    def add_movie(self):
        name = self.movie_name.get()
        price = self.price.get()
        show_time = self.show_time.get()

        if not name or not price or not show_time:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO movie (movie_name, price) VALUES (%s, %s)", (name, price))
        movie_id = cur.lastrowid
        cur.execute("INSERT INTO shows (movie_id, show_name, show_time, total_seats, available_seats) VALUES (%s, %s, %s, 20, 20)", (movie_id, "Evening", show_time))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"✅ '{name}' added with showtime {show_time}")
        self.view_movies()

    def delete_movie(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a movie to delete.")
            return
        movie_id = self.tree.item(selected)["values"][0]
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM movie WHERE movie_id=%s", (movie_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted", "Movie deleted successfully.")
        self.view_movies()
