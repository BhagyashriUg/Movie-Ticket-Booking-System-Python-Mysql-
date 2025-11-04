from database_config import get_connection

class UserModule:
    def __init__(self, username):
        self.username = username
        self.conn = get_connection()
        self.cur = self.conn.cursor()

        # Auto-create user if not exists
        self.cur.execute("SELECT user_id FROM users WHERE username=%s", (username,))
        row = self.cur.fetchone()
        if row:
            self.user_id = row["user_id"]
        else:
            self.cur.execute("INSERT INTO users(username,password,role) VALUES(%s,%s,'user')",
                             (username, "password"))
            self.conn.commit()
            self.user_id = self.cur.lastrowid

    def view_shows(self):
        self.cur.execute("""SELECT s.show_id, m.movie_name, s.show_name, s.show_time, s.available_seats
                            FROM shows s JOIN movie m ON s.movie_id=m.movie_id""")
        return self.cur.fetchall()

    def view_available_seats(self, show_id):
        self.cur.execute("SELECT seat_no, is_booked FROM seats WHERE show_id=%s", (show_id,))
        return self.cur.fetchall()

    def book_seat(self, show_id, seat_no):
        self.cur.execute("SELECT is_booked FROM seats WHERE show_id=%s AND seat_no=%s", (show_id, seat_no))
        seat = self.cur.fetchone()
        if not seat:
            print("❌ Invalid seat.")
            return
        if seat["is_booked"]:
            print("❌ Seat already booked.")
            return

        self.cur.execute("UPDATE seats SET is_booked=1, user_id=%s WHERE show_id=%s AND seat_no=%s",
                         (self.user_id, show_id, seat_no))
        self.cur.execute("UPDATE shows SET available_seats=available_seats-1 WHERE show_id=%s", (show_id,))
        self.cur.execute("SELECT m.price FROM shows s JOIN movie m ON s.movie_id=m.movie_id WHERE s.show_id=%s", (show_id,))
        price = self.cur.fetchone()["price"]

        self.cur.execute("INSERT INTO reservations(user_id, show_id, seat_no, price) VALUES(%s,%s,%s,%s)",
                         (self.user_id, show_id, seat_no, price))
        self.conn.commit()
        print(f"✅ Seat {seat_no} booked successfully for user {self.username}!")

    def cancel_booking(self, seat_no):
        q = """SELECT r.show_id, r.booking_id FROM reservations r
               WHERE r.user_id=%s AND r.seat_no=%s"""
        self.cur.execute(q, (self.user_id, seat_no))
        row = self.cur.fetchone()
        if not row:
            print("❌ No such booking found.")
            return

        show_id = row["show_id"]
        self.cur.execute("DELETE FROM reservations WHERE booking_id=%s", (row["booking_id"],))
        self.cur.execute("UPDATE seats SET is_booked=0, user_id=NULL WHERE show_id=%s AND seat_no=%s",
                         (show_id, seat_no))
        self.cur.execute("UPDATE shows SET available_seats=available_seats+1 WHERE show_id=%s", (show_id,))
        self.conn.commit()
        print(f"✅ Booking for seat {seat_no} cancelled.")

    def close(self):
        self.conn.close()
