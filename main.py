from admin_module import AdminModule
from user_module import UserModule

def admin_menu():
    admin = AdminModule()
    while True:
        print("\n=== Admin Menu ===")
        print("1. View Movies\n2. Add Movie\n3. Delete Movie\n4. View Reservations\n5. Exit")
        ch = input("Enter choice: ")
        if ch == '1':
            for m in admin.view_movies():
                print(m)
        elif ch == '2':
            name = input("Movie Name: ")
            price = int(input("Price: "))
            admin.add_movie(name, price)
        elif ch == '3':
            mid = int(input("Movie ID: "))
            admin.delete_movie(mid)
        elif ch == '4':
            for r in admin.view_reservations():
                print(r)
        else:
            break
    admin.close()

def user_menu(username):
    user = UserModule(username)
    while True:
        print("\n=== User Menu ===")
        print("1. View Shows\n2. View Seats\n3. Book Seat\n4. Cancel Booking\n5. Exit")
        ch = input("Enter choice: ")
        if ch == '1':
            for s in user.view_shows():
                print(s)
        elif ch == '2':
            sid = int(input("Show ID: "))
            for s in user.view_available_seats(sid):
                print(s)
        elif ch == '3':
            sid = int(input("Show ID: "))
            seat = input("Seat No (e.g., A05): ").upper()
            user.book_seat(sid, seat)
        elif ch == '4':
            seat = input("Seat No to cancel: ").upper()
            user.cancel_booking(seat)
        else:
            break
    user.close()

def main():
    print("🎬 Welcome to Movie Ticket Reservation System 🎫")
    role = input("Login as (admin/user): ").strip().lower()
    if role == 'admin':
        uname = input("Username: ")
        pwd = input("Password: ")
        if uname == 'admin' and pwd == 'admin':
            admin_menu()
        else:
            print("❌ Invalid admin credentials.")
    else:
        uname = input("Enter your name: ")
        user_menu(uname)

if __name__ == "__main__":
    main()
