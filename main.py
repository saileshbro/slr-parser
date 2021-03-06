from slr_parser import SLRParser
from grammar import *
if __name__ == "__main__":
    """
    Reads the grammar file and creates a dictionary of the grammar.
    """
    global grammar_str
    file_path = input("Enter file path, relative to the main.py\n")

    test_str = str(
        input("Enter test string, terminals seperated by space eg\n"))
    print()
    with open(file_path) as f:
        """
        Reads the lines from the grammar file except the empty lines
        """
        grammar_list = list(filter(None, f.read().splitlines()))
        """
        Joins all the lines with \n string
        """
        grammar_str = '\n'.join(grammar_list)
    temp = Grammar(grammar_str)
    """
    Add S' -> S at the top of the grammar
    """
    grammar_aug = f"{temp.start}' -> {temp.start}\n{temp.grammar_str}"
    g = Grammar(grammar_aug)
    g.print_info()
    g.first_follow()
    g.print_first_follow()
    parser = SLRParser(g)
    parser.construct_parse_table()
    parser.draw_parse_table()

    print()
    parser.parse_input_string(test_str)
    parser.print_parsing_result()
