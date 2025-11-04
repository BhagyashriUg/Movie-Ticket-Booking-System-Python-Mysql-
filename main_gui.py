import tkinter as tk
from tkinter import messagebox
from admin_gui import AdminGUI
from user_gui import UserGUI
from database_config import get_connection

def login_window():
    root = tk.Tk()
    root.title("🎬 Movie Ticket System - Login")
    root.geometry("420x360")
    root.configure(bg="#f8f8f8")

    tk.Label(root, text="🎟️ Movie Ticket System", font=("Arial", 18, "bold"), bg="#f8f8f8").pack(pady=20)
    tk.Label(root, text="Login as:", bg="#f8f8f8", font=("Arial", 12)).pack()

    role_var = tk.StringVar(value="user")
    tk.Radiobutton(root, text="Admin", variable=role_var, value="admin", bg="#f8f8f8").pack()
    tk.Radiobutton(root, text="User", variable=role_var, value="user", bg="#f8f8f8").pack()

    tk.Label(root, text="Username:", bg="#f8f8f8", font=("Arial", 12)).pack(pady=5)
    uname = tk.Entry(root, font=("Arial", 12))
    uname.pack()

    tk.Label(root, text="Password:", bg="#f8f8f8", font=("Arial", 12)).pack(pady=5)
    pwd = tk.Entry(root, show="*", font=("Arial", 12))
    pwd.pack()

    # --- LOGIN FUNCTION ---
    def login():
        username = uname.get().strip()
        password = pwd.get().strip()
        role = role_var.get()

        if role == "admin":
            if username == "admin" and password == "admin":
                root.destroy()
                admin_root = tk.Tk()
                AdminGUI(admin_root)
                admin_root.mainloop()
            else:
                messagebox.showerror("Error", "❌ Invalid admin credentials.")
        else:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cur.fetchone()
            conn.close()

            if user:
                root.destroy()
                UserGUI(username)
            else:
                messagebox.showerror("Error", "❌ Invalid username or password.")

    # --- SIGNUP FUNCTION ---
    def signup():
        username = uname.get().strip()
        password = pwd.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields to sign up.")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        exists = cur.fetchone()
        if exists:
            messagebox.showerror("Error", "Username already exists. Try another.")
            conn.close()
            return

        cur.execute("INSERT INTO users(username, password, role) VALUES(%s, %s, 'user')", (username, password))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"✅ Account created successfully for {username}!")
        uname.delete(0, 'end')
        pwd.delete(0, 'end')

    # Buttons
    btn_frame = tk.Frame(root, bg="#f8f8f8")
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="Login", command=login, bg="#4CAF50", fg="white", width=10, font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Sign Up", command=signup, bg="#2196F3", fg="white", width=10, font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10)

    root.mainloop()


if __name__ == "__main__":
    login_window()
