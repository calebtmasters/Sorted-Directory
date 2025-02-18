#!/usr/bin/env python3
import sqlite3
import os

class ContactDatabase:
    def __init__(self, db_name="Directory.db", text_file="Directory.txt"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(script_dir, "Db_Files", db_name)
        self.txt_file = os.path.join(script_dir, "Text_Files", text_file)

        db_dir = os.path.dirname(self.db_name)
        if not os.path.exists(db_dir):
            print(f"Warning: The directroy for the database does not exist. Creating {db_dir}")
            os.makedirs(db_dir)
        else: 
            print(f'Database Directory Already Exists: {db_dir}")')

        text_dir = os.path.dirname(self.txt_file)
        if not os.path.exists(text_dir):
            print(f"Warning: The directory for the text file does not exist. Creating {text_dir}")
            os.makedirs(text_dir)
        else:
            print(f'Text Files Directory already exists: {text_dir}")')

        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.create_table()
            self.update_text_file()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            exit(1)

    def create_table(self):
        """Create contacts table if it doesn't exist."""
        try:
            self.cursor.execute("""
                create table if not exists contacts (
                    id integer primary key autoincrement,
                    name text unique,
                    phone text
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            exit(1)

    def add_contact(self, name, phone):
        """Add a new contact (name must be unique)."""
        try:
            self.cursor.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
            self.conn.commit()
            self.update_text_file()
            print(f"Added: {name} - {phone}")
        except sqlite3.IntegrityError:
            print(f"Error: The name '{name}' already exists.")
        except sqlite3.Error as e:
            print(f"Database error while adding contact: {e}")

    def remove_contact(self, name):
        """Remove a contact by name."""
        try:
            self.cursor.execute("DELETE FROM contacts WHERE name = ?", (name,))
            if self.cursor.rowcount > 0:
                print(f" Removed: {name}")
            else:
                print(f" Error: Name '{name}' not found.")
            self.conn.commit()
            self.update_text_file()
        except sqlite3.Error as e:
            print(f"Database error while removing contact: {e}")

    def show_contacts(self):
        """Display all stored contacts."""
        try:
            self.cursor.execute("SELECT name, phone FROM contacts ORDER BY "
                                "substr(name, instr(name, ' ') + 1) ASC, name ASC")
            contacts = self.cursor.fetchall()
            if contacts:
                print("\nContact List (sorted by Last Name and then First Name):")
                for name, phone in contacts:
                    print(f"{name}: {phone}")
            else:
                print("No contacts found.")
        except sqlite3.Error as e:
            print(f"Database error while displaying contacts: {e}")

    def reset_database(self):
        """Delete all contacts and reset the database."""
        try:
            self.cursor.execute("DROP TABLE IF EXISTS contacts")
            self.create_table()
            self.update_text_file()
            print("Database has been reset.")
        except sqlite3.Error as e:
            print(f"Database error while resetting: {e}")

    def update_text_file(self):
        try:
            self.cursor.execute("SELECT name, phone FROM contacts")
            contacts = self.cursor.fetchall()

            with open(self.txt_file, "w") as f:
                for name, phone in contacts:
                    f.write(f"{name}: {phone}\n")
        except sqlite3.Error as e:
            print(f"Database error while updating text file: {e}")

    def close(self):
        """Close the database connection."""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(f"Error closing database: {e}")


# Interactive menu to use the database
if __name__ == "__main__":
    db = ContactDatabase()

    while True:
        print("\nOptions: add, remove, show, reset, exit")
        choice = input("Choose an option: ").strip().lower()

        if choice == "add":
            name = input("Enter name: ").strip()
            phone = input("Enter phone number: ").strip()
            db.add_contact(name, phone)
        elif choice == "remove":
            name = input("Enter name to remove: ").strip()
            db.remove_contact(name)
        elif choice == "show":
            db.show_contacts()
        elif choice == "reset":
            db.reset_database()
        elif choice == "exit":
            db.close()
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")

