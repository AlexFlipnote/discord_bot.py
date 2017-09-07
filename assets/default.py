import time


def timetext(name):
    return f"{name}_{int(time.time())}.txt"


def date(target):
    return target.strftime("%d %B %Y, %H:%M")
