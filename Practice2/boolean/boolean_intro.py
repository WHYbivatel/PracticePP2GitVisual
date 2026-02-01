is_student = True
is_graduated = False
print(f"Student: {is_student}, Graduated: {is_graduated}")


def is_even(number):
    return number % 2 == 0

result = is_even(10)
print(f"Is 10 even? {result}")


empty_list = []
full_list = [1, 2, 3]
print(f"Empty list: {bool(empty_list)}")
print(f"Full list: {bool(full_list)}")


has_permission = True
if has_permission:
    print("Access granted")
else:
    print("Access denied")