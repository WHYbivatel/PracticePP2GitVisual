count = 1
while count <= 5:
    print(f"Count: {count}")
    count += 1


number = 10
while number > 0:
    print(f"Number: {number}")
    number -= 2


total = 0
i = 1
while i <= 10:
    total += i
    i += 1
print(f"Total: {total}")


password = ""
while password != "secret":
    password = input("Enter password: ")
print("Access granted")


counter = 5
while counter >= 1:
    print(f"Countdown: {counter}")
    counter -= 1