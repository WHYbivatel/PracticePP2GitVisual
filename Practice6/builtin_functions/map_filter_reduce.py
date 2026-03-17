from functools import reduce

# Example 1: map - square numbers
nums = [1, 2, 3]
squared = list(map(lambda x: x**2, nums))
print(squared)

# Example 2: filter - even numbers
evens = list(filter(lambda x: x % 2 == 0, nums))
print(evens)

# Example 3: reduce - sum
sum_all = reduce(lambda x, y: x + y, nums)
print(sum_all)

# Example 4: map with function
def double(x): return x * 2
print(list(map(double, nums)))

# Example 5: filter with function
def is_positive(x): return x > 0
print(list(filter(is_positive, [-1, 2, 3])))
