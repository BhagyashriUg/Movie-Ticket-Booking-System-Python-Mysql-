import tkinter as tk
from tkinter import ttk, messagebox
from database_config import get_connection


class UserGUI:
    def __init__(self, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title(f"🎬 Movie Booking - Welcome {self.username}")
        self.root.geometry("950x650")
        self.root.configure(bg="#f8f8f8")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.create_movies_tab()
        self.create_mybookings_tab()
        self.create_trending_tab()

        self.root.mainloop()

    # ---------------- DB CONNECTION ----------------
    def get_conn(self):
        return get_connection()

    # ---------------- MOVIES TAB ----------------
    def create_movies_tab(self):
        frame = tk.Frame(self.notebook, bg="#f8f8f8")
        self.notebook.add(frame, text="🎥 Movies")

        tk.Label(frame, text="🎬 Available Movies", font=("Arial", 16, "bold"), bg="#f8f8f8").pack(pady=10)
        self.movie_tree = ttk.Treeview(frame, columns=("ID", "Name", "Price"), show="headings", height=12)
        self.movie_tree.heading("ID", text="ID")
        self.movie_tree.heading("Name", text="Movie Name")
        self.movie_tree.heading("Price", text="Price (₹)")
        self.movie_tree.pack(pady=10)

        tk.Button(frame, text="Book Selected Movie", bg="#4CAF50", fg="white",
                  font=("Arial", 12, "bold"), command=self.open_seat_window).pack(pady=10)

        self.load_movies()

    def load_movies(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT movie_id, movie_name, price FROM movie")
        rows = cur.fetchall()
        conn.close()
        self.movie_tree.delete(*self.movie_tree.get_children())
        for row in rows:
            self.movie_tree.insert("", "end", values=(row["movie_id"], row["movie_name"], row["price"]))

    # ---------------- TRENDING TAB ----------------
    def create_trending_tab(self):
        frame = tk.Frame(self.notebook, bg="#f8f8f8")
        self.notebook.add(frame, text="🔥 Trending Movies")

        tk.Label(frame, text="🔥 Trending Movies", font=("Arial", 16, "bold"), bg="#f8f8f8").pack(pady=10)
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT movie_id, movie_name, price FROM movie ORDER BY movie_id DESC LIMIT 5")
        trending = cur.fetchall()
        conn.close()

        for movie in trending:
            tk.Button(frame,
                      text=f"{movie['movie_name']} - ₹{movie['price']}",
                      bg="#ff9800", fg="white", font=("Arial", 12, "bold"),
                      width=40,
                      command=lambda m=movie: self.open_seat_window_direct(m)).pack(pady=8)

    def open_seat_window_direct(self, movie):
        self.ensure_seats_exist(movie["movie_id"])
        self.open_seat_gui(movie["movie_id"], movie["movie_name"], movie["price"])

    # ---------------- ENSURE SEATS EXIST ----------------
    def ensure_seats_exist(self, movie_id):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT show_id FROM shows WHERE movie_id=%s", (movie_id,))
        show = cur.fetchone()
        if not show:
            conn.close()
            return
        show_id = show["show_id"]

        cur.execute("SELECT COUNT(*) AS cnt FROM seats WHERE show_id=%s", (show_id,))
        count = cur.fetchone()["cnt"]
        if count == 0:
            seats = [f"{chr(65+i)}{j+1}" for i in range(4) for j in range(5)]
            for s in seats:
                cur.execute("INSERT INTO seats(show_id, seat_no, is_booked) VALUES(%s,%s,0)", (show_id, s))
            conn.commit()
        conn.close()

    # ---------------- SEAT WINDOW ----------------
    def open_seat_window(self):
        selected = self.movie_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a movie first.")
            return
        movie = self.movie_tree.item(selected)["values"]
        self.ensure_seats_exist(movie[0])
        self.open_seat_gui(movie[0], movie[1], movie[2])

    def open_seat_gui(self, movie_id, movie_name, price):
        seat_win = tk.Toplevel(self.root)
        seat_win.title(f"🎟️ {movie_name} - Seat Booking")
        seat_win.geometry("600x500")
        seat_win.configure(bg="white")

        tk.Label(seat_win, text=f"Select Seats for {movie_name}", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        seat_frame = tk.Frame(seat_win, bg="white")
        seat_frame.pack(pady=10)

        selected_seats = []

        # --- fetch show_id before loading seats ---
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT show_id FROM shows WHERE movie_id=%s", (movie_id,))
        show = cur.fetchone()
        conn.close()
        if not show:
            messagebox.showerror("Error", "No show found for this movie.")
            return
        show_id = show["show_id"]

        # --- seat refresh function ---
        def refresh_seats():
            for widget in seat_frame.winfo_children():
                widget.destroy()

            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("SELECT seat_no, is_booked FROM seats WHERE show_id=%s ORDER BY seat_id", (show_id,))
            seats = cur.fetchall()
            conn.close()

            for i, seat in enumerate(seats):
                color = "red" if seat["is_booked"] else "green"
                btn = tk.Button(seat_frame, text=seat["seat_no"], width=5,
                                bg=color, fg="white", font=("Arial", 10, "bold"))

                def toggle(s=seat):
                    if s["is_booked"]:
                        messagebox.showerror("Error", f"Seat {s['seat_no']} already booked!")
                    else:
                        if s["seat_no"] not in selected_seats:
                            selected_seats.append(s["seat_no"])
                            btn.config(bg="#ffeb3b")  # yellow when selected
                        else:
                            selected_seats.remove(s["seat_no"])
                            btn.config(bg="green")

                btn.config(command=toggle)
                btn.grid(row=i // 5, column=i % 5, padx=10, pady=10)

        refresh_seats()

        # --- confirm booking ---
        def confirm_booking():
            if not selected_seats:
                messagebox.showerror("Error", "Please select at least one seat.")
                return

            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM users WHERE username=%s", (self.username,))
            user = cur.fetchone()
            user_id = user["user_id"]

            for seat_no in selected_seats:
                cur.execute("""
                    UPDATE seats 
                    SET is_booked=1, user_id=%s 
                    WHERE show_id=%s AND seat_no=%s AND is_booked=0
                """, (user_id, show_id, seat_no))
                cur.execute("""
                    INSERT INTO reservations (user_id, show_id, seat_no, price) 
                    VALUES (%s,%s,%s,%s)
                """, (user_id, show_id, seat_no, price))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"🎉 Booked: {', '.join(selected_seats)}")
            selected_seats.clear()
            refresh_seats()
            self.load_my_bookings()

        tk.Button(seat_win, text="✅ Confirm Booking", bg="#4CAF50", fg="white",
                  font=("Arial", 12, "bold"), command=confirm_booking).pack(pady=10)

        tk.Button(seat_win, text="🔄 Refresh Seats", bg="#2196F3", fg="white",
                  font=("Arial", 12, "bold"), command=refresh_seats).pack(pady=5)

    # ---------------- MY BOOKINGS ----------------
    def create_mybookings_tab(self):
        frame = tk.Frame(self.notebook, bg="#f8f8f8")
        self.notebook.add(frame, text="🎟️ My Bookings")

        tk.Label(frame, text="🎟️ My Bookings", font=("Arial", 16, "bold"), bg="#f8f8f8").pack(pady=10)

        self.booking_tree = ttk.Treeview(frame, columns=("Movie", "Seat", "Time", "Price"),
                                         show="headings", height=12)
        self.booking_tree.heading("Movie", text="Movie")
        self.booking_tree.heading("Seat", text="Seat No")
        self.booking_tree.heading("Time", text="Booking Time")
        self.booking_tree.heading("Price", text="Price (₹)")
        self.booking_tree.pack(pady=10)

        btn_frame = tk.Frame(frame, bg="#f8f8f8")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="🔄 Refresh", bg="#2196F3", fg="white",
                  font=("Arial", 12, "bold"), command=self.load_my_bookings).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="❌ Cancel Selected", bg="#f44336", fg="white",
                  font=("Arial", 12, "bold"), command=self.cancel_booking).grid(row=0, column=1, padx=10)

        self.load_my_bookings()

    def load_my_bookings(self):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.movie_name, r.seat_no, r.booking_time, r.price
            FROM reservations r
            JOIN shows s ON r.show_id = s.show_id
            JOIN movie m ON s.movie_id = m.movie_id
            JOIN users u ON r.user_id = u.user_id
            WHERE u.username=%s
            ORDER BY r.booking_time DESC
        """, (self.username,))
        rows = cur.fetchall()
        conn.close()

        self.booking_tree.delete(*self.booking_tree.get_children())
        for r in rows:
            self.booking_tree.insert("", "end", values=(r["movie_name"], r["seat_no"], r["booking_time"], r["price"]))

    def cancel_booking(self):
        selected = self.booking_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a booking to cancel.")
            return

        item = self.booking_tree.item(selected)
        movie_name, seat_no = item["values"][0], item["values"][1]

        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT show_id FROM shows WHERE movie_id=(SELECT movie_id FROM movie WHERE movie_name=%s)",
                    (movie_name,))
        show_id = cur.fetchone()["show_id"]

        cur.execute("UPDATE seats SET is_booked=0, user_id=NULL WHERE show_id=%s AND seat_no=%s",
                    (show_id, seat_no))
        cur.execute("DELETE FROM reservations WHERE show_id=%s AND seat_no=%s", (show_id, seat_no))
        conn.commit()
        conn.close()

        messagebox.showinfo("Cancelled", f"❌ Booking cancelled for seat {seat_no}.")
        self.load_my_bookings()


if __name__ == "__main__":
    UserGUI("testuser")
