count = 0
while count < 10:
    count += 1
    if count % 2 == 0:
        continue
    print(f"Odd number: {count}")


number = 0
while number < 20:
    number += 1
    if number % 3 == 0:
        continue
    print(f"Not divisible by 3: {number}")


i = 0
while i < 15:
    i += 1
    if i == 5 or i == 10:
        continue
    print(f"Number: {i}")


total = 0
count = 0
while count < 10:
    count += 1
    if count == 7:
        continue
    total += count
print(f"Total (skipping 7): {total}")