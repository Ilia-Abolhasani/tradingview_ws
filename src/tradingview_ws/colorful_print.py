class ColorfulPrint():
    @staticmethod
    def print_red(text):
        print("\033[91m" + text + "\033[0m")

    @staticmethod
    def print_green(text):
        print("\033[92m" + text + "\033[0m")

    @staticmethod
    def print_yellow(text):
        print("\033[93m" + text + "\033[0m")

    @staticmethod
    def print_blue(text):
        print("\033[94m" + text + "\033[0m")
