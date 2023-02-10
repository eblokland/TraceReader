# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from EnvironmentParser import EnvironmentLog

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print('Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    log = EnvironmentLog('./data/nicelog.txt')
    log.print_logs()
    res = log.get_power_for_time(783838073446)
    print(res)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
