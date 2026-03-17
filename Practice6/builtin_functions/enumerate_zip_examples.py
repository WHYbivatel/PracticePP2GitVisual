# Example 1: enumerate list
for i, val in enumerate(['a', 'b', 'c']):
    print(i, val)

# Example 2: enumerate with start index
for i, val in enumerate(['x', 'y'], start=1):
    print(i, val)

# Example 3: zip two lists
names = ['Alice', 'Bob']
age = [25, 30]
print(list(zip(names, age)))

# Example 4: loop with zip
for n, a in zip(names, age):
    print(n, a)

# Example 5: unzip
pairs = [('a', 1), ('b', 2)]
letters, numbers = zip(*pairs)
print(letters, numbers)
