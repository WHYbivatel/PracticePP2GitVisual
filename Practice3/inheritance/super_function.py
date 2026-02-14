class Person:
    def __init__(self, name):
        self.name = name

class Student(Person):
    def __init__(self, name, age):
        super().__init__(name)
        self.age = age

class A:
    def __init__(self):
        print("A")

class B(A):
    def __init__(self):
        super().__init__()

class Animal:
    def __init__(self, species):
        self.species = species

class Dog(Animal):
    def __init__(self, species, name):
        super().__init__(species)
        self.name = name
