import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
from database_config import get_connection

class MovieApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Ticket Reservation")
        self.root.geometry("1000x600")

        # --- Header ---
        tk.Label(
            self.root,
            text="🎬 Movie Ticket Reservation System 🎟️",
            font=("Arial", 24, "bold"),
            bg="gray",
            fg="lightgreen",
            pady=10
        ).pack(fill="x")

        # --- Show Selection Frame ---
        frame = tk.Frame(self.root, bg="#ffb6b9", pady=10)
        frame.pack(fill="x")

        tk.Label(frame, text="Select Show:", font=("Arial", 14, "bold"), bg="#ffb6b9").grid(row=0, column=0, padx=10)
        self.show_combo = ttk.Combobox(frame, font=("Arial", 14), state="readonly")
        self.show_combo.grid(row=0, column=1, padx=10)
        
        tk.Label(frame, text="Your Name:", font=("Arial", 14, "bold"), bg="#ffb6b9").grid(row=0, column=2, padx=10)
        self.name_entry = tk.Entry(frame, font=("Arial", 14))
        self.name_entry.grid(row=0, column=3, padx=10)

        tk.Button(frame, text="Reserve Seat", font=("Arial", 14, "bold"), command=self.reserve_seat).grid(row=0, column=4, padx=10)
        tk.Button(frame, text="Cancel Seat", font=("Arial", 14, "bold"), command=self.cancel_reservation).grid(row=0, column=5, padx=10)

        # --- Seat Table ---
        self.tree = ttk.Treeview(self.root, columns=("seat_no", "is_booked"), show="headings")
        self.tree.heading("seat_no", text="Seat Number")
        self.tree.heading("is_booked", text="Status")
        self.tree.pack(fill="both", expand=True, pady=20)

        self.load_shows()

    # ========== Database Methods ==========
    def load_shows(self):
        """Load show names into combobox"""
        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT show_id, show_name FROM shows")
        shows = cur.fetchall()
        self.shows_dict = {s["show_name"]: s["show_id"] for s in shows}
        self.show_combo["values"] = list(self.shows_dict.keys())
        con.close()

        if shows:
            self.show_combo.current(0)
            self.load_seats()

        self.show_combo.bind("<<ComboboxSelected>>", lambda e: self.load_seats())

    def load_seats(self):
        """Load seat data for selected show"""
        show_name = self.show_combo.get()
        if not show_name:
            return
        show_id = self.shows_dict[show_name]
        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT seat_no, is_booked FROM seats WHERE show_id=%s", (show_id,))
        seats = cur.fetchall()
        con.close()

        # clear table
        for i in self.tree.get_children():
            self.tree.delete(i)

        for seat in seats:
            status = "Booked" if seat["is_booked"] else "Available"
            self.tree.insert("", "end", values=(seat["seat_no"], status))

    def reserve_seat(self):
        """Book seat selected in treeview"""
        try:
            selected = self.tree.focus()
            if not selected:
                messagebox.showerror("Error", "Please select a seat!")
                return
            seat_no = self.tree.item(selected)["values"][0]
            show_name = self.show_combo.get()
            user_name = self.name_entry.get()

            if not user_name:
                messagebox.showerror("Error", "Enter your name.")
                return

            show_id = self.shows_dict[show_name]

            con = get_connection()
            cur = con.cursor()

            # check if already booked
            cur.execute("SELECT is_booked FROM seats WHERE show_id=%s AND seat_no=%s", (show_id, seat_no))
            seat = cur.fetchone()
            if seat["is_booked"]:
                messagebox.showerror("Error", f"Seat {seat_no} already booked.")
                con.close()
                return

            # create user if not exists
            cur.execute("SELECT user_id FROM users WHERE username=%s", (user_name,))
            user = cur.fetchone()
            if user:
                user_id = user["user_id"]
            else:
                cur.execute("INSERT INTO users(username, password) VALUES(%s, %s)", (user_name, "pass"))
                user_id = cur.lastrowid

            # update booking
            cur.execute("UPDATE seats SET is_booked=1, user_id=%s WHERE show_id=%s AND seat_no=%s", (user_id, show_id, seat_no))
            cur.execute("UPDATE shows SET available_seats=available_seats-1 WHERE show_id=%s", (show_id,))

            # record reservation
            cur.execute("SELECT m.price FROM shows s JOIN movie m ON s.movie_id=m.movie_id WHERE s.show_id=%s", (show_id,))
            price = cur.fetchone()["price"]
            cur.execute("INSERT INTO reservations(user_id, show_id, seat_no, price) VALUES(%s,%s,%s,%s)", (user_id, show_id, seat_no, price))

            con.commit()
            con.close()

            messagebox.showinfo("Success", f"Seat {seat_no} booked successfully for {user_name}!")
            self.load_seats()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cancel_reservation(self):
        """Cancel selected seat"""
        try:
            selected = self.tree.focus()
            if not selected:
                messagebox.showerror("Error", "Select a seat to cancel!")
                return
            seat_no = self.tree.item(selected)["values"][0]
            show_name = self.show_combo.get()
            user_name = self.name_entry.get()
            if not user_name:
                messagebox.showerror("Error", "Enter your name to cancel.")
                return

            show_id = self.shows_dict[show_name]

            con = get_connection()
            cur = con.cursor()

            # find reservation
            q = """SELECT r.booking_id, r.user_id FROM reservations r
                   JOIN users u ON r.user_id=u.user_id
                   WHERE u.username=%s AND r.show_id=%s AND r.seat_no=%s"""
            cur.execute(q, (user_name, show_id, seat_no))
            res = cur.fetchone()

            if not res:
                messagebox.showerror("Error", "No such reservation found.")
                con.close()
                return

            cur.execute("DELETE FROM reservations WHERE booking_id=%s", (res["booking_id"],))
            cur.execute("UPDATE seats SET is_booked=0, user_id=NULL WHERE show_id=%s AND seat_no=%s", (show_id, seat_no))
            cur.execute("UPDATE shows SET available_seats=available_seats+1 WHERE show_id=%s", (show_id,))

            con.commit()
            con.close()

            messagebox.showinfo("Cancelled", f"Reservation for seat {seat_no} cancelled successfully.")
            self.load_seats()

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = MovieApp(root)
    root.mainloop()
