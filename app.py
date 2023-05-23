import mysql.connector
import qrcode
from datetime import datetime
import tkinter as tk

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="fare_payment_system"
)

# Create the necessary tables if they don't exist
cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        UserID INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(255),
        Email VARCHAR(255),
        Phone VARCHAR(20),
        PaymentMethod VARCHAR(50),
        Balance DECIMAL(10, 2)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS fares (
        FareID INT AUTO_INCREMENT PRIMARY KEY,
        UserID INT,
        FareAmount DECIMAL(10, 2),
        PaymentStatus BOOLEAN,
        Timestamp DATETIME,
        FOREIGN KEY (UserID) REFERENCES users(UserID)
    )
""")
db.commit()


def register_user(name, email, phone, payment_method):
    # Register a new user
    balance = 0.0
    cursor.execute("""
        INSERT INTO users (Name, Email, Phone, PaymentMethod, Balance)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, email, phone, payment_method, balance))
    db.commit()
    print("User registered successfully.")


def generate_fare(user_id, fare_amount):
    # Generate a fare transaction and QR code
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payment_status = False

    cursor.execute("""
        INSERT INTO fares (UserID, FareAmount, PaymentStatus, Timestamp)
        VALUES (%s, %s, %s, %s)
    """, (user_id, fare_amount, payment_status, timestamp))
    db.commit()

    fare_id = cursor.lastrowid

    qr_data = f"FARE:{fare_id};USER:{user_id};AMOUNT:{fare_amount}"
    qr_code = qrcode.make(qr_data)
    qr_code.save(f"fare_{fare_id}.png")

    print("Fare generated successfully.")
    print("QR code saved as fare_{fare_id}.png")


def scan_qr_code(qr_data):
    # Scan and process the fare QR code
    fare_id = qr_data.split(";")[0].split(":")[1]
    user_id = qr_data.split(";")[1].split(":")[1]
    fare_amount = float(qr_data.split(";")[2].split(":")[1])

    cursor.execute("""
        SELECT * FROM fares WHERE FareID = %s
    """, (fare_id,))
    fare = cursor.fetchone()

    if fare is None:
        print("Invalid QR code.")
    elif fare[3] == True:
        print("Payment already completed.")
    elif fare[1] != int(user_id) or fare[2] != fare_amount:
        print("QR code does not match fare details.")
    else:
        cursor.execute("""
            UPDATE fares SET PaymentStatus = %s WHERE FareID = %s
        """, (True, fare_id))
        db.commit()
        print("Payment successful.")


def register_user_gui():
    # Register user GUI
    def register():
        name = name_entry.get()
        email = email_entry.get()
        phone = phone_entry.get()
        payment_method = payment_entry.get()
        register_user(name, email, phone, payment_method)
        register_window.destroy()

    register_window = tk.Toplevel()
    register_window.title("Register User")

    label = tk.Label(register_window, text="Register User", font=("Arial", 16, "bold"))
    label.grid(row=0, column=0, columnspan=2, pady=10)

    name_label = tk.Label(register_window, text="Name:")
    name_label.grid(row=1, column=0, sticky="E")
    name_entry = tk.Entry(register_window)
    name_entry.grid(row=1, column=1)

    email_label = tk.Label(register_window, text="Email:")
    email_label.grid(row=2, column=0, sticky="E")
    email_entry = tk.Entry(register_window)
    email_entry.grid(row=2, column=1)

    phone_label = tk.Label(register_window, text="Phone:")
    phone_label.grid(row=3, column=0, sticky="E")
    phone_entry = tk.Entry(register_window)
    phone_entry.grid(row=3, column=1)

    payment_label = tk.Label(register_window, text="Payment Method:")
    payment_label.grid(row=4, column=0, sticky="E")
    payment_entry = tk.Entry(register_window)
    payment_entry.grid(row=4, column=1)

    register_button = tk.Button(register_window, text="Register", command=register)
    register_button.grid(row=5, columnspan=2, pady=10)


def generate_fare_gui():
    # Generate fare GUI
    def generate():
        user_id = user_id_entry.get()
        fare_amount = float(fare_amount_entry.get())
        generate_fare(user_id, fare_amount)
        generate_window.destroy()

    generate_window = tk.Toplevel()
    generate_window.title("Generate Fare")

    label = tk.Label(generate_window, text="Generate Fare", font=("Arial", 16, "bold"))
    label.grid(row=0, column=0, columnspan=2, pady=10)

    user_id_label = tk.Label(generate_window, text="User ID:")
    user_id_label.grid(row=1, column=0, sticky="E")
    user_id_entry = tk.Entry(generate_window)
    user_id_entry.grid(row=1, column=1)

    fare_amount_label = tk.Label(generate_window, text="Fare Amount:")
    fare_amount_label.grid(row=2, column=0, sticky="E")
    fare_amount_entry = tk.Entry(generate_window)
    fare_amount_entry.grid(row=2, column=1)

    generate_button = tk.Button(generate_window, text="Generate", command=generate)
    generate_button.grid(row=3, columnspan=2, pady=10)


def scan_qr_code_gui():
    # Scan QR code GUI
    def scan():
        qr_data = qr_entry.get()
        scan_qr_code(qr_data)
        scan_window.destroy()

    scan_window = tk.Toplevel()
    scan_window.title("Scan QR Code")

    label = tk.Label(scan_window, text="Scan QR Code", font=("Arial", 16, "bold"))
    label.grid(row=0, column=0, columnspan=2, pady=10)

    qr_label = tk.Label(scan_window, text="QR Code:")
    qr_label.grid(row=1, column=0, sticky="E")
    qr_entry = tk.Entry(scan_window)
    qr_entry.grid(row=1, column=1)

    scan_button = tk.Button(scan_window, text="Scan", command=scan)
    scan_button.grid(row=2, columnspan=2, pady=10)


def main():
    root = tk.Tk()
    root.title("QR Code Fare Payment System")

    label = tk.Label(root, text="QR Code Fare Payment System", font=("Arial", 18, "bold"))
    label.pack(pady=20)

    register_button = tk.Button(root, text="Register User", command=register_user_gui)
    register_button.pack(pady=10)

    generate_button = tk.Button(root, text="Generate Fare", command=generate_fare_gui)
    generate_button.pack(pady=10)

    scan_button = tk.Button(root, text="Scan QR Code", command=scan_qr_code_gui)
    scan_button.pack(pady=10)

    exit_button = tk.Button(root, text="Exit", command=root.quit)
    exit_button.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
