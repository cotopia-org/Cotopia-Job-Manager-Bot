
PREFIX = "JRS"
THE_NUMBER = 53487611231215


def gen_code(id: int):
    string = PREFIX + str(THE_NUMBER - id)
    return string


def decode(code: str):
    num = code.split(PREFIX, 1)[1]
    id = THE_NUMBER - int(num)
    return id


