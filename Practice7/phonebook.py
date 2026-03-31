import csv
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


# ---------- INSERT FROM CSV ----------
def insert_from_csv(file_path):
    conn = get_connection()
    cur = conn.cursor()

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 2:
                continue
            name, phone = row
            cur.execute(
                """
                INSERT INTO contacts (first_name, phone)
                VALUES (%s, %s)
                ON CONFLICT (phone) DO NOTHING
                """,
                (name, phone)
            )

    conn.commit()
    cur.close()
    conn.close()


# ---------- INSERT FROM CONSOLE (UPDATED) ----------
def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO contacts (first_name, phone)
        VALUES (%s, %s)
        ON CONFLICT (phone)
        DO UPDATE SET first_name = EXCLUDED.first_name
        """,
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Contact added or updated successfully.")


# ---------- UPDATE ----------
def update_contact(old_phone, new_name=None, new_phone=None):
    conn = get_connection()
    cur = conn.cursor()

    if new_name:
        cur.execute(
            "UPDATE contacts SET first_name=%s WHERE phone=%s",
            (new_name, old_phone)
        )

    if new_phone:
        cur.execute(
            "UPDATE contacts SET phone=%s WHERE phone=%s",
            (new_phone, old_phone)
        )

    conn.commit()
    cur.close()
    conn.close()


# ---------- QUERY ----------
def search_contacts(name=None, phone_prefix=None):
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM contacts WHERE TRUE"
    params = []

    if name:
        query += " AND first_name ILIKE %s"
        params.append(f"%{name}%")

    if phone_prefix:
        query += " AND phone LIKE %s"
        params.append(f"{phone_prefix}%")

    cur.execute(query, params)
    results = cur.fetchall()

    for row in results:
        print(row)

    cur.close()
    conn.close()


# ---------- DELETE ----------
def delete_contact(name=None, phone=None):
    conn = get_connection()
    cur = conn.cursor()

    if name:
        cur.execute("DELETE FROM contacts WHERE first_name=%s", (name,))
    elif phone:
        cur.execute("DELETE FROM contacts WHERE phone=%s", (phone,))

    conn.commit()
    cur.close()
    conn.close()


# ---------- MAIN ----------
if __name__ == "__main__":
    print("Program started")

    create_table()
    insert_from_csv("contacts.csv")
    insert_from_console()

    print("\nSearch by name:")
    search_contacts(name="Ali")

    print("\nSearch by prefix:")
    search_contacts(phone_prefix="123")

    update_contact("123456", new_name="Updated Name")
    delete_contact(phone="987654")