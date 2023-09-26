import os
if os.path.exists("red_log.txt"):
    os.remove("red_log.txt")
if os.path.exists("green_log.txt"):
    os.remove("green_log.txt")
if os.path.exists("red_log.txt"):
    os.remove("red_log.txt")
if os.path.exists("blue_log.txt"):
    os.remove("blue_log.txt")


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
    def print_red(text):
        ColorfulPrint.write("red_log.txt", text)
        print("\033[91m" + text + "\033[0m")

    @staticmethod
    def print_green(text):
        ColorfulPrint.write("green_log.txt", text)
        print("\033[92m" + text + "\033[0m")

    @staticmethod
    def print_yellow(text):
        ColorfulPrint.write("yellow_log.txt", text)
        print("\033[93m" + text + "\033[0m")

    @staticmethod
    def print_blue(text):
        ColorfulPrint.write("blue_log.txt", text)
        print("\033[94m" + text + "\033[0m")
