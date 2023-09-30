import os

RED_PATH = "logs/red_log.txt"
GREEN_PATH = "logs/green_log.txt"
YELLOW_PATH = "logs/yellow_log.txt"
BLUE_PATH = "logs/blue_log.txt"

for _path in [RED_PATH, GREEN_PATH, YELLOW_PATH, BLUE_PATH]:
    if os.path.exists(_path):
        os.remove(_path)


class ColorfulPrint():
    @staticmethod
    def write(path, text):
        if not os.path.exists(path):
            with open(path, 'w') as file:
                file.write(text + "\n\n")
        else:
            with open(path, 'a') as file:
                file.write(text + "\n\n")

    @staticmethod
    def print_red(text, write=True):
        if write:
            ColorfulPrint.write(RED_PATH, text)
        print("\033[91m" + text + "\033[0m")

    @staticmethod
    def print_green(text, write=True):
        if write:
            ColorfulPrint.write(GREEN_PATH, text)
        print("\033[92m" + text + "\033[0m")

    @staticmethod
    def print_yellow(text, write=True):
        if write:
            ColorfulPrint.write(YELLOW_PATH, text)
        print("\033[93m" + text + "\033[0m")

    @ staticmethod
    def print_blue(text, write=True):
        if write:
            ColorfulPrint.write(BLUE_PATH, text)
        print("\033[94m" + text + "\033[0m")
