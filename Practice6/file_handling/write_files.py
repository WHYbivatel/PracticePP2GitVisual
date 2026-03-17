# Example 1: Write to file (overwrite)
with open('output.txt', 'w') as f:
    f.write("Hello World\n")

# Example 2: Append to file
with open('output.txt', 'a') as f:
    f.write("Append this line\n")

# Example 3: Write multiple lines
lines = ['Line1\n', 'Line2\n']
with open('output.txt', 'w') as f:
    f.writelines(lines)

# Example 4: Write using print
with open('output.txt', 'w') as f:
    print("Hello via print", file=f)

# Example 5: Write numbers
with open('numbers.txt', 'w') as f:
    for i in range(5):
        f.write(str(i) + '\n')
