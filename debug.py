import keyboard


EXIT_FLAG = False
def stop():
    global EXIT_FLAG
    EXIT_FLAG = True

keyboard.on_press_key('esc', lambda event: stop())

while True:
    print(EXIT_FLAG)