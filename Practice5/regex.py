import re

# 1 --------------------------------------------------

pattern = r'ab*'
strings = ["a", "ab", "abb", "ac", "b"]

for s in strings:
    if re.fullmatch(pattern, s):
        print(s)


# 2 --------------------------------------------------

pattern = r'ab{2,3}'
strings = ["ab", "abb", "abbb", "abbbb"]

for s in strings:
    if re.fullmatch(pattern, s):
        print(s)


# 3 --------------------------------------------------

text = "hello_world test_case Example_Test another_example"
pattern = r'\b[a-z]+_[a-z]+\b'

print(re.findall(pattern, text))


# 4 --------------------------------------------------

text = "Hello world Test Python REGEX Example"
pattern = r'\b[A-Z][a-z]+\b'

print(re.findall(pattern, text))


# 5 --------------------------------------------------

pattern = r'a.*b'
strings = ["ab", "axb", "axxxb", "ac", "ba"]

for s in strings:
    if re.fullmatch(pattern, s):
        print(s)


# 6 --------------------------------------------------

text = "Hello, world. Python is fun"
print(re.sub(r"[ ,.]", ":", text))


# 7 --------------------------------------------------

def snake_to_camel(text):
    return re.sub(r"_([a-z])", lambda m: m.group(1).upper(), text)

print(snake_to_camel("hello_world_example"))


# 8 --------------------------------------------------

text = "HelloWorldPythonTest"
print(re.split(r"(?=[A-Z])", text))


# 9 --------------------------------------------------

text = "HelloWorldPythonTest"
print(re.sub(r"(?<!^)(?=[A-Z])", " ", text))


# 10 --------------------------------------------------

def camel_to_snake(text):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()

print(camel_to_snake("helloWorldExample"))