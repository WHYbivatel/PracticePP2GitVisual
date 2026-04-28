import csv
import json
from connect import get_connection


def print_rows(rows):
    if not rows:
        print("No results.\n")
        return

    for row in rows:
        print(row)
    print()


def add_contact():
    name = input("Name: ").strip()
    surname = input("Surname: ").strip()
    email = input("Email: ").strip()
    birthday = input("Birthday YYYY-MM-DD: ").strip()
    group = input("Group Family/Work/Friend/Other: ").strip()
    phone = input("Phone: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "CALL insert_or_update_user(%s, %s, %s, %s, %s, %s);",
        (name, surname, email, phone, birthday, group)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Contact inserted/updated.\n")


def add_phone():
    name = input("Contact name: ").strip()
    phone = input("New phone: ").strip()
    phone_type = input("Type home/work/mobile: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL add_phone(%s, %s, %s);", (name, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()

    print("Phone added.\n")


def move_to_group():
    name = input("Contact name: ").strip()
    group = input("New group: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL move_to_group(%s, %s);", (name, group))

    conn.commit()
    cur.close()
    conn.close()

    print("Contact moved.\n")


def search_contacts():
    query = input("Search query: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s);", (query,))
    rows = cur.fetchall()

    print_rows(rows)

    cur.close()
    conn.close()


def search_by_email():
    email = input("Email search: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.first_name, c.surname, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE c.email ILIKE %s
        ORDER BY c.id;
    """, (f"%{email}%",))

    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()


def filter_by_group():
    group = input("Group name: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.first_name, c.surname, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE g.name ILIKE %s
        ORDER BY c.id;
    """, (group,))

    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()


def sort_contacts():
    print("1. Sort by name")
    print("2. Sort by birthday")
    print("3. Sort by date added")
    choice = input("Choose: ").strip()

    if choice == "1":
        order_by = "first_name"
    elif choice == "2":
        order_by = "birthday"
    elif choice == "3":
        order_by = "created_at"
    else:
        print("Invalid option.\n")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        SELECT c.id, c.first_name, c.surname, c.email, c.birthday, c.created_at, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.{order_by} NULLS LAST;
    """)

    rows = cur.fetchall()
    print_rows(rows)

    cur.close()
    conn.close()


def paginated_navigation():
    limit_count = int(input("Page size: "))
    offset = 0

    while True:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM get_contacts_paginated(%s, %s);",
            (limit_count, offset)
        )

        rows = cur.fetchall()
        print_rows(rows)

        cur.close()
        conn.close()

        command = input("next / prev / quit: ").strip().lower()

        if command == "next":
            offset += limit_count
        elif command == "prev":
            offset = max(0, offset - limit_count)
        elif command == "quit":
            break
        else:
            print("Invalid command.\n")


def delete_contact():
    value = input("Delete by name/surname/phone/email: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM contacts
        WHERE first_name = %s
           OR surname = %s
           OR email = %s
           OR id IN (
               SELECT contact_id FROM phones WHERE phone = %s
           );
    """, (value, value, value, value))

    conn.commit()
    cur.close()
    conn.close()

    print("Deleted if existed.\n")


def export_to_json():
    filename = input("JSON filename to export: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.first_name, c.surname, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.id;
    """)

    contacts = cur.fetchall()

    data = []

    for contact in contacts:
        contact_id, name, surname, email, birthday, group_name = contact

        cur.execute("""
            SELECT phone, type
            FROM phones
            WHERE contact_id = %s;
        """, (contact_id,))

        phones = cur.fetchall()

        data.append({
            "name": name,
            "surname": surname,
            "email": email,
            "birthday": str(birthday) if birthday else None,
            "group": group_name,
            "phones": [
                {"phone": phone, "type": phone_type}
                for phone, phone_type in phones
            ]
        })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    cur.close()
    conn.close()

    print("Export completed.\n")


def import_from_json():
    filename = input("JSON filename to import: ").strip()

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = get_connection()
    cur = conn.cursor()

    for item in data:
        name = item.get("name")
        surname = item.get("surname")
        email = item.get("email")
        birthday = item.get("birthday")
        group = item.get("group") or "Other"
        phones = item.get("phones", [])

        cur.execute("""
            SELECT id FROM contacts
            WHERE first_name = %s AND surname = %s;
        """, (name, surname))

        existing = cur.fetchone()

        if existing:
            action = input(f"{name} {surname} exists. skip/overwrite: ").strip().lower()

            if action == "skip":
                continue

        main_phone = phones[0]["phone"] if phones else None

        cur.execute(
            "CALL insert_or_update_user(%s, %s, %s, %s, %s, %s);",
            (name, surname, email, main_phone, birthday, group)
        )

        cur.execute("""
            SELECT id FROM contacts
            WHERE first_name = %s AND surname = %s;
        """, (name, surname))

        contact_id = cur.fetchone()[0]

        for phone_obj in phones:
            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s, %s, %s);
            """, (
                contact_id,
                phone_obj.get("phone"),
                phone_obj.get("type", "mobile")
            ))

    conn.commit()
    cur.close()
    conn.close()

    print("Import completed.\n")


def import_from_csv():
    filename = input("CSV filename: ").strip()

    conn = get_connection()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        for row in reader:
            if len(row) != 7:
                continue

            name, surname, email, birthday, group, phone, phone_type = row

            cur.execute(
                "CALL insert_or_update_user(%s, %s, %s, %s, %s, %s);",
                (name, surname, email, phone, birthday, group)
            )

            cur.execute("CALL add_phone(%s, %s, %s);", (name, phone, phone_type))

    conn.commit()
    cur.close()
    conn.close()

    print("CSV import completed.\n")


def menu():
    while True:
        print("=== PHONEBOOK MENU ===")
        print("1. Add/update contact")
        print("2. Add phone")
        print("3. Move contact to group")
        print("4. Search contacts")
        print("5. Search by email")
        print("6. Filter by group")
        print("7. Sort contacts")
        print("8. Paginated navigation")
        print("9. Delete contact")
        print("10. Export to JSON")
        print("11. Import from JSON")
        print("12. Import from CSV")
        print("13. Exit")

        choice = input("Choose option: ").strip()

        if choice == "1":
            add_contact()
        elif choice == "2":
            add_phone()
        elif choice == "3":
            move_to_group()
        elif choice == "4":
            search_contacts()
        elif choice == "5":
            search_by_email()
        elif choice == "6":
            filter_by_group()
        elif choice == "7":
            sort_contacts()
        elif choice == "8":
            paginated_navigation()
        elif choice == "9":
            delete_contact()
        elif choice == "10":
            export_to_json()
        elif choice == "11":
            import_from_json()
        elif choice == "12":
            import_from_csv()
        elif choice == "13":
            print("Goodbye!")
            break
        else:
            print("Invalid option.\n")


if __name__ == "__main__":
    menu()