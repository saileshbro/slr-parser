from grammar import *
from texttable import Texttable
if __name__ == "__main__":
    g = Grammar("grammar.txt")
    first, follow = g.first_follow()
    my_table = Texttable()
    my_table.header(["Symbol", "First"])
    for key, value in first.items():
        my_table.add_row([key, value])
    print(my_table.draw())
    print('\n\n')
    my_table.header(["Symbol", "Follow"])
    for key, value in follow.items():
        my_table.add_row([key, value])
    print(my_table.draw())
