# Example 1: Read entire file
with open('example.txt', 'r') as f:
    content = f.read()
    print(content)

# Example 2: Read line by line
with open('example.txt', 'r') as f:
    for line in f:
        print(line.strip())

# Example 3: Read first N characters
with open('example.txt', 'r') as f:
    print(f.read(10))

# Example 4: Read all lines into list
with open('example.txt', 'r') as f:
    lines = f.readlines()
    print(lines)

# Example 5: Safe read with try-except
try:
    with open('example.txt', 'r') as f:
        print(f.read())
except FileNotFoundError:
    print("File not found")