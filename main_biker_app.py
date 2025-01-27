import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import re
from hashlib import sha256
import pandas as pd
import openpyxl



class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Medewerker Login")
        self.geometry("400x300")
        self.configure(bg="#f0f0f0")

        # Center the window
        self.center_window()

        # Create database and tables
        self.conn = sqlite3.connect('bike_rental.db')
        self.cursor = self.conn.cursor()
        self.create_tables() # Creates tables needed to run and use the application
        self.create_admin_account()  # Creates default admin account if it doesn't exist

        # Create login form
        self.create_login_form()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 400
        window_height = 300
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_tables(self):
        # Create employees table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0
        )""")
        self.conn.commit()

    def create_admin_account(self):
        # Create default admin account if it doesn't exist
        admin_username = "admin"
        admin_password = "admin123"
        employee_username = "employee"
        employee_password = "employee123"
        hashed_admin_password = sha256(admin_password.encode()).hexdigest()
        hashed_employee_password = sha256(employee_password.encode()).hexdigest()

        accounts = [
            (admin_username, hashed_admin_password, 1),
            (employee_username, hashed_employee_password, 0)
        ]

        try:
            self.cursor.executemany("""
            INSERT OR IGNORE INTO employees (username, password, is_admin) 
            VALUES (?, ?, ?)""", accounts)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Fout bij het maken van admin-account: {e}")

    def create_login_form(self):
        # Create main frame
        main_frame = tk.Frame(self, bg="#f0f0f0", padx=20, pady=20)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        title_label = tk.Label(main_frame, text="Medewerker Login",
                               font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 20))

        # Username
        username_frame = tk.Frame(main_frame, bg="#f0f0f0")
        username_frame.pack(fill="x", pady=5)

        username_label = tk.Label(username_frame, text="Gebruikersnaam:",
                                  bg="#f0f0f0", font=("Arial", 12))
        username_label.pack(anchor="w")

        self.username_entry = tk.Entry(username_frame, font=("Arial", 12))
        self.username_entry.pack(fill="x", pady=(5, 0))

        # Password
        password_frame = tk.Frame(main_frame, bg="#f0f0f0")
        password_frame.pack(fill="x", pady=5)

        password_label = tk.Label(password_frame, text="Wachtwoord:",
                                  bg="#f0f0f0", font=("Arial", 12))
        password_label.pack(anchor="w")

        self.password_entry = tk.Entry(password_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(fill="x", pady=(5, 0))

        # Login button
        login_button = tk.Button(main_frame, text="Login",
                                 command=self.login,
                                 bg="#4CAF50", fg="white",
                                 font=("Arial", 12, "bold"),
                                 padx=30, pady=5)
        login_button.pack(pady=20)

        # Bind Enter key to login function
        self.bind('<Return>', lambda event: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Vul alle velden in")
            return

        hashed_password = sha256(password.encode()).hexdigest()

        try:
            self.cursor.execute("""
            SELECT id, username, is_admin FROM employees 
            WHERE username = ? AND password = ?""", (username, hashed_password))

            employee = self.cursor.fetchone()

            if employee:
                self.withdraw()  # Hide login window
                bike_rental_app = BikeRentalApp(employee, self)
                bike_rental_app.protocol("WM_DELETE_WINDOW",
                                         lambda: self.on_rental_app_close(bike_rental_app))
            else:
                messagebox.showerror("Error", "Ongeldige gebruikersnaam of wachtwoord")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

    def on_rental_app_close(self, rental_app):
        rental_app.destroy()
        self.deiconify()  # Show login window again
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()


class BikeRentalApp(tk.Toplevel):
    def __init__(self, employee, login_window):
        super().__init__()
        self.employee = employee  # Store employee info (id, username, is_admin)
        self.login_window = login_window

        self.title(f"Biker applicatie - Ingelogd als {employee[1]}")
        self.geometry("1920x1080")
        self.configure(bg="#f0f0f0")

        # Create main containers
        self.top_frame = tk.Frame(self, bg="#f0f0f0")
        self.top_frame.pack(side=tk.TOP, pady=20)

        # Add logout button
        self.logout_button = tk.Button(self.top_frame, text="Log uit",
                                       command=self.log_out,
                                       bg="#f44336", fg="white",
                                       font=("Arial", 10),
                                       padx=10, pady=5)
        self.logout_button.pack(side=tk.RIGHT, padx=20)

        # Add export button for admin users
        if self.employee[2]:  # Check if user is admin
            self.export_button = tk.Button(self.top_frame, text="Exporteer naar Excel",
                                           command=self.export_to_excel,
                                           bg="#2196F3", fg="white",
                                           font=("Arial", 10),
                                           padx=10, pady=5)
            self.export_button.pack(side=tk.RIGHT, padx=20)

        self.form_frame = tk.Frame(self, bg="#f0f0f0", padx=20)
        self.form_frame.pack(side=tk.LEFT, pady=20, fill=tk.BOTH, expand=True)

        self.client_list_frame = tk.Frame(self, bg="#f0f0f0", padx=20)
        self.client_list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=20)

        # Initialize scrollable frame for client list
        self.init_client_list_frame()

        # Create database connection
        self.conn = sqlite3.connect('bike_rental.db')
        self.cursor = self.conn.cursor()
        self.create_table()

        # Create form fields
        tk.Label(self.top_frame, text="Klant Registratie", font=("Arial", 18), bg="#f0f0f0").pack(side=tk.LEFT)

        tk.Label(self.form_frame, text="Naam:", bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.name_entry = tk.Entry(self.form_frame, font=("Arial", 12))
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.form_frame, text="Email:", bg="#f0f0f0").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.email_entry = tk.Entry(self.form_frame, font=("Arial", 12))
        self.email_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.form_frame, text="Telefoon:", bg="#f0f0f0").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.phone_entry = tk.Entry(self.form_frame, font=("Arial", 12))
        self.phone_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.form_frame, text="Type Fiets:", bg="#f0f0f0").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.rental_type = ttk.Combobox(self.form_frame, values=["Bike", "Electric Bike"], font=("Arial", 12))
        self.rental_type.grid(row=3, column=1, padx=10, pady=10)

        self.register_button = tk.Button(self.form_frame, text="Registreer Klant", command=self.register_client,
                                         bg="#4CAF50", fg="white", font=("Arial", 12), padx=10, pady=5)
        self.register_button.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

        tk.Label(self.form_frame, text="Klant ID:", bg="#f0f0f0").grid(row=7, column=0, padx=10, pady=10, sticky="e")
        self.client_id_entry = tk.Entry(self.form_frame, font=("Arial", 12))
        self.client_id_entry.grid(row=7, column=1, padx=10, pady=10)

        self.update_button = tk.Button(self.form_frame, text="Update Klant", command=self.update_client,
                                       bg="#2196F3", fg="white", font=("Arial", 12), padx=10, pady=5)
        self.update_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

        self.register_button.grid(row=6, column=0, columnspan=2, padx=10, pady=20)

        # Initial update of client list
        self.update_client_list()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log_out(self):
        self.destroy()
        LoginWindow()

    def on_closing(self):
        self.destroy()
        self.login_window.deiconify()  # Show login window
        self.login_window.username_entry.delete(0, tk.END)
        self.login_window.password_entry.delete(0, tk.END)
        self.login_window.username_entry.focus()

    def export_to_excel(self):
        try:
            # Fetch all clients from database
            self.cursor.execute("SELECT id, name, email, phone, rental_type FROM clients")
            clients = self.cursor.fetchall()

            if not clients:
                messagebox.showinfo("Info", "Geen klanten om te exporteren")
                return

            # Create DataFrame
            df = pd.DataFrame(clients, columns=['ID', 'Name', 'Email', 'Phone', 'Rental Type'])

            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[("Excel files", "*.xlsx")],
                initialfile="bike_rental_clients.xlsx"
            )

            if file_path:
                # Export to Excel
                df.to_excel(file_path, index=False, sheet_name='Clients')
                messagebox.showinfo("Success", "Klantgegevens succesvol geëxporteerd!")
        except Exception as e:
            messagebox.showerror("Error", f"Er is een fout opgetreden bij het exporteren: {str(e)}")

    def init_client_list_frame(self):
        # Create a canvas and scrollbar for the client list
        self.client_canvas = tk.Canvas(self.client_list_frame, bg="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self.client_list_frame, orient=tk.VERTICAL, command=self.client_canvas.yview)

        # Create a frame inside the canvas to hold the client list
        self.scrollable_frame = tk.Frame(self.client_canvas, bg="#f0f0f0")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.client_canvas.configure(scrollregion=self.client_canvas.bbox("all"))
        )

        # Create window inside canvas to hold the scrollable frame
        self.client_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.client_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.client_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS clients (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            email TEXT,
                            phone TEXT UNIQUE,
                            rental_type TEXT)""")
        dummy_clients = [
            ("Guus S", "guus@guus.com", "123", "Bike"),
            ("John Doe", "john.doe@example.com", "0612345678", "Bike"),
            ("Emma Smith", "emma.smith@example.com", "0687654321", "Electric Bike"),
            ("Michael Johnson", "michael.j@example.com", "0623456789", "Bike"),
            ("Sarah Williams", "sarah.w@example.com", "0698765432", "Electric Bike"),
            ("David Brown", "david.brown@example.com", "0643210987", "Bike")
        ]

        # Insert dummy data
        try:
            self.cursor.executemany("""
                   INSERT OR IGNORE INTO clients (name, email, phone, rental_type) 
                   VALUES (?, ?, ?, ?)""", dummy_clients)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting dummy data: {e}")

    def is_valid_email(self, email):
        # Regular expression for email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None

    def is_phone_unique(self, phone):
        self.cursor.execute("SELECT COUNT(*) FROM clients WHERE phone = ?", (phone,))
        count = self.cursor.fetchone()[0]
        return count == 0

    def register_client(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        rental_type = self.rental_type.get()

        # Validate all fields are filled
        if not all([name, email, phone, rental_type]):
            messagebox.showerror("Error", "Voer alle velden in")
            return

        # Validate email format
        if not self.is_valid_email(email):
            messagebox.showerror("Error", "Vul een geldig email adres in")
            return

        # Check if phone is unique
        if not self.is_phone_unique(phone):
            messagebox.showerror("Error", "Dit nummer is al geregistreerd")
            return

        try:
            self.cursor.execute("INSERT INTO clients (name, email, phone, rental_type) VALUES (?, ?, ?, ?)",
                                (name, email, phone, rental_type))
            self.conn.commit()
            self.clear_form()
            self.update_client_list()
            messagebox.showinfo("Success", "Klant geregistreerd")
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Error", "Er is een fout opgetreden bij het registreren van de klant. Probeer opnieuw.")
            print(f"Database error: {e}")
        except Exception as e:
            messagebox.showerror("Error", "Er is een onverwachte fout opgetreden: ")
            print(f"Unexpected error: {e}")

    def update_client(self):
        # Get the client ID from the entry
        try:
            client_id = int(self.client_id_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Voer een geldig ID in: ")
            return

        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        rental_type = self.rental_type.get()

        # Validate all fields are filled
        if not all([name, email, phone, rental_type]):
            messagebox.showerror("Error", "Vul alle velden in.")
            return

        # Validate email format
        if not self.is_valid_email(email):
            messagebox.showerror("Error", "Vul een geldig email adres in.")
            return

        # Check if phone is unique (excluding current client)
        self.cursor.execute("SELECT COUNT(*) FROM clients WHERE phone = ? AND id != ?", (phone, client_id))
        count = self.cursor.fetchone()[0]
        if count > 0:
            messagebox.showerror("Error", "Dit nummer is al geregistreerd")
            return

        try:
            self.cursor.execute("""
                UPDATE clients 
                SET name = ?, email = ?, phone = ?, rental_type = ? 
                WHERE id = ?
            """, (name, email, phone, rental_type, client_id))

            # Check if any row was actually updated
            if self.cursor.rowcount == 0:
                messagebox.showerror("Error", "Geen klanten gevonden met dit ID")
                return

            self.conn.commit()
            self.clear_form()
            self.update_client_list()
            messagebox.showinfo("Success", "Klant geupdate!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Er is een fout opgetreden bij het updaten van de klant. {str(e)}")

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.rental_type.set("")

    def update_client_list(self):
        # Clear existing clients from scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Fetch clients from database
        self.cursor.execute("SELECT * FROM clients")
        clients = self.cursor.fetchall()

        # Add header
        header = tk.Label(self.scrollable_frame, text="Geregistreerde Klanten", font=("Arial", 16), bg="#f0f0f0")
        header.pack(pady=10)

        if not clients:
            tk.Label(self.scrollable_frame, text="Nog geen klanten geregistreerd",
                     bg="#f0f0f0", font=("Arial", 14)).pack(pady=20)
        else:
            for client in clients:
                client_frame = tk.Frame(self.scrollable_frame, bg="#ffffff", relief=tk.SOLID, borderwidth=1)
                client_frame.pack(fill=tk.X, padx=10, pady=5)

                labels = [
                    f"ID: {client[0]}",
                    f"Name: {client[1]}",
                    f"Email: {client[2]}",
                    f"Phone: {client[3]}",
                    f"Rental: {client[4]}"
                ]

                for text in labels:
                    label = tk.Label(client_frame, text=text, bg="#ffffff", font=("Arial", 12))
                    label.pack(side=tk.LEFT, padx=10, pady=5)

                remove_button = tk.Button(
                    client_frame,
                    text="Remove",
                    command=lambda cid=client[0]: self.remove_client(cid),
                    bg="#f44336",
                    fg="white",
                    font=("Arial", 10),
                    padx=5,
                    pady=2
                )
                remove_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Update the scroll region
        self.client_canvas.update_idletasks()
        self.client_canvas.configure(scrollregion=self.client_canvas.bbox("all"))

    def remove_client(self, client_id):
        if messagebox.askyesno("Confirm Removal", "Weet je zeker dat je deze klant wilt verwijderen?"):
            self.cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            self.conn.commit()
            self.update_client_list()
            messagebox.showinfo("Success", "Klant verwijderd.")



if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()