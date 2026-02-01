for i in range(1, 20):
    print(f"Number: {i}")
    if i == 5:
        break


fruits = ["apple", "banana", "cherry", "date", "elderberry"]
for fruit in fruits:
    print(f"Fruit: {fruit}")
    if fruit == "cherry":
        break


total = 0
for num in range(1, 99):
    total += num
    if total > 50:
        break
print(f"Total: {total}")


numbers = [5, 12, 8, 3, 15, 9]
for num in numbers:
    if num > 10:
        print(f"Found number greater than 10: {num}")
        break