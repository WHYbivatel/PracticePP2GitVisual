import math

degree = float(input("Input degree: "))
radian = degree * (math.pi / 180)

print("Output radian:", round(radian, 6))





height = float(input("Height: "))
base1 = float(input("Base, first value: "))
base2 = float(input("Base, second value: "))

area = ((base1 + base2) / 2) * height

print("Expected Output:", area)






import math

n = int(input("Input number of sides: "))
s = float(input("Input the length of a side: "))

area = (n * s**2) / (4 * math.tan(math.pi / n))

print("The area of the polygon is:", round(area, 2))






base = float(input("Length of base: "))
height = float(input("Height of parallelogram: "))

area = base * height

print("Expected Output:", float(area))