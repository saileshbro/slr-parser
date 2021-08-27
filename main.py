from slr_parser import SLRParser
from grammar import *
if __name__ == "__main__":
    """
    Reads the grammar file and creates a dictionary of the grammar.
    """
    global grammar_str
    with open('grammar.txt') as f:
        """
        Reads the lines from the grammar file except the empty lines
        """
        grammar_list = list(filter(None, f.read().splitlines()))
        """
        Joins all the lines with \n string
        """
        grammar_str = '\n'.join(grammar_list)
    g = Grammar(grammar_str)
    """
    Add S' -> S at the top of the grammar
    """
    g = Grammar(f"{g.start}' -> {g.start}\n{g.grammar_str}")
    g.print_info()
    g.first_follow()
    g.print_first_follow()
    parser = SLRParser(g)
    parser.construct_parse_table()
    parser.draw_parse_table()
