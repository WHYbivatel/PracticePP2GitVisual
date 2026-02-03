count = 1
while True:
    print(f"Count: {count}")
    if count == 5:
        break
    count += 1


number = 1
while number <= 100:
    print(f"Number: {number}")
    if number == 10:
        break
    number += 1


total = 0
i = 1
while i <= 20:
    total += i
    if total > 50:
        break
    i += 1
print(f"Total: {total}")


attempts = 0
while attempts < 10:
    password = input("Enter password: ")
    attempts += 1
    if password == "secret":
        print("Access granted")
        break
else:
    print("Too many attempts")



search = 1
while search <= 50:
    if search == 25:
        print(f"Found target: {search}")
        break
    search += 1