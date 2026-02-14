def print_args(*args):
    for arg in args:
        print(arg)

def sum_all(*nums):
    return sum(nums)

def print_kwargs(**kwargs):
    for key, value in kwargs.items():
        print(key, value)

def user_info(**info):
    print(info)

def mixed(a, *args, **kwargs):
    print(a)
    print(args)
    print(kwargs)
