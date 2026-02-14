class Animal:
    def speak(self):
        print("Sound")

class Dog(Animal):
    def speak(self):
        print("Woof")

class Shape:
    def area(self):
        return 0

class Square(Shape):
    def area(self):
        return 4

class Person:
    def greet(self):
        print("Hello")

class Student(Person):
    def greet(self):
        print("Hi")
