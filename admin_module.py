from database_config import get_connection

class AdminModule:
    def __init__(self):
        self.conn = get_connection()
        self.cur = self.conn.cursor()

    def view_movies(self):
        self.cur.execute("SELECT * FROM movie")
        return self.cur.fetchall()

    def add_movie(self, name, price):
        self.cur.execute("INSERT INTO movie(movie_name, price) VALUES(%s, %s)", (name, price))
        self.conn.commit()
        print(f"✅ Movie '{name}' added successfully!")

    def delete_movie(self, movie_id):
        self.cur.execute("DELETE FROM movie WHERE movie_id=%s", (movie_id,))
        self.conn.commit()
        print("✅ Movie deleted successfully.")

    def view_reservations(self):
        q = """SELECT r.booking_id, u.username, m.movie_name, s.show_name, r.seat_no, r.booking_time
               FROM reservations r
               JOIN users u ON r.user_id=u.user_id
               JOIN shows s ON r.show_id=s.show_id
               JOIN movie m ON s.movie_id=m.movie_id"""
        self.cur.execute(q)
        return self.cur.fetchall()

    def close(self):
        self.conn.close()
