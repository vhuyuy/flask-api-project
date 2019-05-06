class User(object):
    def __init__(self, _name, _age):
        # self 类似this指针
        # self.name 定义类属性
        self.name = _name
        self.age = _age

    def __repr__(self):
        return self.name + '|' + self.age

    def __str__(self):
        return self.name

    def GetName(self):
        return self.name
