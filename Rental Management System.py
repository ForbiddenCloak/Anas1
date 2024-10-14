import mysql.connector

# Establish connection to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="abc123"
)

cursor = db.cursor(buffered=True)

# Create and use the database
cursor.execute("CREATE DATABASE IF NOT EXISTS management")
cursor.execute("USE management")

# Removed table drops to preserve data
# cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
# cursor.execute("DROP TABLE IF EXISTS vehicles")
# cursor.execute("DROP TABLE IF EXISTS customers")
# cursor.execute("DROP TABLE IF EXISTS rentals")
# cursor.execute("DROP TABLE IF EXISTS rental_history")
# cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# Create tables if they do not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(255),
    category VARCHAR(255),
    availability VARCHAR(50),
    rate_3_hours FLOAT(10, 2),
    rate_6_hours FLOAT(10, 2),
    rate_12_hours FLOAT(10, 2),
    rate_24_hours FLOAT(10, 2),
    status VARCHAR(50) DEFAULT 'Available'
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    phone VARCHAR(255),
    rented_vehicles VARCHAR(500),
    rental_count INT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS rentals (
    rental_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    vehicle_id INT,
    duration_hours INT,
    total_price FLOAT(10, 2),
    actual_return_time VARCHAR(255),
    late_fee FLOAT(10, 2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS rental_history (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    vehicle_model VARCHAR(255),
    rental_start_time VARCHAR(255),
    rental_end_time VARCHAR(255),
    total_price FLOAT(10, 2),
    late_fee FLOAT(10, 2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
''')

# Sample vehicles
vehicles = [
    ('Access', 'Scooty', 'Available', 250, 350, 450, 550),
    ('Fascino', 'Scooty', 'Available', 250, 350, 450, 550),
    ('Grazia', 'Scooty', 'Available', 250, 350, 450, 550),
    ('Ntorq', 'Scooty', 'Available', 300, 450, 600, 700),
    ('Avenis', 'Scooty', 'Available', 300, 450, 600, 700),
    ('Ray ZR', 'Scooty', 'Available', 300, 450, 600, 700),
    ('Burgmann Street', 'Scooty', 'Available', 350, 500, 700, 800),
    ('Hunter 350', 'Bike', 'Available', 500, 800, 1100, 1300),
    ('Ronin 200', 'Bike', 'Available', 500, 800, 1100, 1300)
]

# Insert sample vehicles only if the table is empty
cursor.execute("SELECT COUNT(*) FROM vehicles")
vehicle_count = cursor.fetchone()[0]

if vehicle_count == 0:
    # Insert sample vehicles
    cursor.executemany('''
    INSERT INTO vehicles (model, category, availability, rate_3_hours, rate_6_hours, rate_12_hours, rate_24_hours, status) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, "Available")
    ''', vehicles)
    db.commit()
    print("Sample vehicles inserted into the database.")
else:
    print("Vehicles already exist in the database. Skipping sample data insertion.")

def main_menu():
    print("\n1. Login as Customer")
    print("2. Create New Customer")
    print("3. Login as Admin")
    print("4. Exit")
    choice = input("Choose an option: ")
    if choice == '1':
        customer_login()
    elif choice == '2':
        create_customer()
    elif choice == '3':
        admin_login()
    elif choice == '4':
        print("Exiting the program. Goodbye!")
        exit()
    else:
        print("Invalid option.")
        main_menu()

def customer_login():
    phone = input("Enter phone number: ")
    
    cursor.execute("SELECT * FROM customers WHERE phone=%s", (phone,))
    customer = cursor.fetchone()
    
    if customer and customer[2] == phone:
        print("Welcome, " + customer[1] + "!")
        customer_menu(customer)
    else:
        print("Customer not found.")
        main_menu()

def create_customer():
    name = input("Enter your name: ")
    phone = input("Enter your phone number: ")
    cursor.execute("INSERT INTO customers (name, phone, rented_vehicles, rental_count) VALUES (%s, %s, '[]', 0)", (name, phone))
    db.commit()
    print("Customer created successfully!")
    main_menu()

def customer_menu(customer):
    customer_id = customer[0]
    while True:
        print("\nCustomer Menu:")
        print("1. Rent Vehicle")
        print("2. Return Vehicle")
        print("3. View Rented Vehicles")
        print("4. View Rental History")
        print("5. Logout")
        print("6. Exit")
        choice = input("Choose an option: ")
        
        if choice == '1':
            rent_vehicle(customer_id)
        elif choice == '2':
            return_vehicle(customer_id)
        elif choice == '3':
            view_rented_vehicles(customer_id)
        elif choice == '4':
            view_rental_history(customer_id)
        elif choice == '5':
            print("Logging out...")
            main_menu()
        elif choice == '6':
            print("Exiting the program. Goodbye!")
            exit()
        else:
            print("Invalid option. Please try again.")

def display_available_vehicles():
    cursor.execute("SELECT model, category, rate_3_hours, rate_6_hours, rate_12_hours, rate_24_hours FROM vehicles WHERE status='Available'")
    vehicles = cursor.fetchall()

    if vehicles:
        print("\n--- Available Vehicles ---")
        print('Model' + ' ' * 5 + 'Category' + ' ' * 2 + 'Rate (3h)' + ' ' * 2 + 'Rate (6h)' + ' ' * 2 + 'Rate (12h)' + ' ' * 2 + 'Rate (24h)')
        print("-" * 80)

        for vehicle in vehicles:
            model, category, rate_3h, rate_6h, rate_12h, rate_24h = vehicle
            print(
                model + ' ' * (20 - len(model)) +
                category + ' ' * (15 - len(category)) +
                '₹' + str(rate_3h).rjust(11) +
                '₹' + str(rate_6h).rjust(11) +
                '₹' + str(rate_12h).rjust(11) +
                '₹' + str(rate_24h).rjust(11)
            )

        print("-" * 80)
    else:
        print("No vehicles are available at the moment.")


def rent_vehicle(customer_id):
    display_available_vehicles()

    model = input("Enter the model of the vehicle you want to rent: ").capitalize()

    cursor.execute("SELECT * FROM vehicles WHERE model=%s AND status='Available'", (model,))
    vehicle = cursor.fetchone()

    if vehicle:
        try:
            duration_hours = int(input("Enter rental duration in hours (3, 6, 12, or 24): "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        if duration_hours not in [3, 6, 12, 24]:
            print("Invalid duration.")
            return

        rate_column_index = {3: 4, 6: 5, 12: 6, 24: 7}[duration_hours]
        total_price = vehicle[rate_column_index]

        cursor.execute('''INSERT INTO rentals (customer_id, vehicle_id, duration_hours, total_price)
                          VALUES (%s, %s, %s, %s)''', (customer_id, vehicle[0], duration_hours, total_price))
        cursor.execute("UPDATE vehicles SET status='Rented' WHERE vehicle_id=%s", (vehicle[0],))
        db.commit()

        print(model + " rented successfully for " + str(duration_hours) + " hours at ₹" + str(total_price) + ".")
    else:
        print("Vehicle is not available.")


def return_vehicle(customer_id):
    cursor.execute("SELECT * FROM rentals WHERE customer_id=%s AND actual_return_time IS NULL", (customer_id,))
    rentals = cursor.fetchall()

    if not rentals:
        print("No active rentals found.")
        return

    print("\n--- Your Active Rentals ---")
    rentals_list = []
    rental_index = 1  
    for rental in rentals:
        cursor.execute("SELECT model FROM vehicles WHERE vehicle_id=%s", (rental[2],))
        vehicle_model = cursor.fetchone()[0]
        rentals_list.append(rental)
        print(
            str(rental_index) + ". Rental ID: " + str(rental[0]) + 
            ", Vehicle: " + vehicle_model + 
            ", Duration: " + str(rental[3]) + " hours, Total Price: ₹" + str(rental[4])
        )
        rental_index += 1  

    selected_idx = input("Enter the number of the rental you want to return: ")
    try:
        selected_idx = int(selected_idx)
        if 1 <= selected_idx <= len(rentals_list):
            rental = rentals_list[selected_idx - 1]
        else:
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return

    try:
        late_fee = float(input("Enter any late fee to be applied: "))
    except ValueError:
        print("Invalid input for late fee.")
        return

    cursor.execute('''UPDATE rentals SET actual_return_time=%s, late_fee=%s WHERE rental_id=%s''',
                   ('N/A', late_fee, rental[0]))
    cursor.execute("UPDATE vehicles SET status='Available' WHERE vehicle_id=%s", (rental[2],))

    cursor.execute("SELECT model FROM vehicles WHERE vehicle_id=%s", (rental[2],))
    vehicle_model = cursor.fetchone()[0]

    cursor.execute('''INSERT INTO rental_history (customer_id, vehicle_model, rental_start_time, rental_end_time, total_price, late_fee)
                      VALUES (%s, %s, %s, %s, %s, %s)''', (customer_id, vehicle_model, 'N/A', 'N/A', rental[4], late_fee))

    db.commit()
    
    print("Vehicle returned. Late fee: ₹" + str(late_fee))


def view_rented_vehicles(customer_id):
    cursor.execute("SELECT * FROM rentals WHERE customer_id=%s AND actual_return_time IS NULL", (customer_id,))
    rentals = cursor.fetchall()

    if rentals:
        print("\n--- Your Active Rentals ---")
        for rental in rentals:
            cursor.execute("SELECT model FROM vehicles WHERE vehicle_id=%s", (rental[2],))
            vehicle_model = cursor.fetchone()[0]
            print(
                "Rental ID: " + str(rental[0]) + 
                ", Vehicle: " + vehicle_model + 
                ", Duration: " + str(rental[3]) + " hours, Total Price: ₹" + str(rental[4])
            )
    else:
        print("No active rentals found.")


def view_rental_history(customer_id):
    cursor.execute("SELECT * FROM rental_history WHERE customer_id=%s", (customer_id,))
    history = cursor.fetchall()

    if history:
        print("\n--- Your Rental History ---")
        for record in history:
            print(
                "Vehicle: " + record[2] + 
                ", Total Price: ₹" + str(record[5]) + 
                ", Late Fee: ₹" + str(record[6])
            )
    else:
        print("No rental history found.")


def admin_login():
    admin_password = input("Enter admin password: ")
    if admin_password == "admin123":
        admin_menu()
    else:
        print("Invalid password.")
        main_menu()

def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. View All Customers")
        print("2. View All Vehicles")
        print("3. Manage Vehicle Maintenance")
        print("4. Logout")
        print("5. Exit")
        choice = input("Choose an option: ")
        
        if choice == '1':
            view_all_customers()
        elif choice == '2':
            view_all_vehicles()
        elif choice == '3':
            manage_vehicle_maintenance()
        elif choice == '4':
            print("Logging out...")
            main_menu()
        elif choice == '5':
            print("Exiting the program. Goodbye!")
            exit()
        else:
            print("Invalid option.")

def manage_vehicle_maintenance():
    cursor.execute("SELECT * FROM vehicles WHERE status='Available' OR status='Maintenance'")
    vehicles = cursor.fetchall()

    if vehicles:
        print("\n--- Vehicles for Maintenance Management ---")
        for vehicle in vehicles:
            print("Vehicle ID: " + str(vehicle[0]) + 
                  ", Model: " + vehicle[1] + 
                  ", Status: " + vehicle[8])

        vehicle_id = input("Enter the ID of the vehicle you want to change the status of: ")
        new_status = input("Enter the new status (Available/Maintenance): ")

        if new_status not in ['Available', 'Maintenance']:
            print("Invalid status.")
            return

        cursor.execute("UPDATE vehicles SET status=%s WHERE vehicle_id=%s", (new_status, vehicle_id))
        db.commit()
        print("Vehicle status updated.")
    else:
        print("No vehicles available for maintenance management.")


def view_all_customers():
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    if customers:
        print("\n--- All Customers ---")
        for customer in customers:
            print("Customer ID: " + str(customer[0]) + 
                  ", Name: " + customer[1] + 
                  ", Phone: " + customer[2])
    else:
        print("No customers found.")

def view_all_vehicles():
    cursor.execute("SELECT * FROM vehicles")
    vehicles = cursor.fetchall()
    if vehicles:
        print("\n--- All Vehicles ---")
        for vehicle in vehicles:
            print("Vehicle ID: " + str(vehicle[0]) + 
                  ", Model: " + vehicle[1] + 
                  ", Category: " + vehicle[2] + 
                  ", Status: " + vehicle[8])
    else:
        print("No vehicles found.")


print("Welcome to Two-Wheeler Rental Manager")
main_menu()

# Close the connection when the program exits
cursor.close()
db.close()
