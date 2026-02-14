words = ["apple", "banana", "kiwi", "pear"]

print(sorted(words, key=lambda x: len(x)))


print(sorted(words, key=lambda x: x[0]))


print(sorted(words, key=lambda x: x[-1]))


print(sorted(words, key=lambda x: x.lower()))



numbers = [-5, 3, -2, 8]
print(sorted(numbers, key=lambda x: abs(x)))
