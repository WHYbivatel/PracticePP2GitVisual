class A:
    def hello(self):
        print("Hello")

class B:
    def world(self):
        print("World")

class C(A, B):
    pass

class X:
    pass

class Y:
    pass

class Z(X, Y):
    pass

class Writer:
    def write(self):
        print("Writing")

class Speaker:
    def speak(self):
        print("Speaking")

class Communicator(Writer, Speaker):
    pass
