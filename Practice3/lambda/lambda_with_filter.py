nums = [1, 2, 3, 4, 5, 6]

print(list(filter(lambda x: x % 2 == 0, nums)))


print(list(filter(lambda x: x > 3, nums)))


print(list(filter(lambda x: x < 5, nums)))


print(list(filter(lambda x: x != 2, nums)))


print(list(filter(lambda x: x % 2 != 0, nums)))
