from connect import get_connection


# ---------- CREATE TABLE ----------
def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100),
        phone VARCHAR(20) UNIQUE
    );
    """)

    conn.commit()
    cur.close()
    conn.close()


# ---------- CALL: insert/update ONE ----------
def call_insert_or_update_user(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL insert_or_update_user(%s, %s);", (name, phone))

    conn.commit()
    cur.close()
    conn.close()

    print("User inserted/updated.\n")


# ---------- CALL: insert MANY (bulk) ----------
def call_insert_many_users():
    print("Enter multiple users (type 'stop' to finish):")

    names = []
    phones = []

    while True:
        name = input("Name: ").strip()
        if name.lower() == "stop":
            break

        phone = input("Phone: ").strip()

        names.append(name)
        phones.append(phone)

    conn = get_connection()
    cur = conn.cursor()

    # вызываем процедуру
    cur.execute("CALL insert_many_users(%s, %s, NULL);", (names, phones))

    conn.commit()
    cur.close()
    conn.close()

    print("Bulk insert completed.\n")


# ---------- SEARCH (function) ----------
def search_by_pattern(pattern):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
    rows = cur.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No results.")

    print()
    cur.close()
    conn.close()


# ---------- PAGINATION ----------
def get_paginated():
    limit_count = int(input("Enter LIMIT: "))
    offset_count = int(input("Enter OFFSET: "))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM get_contacts_paginated(%s, %s);",
        (limit_count, offset_count)
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    print()
    cur.close()
    conn.close()


# ---------- DELETE ----------
def call_delete_user():
    value = input("Enter username or phone: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL delete_user(%s);", (value,))

    conn.commit()
    cur.close()
    conn.close()

    print("Deleted if existed.\n")


# ---------- MENU ----------
def menu():
    while True:
        print("=== PHONEBOOK MENU ===")
        print("1. Insert or update ONE user")
        print("2. Insert MANY users (bulk)")
        print("3. Search by pattern")
        print("4. Show paginated data")
        print("5. Delete user")
        print("6. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            name = input("Enter name: ").strip()
            phone = input("Enter phone: ").strip()
            call_insert_or_update_user(name, phone)

        elif choice == "2":
            call_insert_many_users()

        elif choice == "3":
            pattern = input("Enter pattern: ").strip()
            search_by_pattern(pattern)

        elif choice == "4":
            get_paginated()

        elif choice == "5":
            call_delete_user()

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid option\n")


# ---------- MAIN ----------
if __name__ == "__main__":
    create_table()
    menu()