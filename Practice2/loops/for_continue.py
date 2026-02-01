for i in range(1, 11):
    if i % 2 == 0:
        continue
    print(f"Odd number: {i}")


fruits = ["apple", "banana", "cherry", "date"]
for fruit in fruits:
    if fruit == "banana":
        continue
    print(f"Fruit: {fruit}")


total = 0
for num in range(1, 21):
    if num % 3 == 0:
        continue
    total += num
print(f"Total (excluding multiples of 3): {total}")


numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for num in numbers:
    if num == 5 or num == 7:
        continue
    print(f"Number: {num}")