def square_generator(N):
    for i in range(N + 1):
        yield i * i

# Example usage
for value in square_generator(5):
    print(value)





def even_numbers(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

# Input from console
n = int(input("Enter a number: "))

print(",".join(str(num) for num in even_numbers(n)))





def divisible_by_3_and_4(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

# Example usage
n = int(input("Enter a number: "))
for num in divisible_by_3_and_4(n):
    print(num)






def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

# Test with for loop
for value in squares(3, 7):
    print(value)






def countdown(n):
    while n >= 0:
        yield n
        n -= 1

# Example usage
for num in countdown(5):
    print(num)