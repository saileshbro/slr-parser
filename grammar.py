class Grammar:

    def __init__(self, grammar_str):
        self.grammar_list = grammar_str.split('\n')
        self.grammar_str = grammar_str
        self.grammar = {}
        self.start = None
        self.terminals = set()
        self.nonterminals = set()
        self.first = set()
        self.follow = set()
        """
        For each grammar line, partition the head and the body part of the grammar.
        """
        for line in self.grammar_list:
            """
            Split the line into head and body.
            """
            head, _, bodies = line.partition(' -> ')
            """
            Check if the head is a nonterminal.
            """
            if not head.isupper():
                raise ValueError(
                    f'\'{head} -> {bodies}\': Head \'{head}\' is not capitalized to be treated as a nonterminal.')
            """
            Since in loop, check if the start symbol is defined.
            If not defined then define it as the head.
            """
            if not self.start:
                self.start = head
            """
            Add head in the grammar map, with default value as empty set.
            """
            self.grammar.setdefault(head, set())
            """
            Add thehead to the list of nonterminals.
            """
            self.nonterminals.add(head)
            """
            Get the bodies of the grammar item seperated by a |, transformed in the set of tuple
            S -> q A B C | A b C, then the bodies will be converted to a set of tuple
            {(q, A, B, C),(A,b,C)}
            """
            bodies = {tuple(body.split())
                      for body in ' '.join(bodies.split()).split('|')}
            """
            Check if epsilon starts with the body of the grammar.
            """
            for body in bodies:
                if 'ε' in body and body != ('ε',):
                    raise ValueError(
                        f'\'{head} -> {" ".join(body)}\': Null symbol \'ε\' is not allowed here.')
                """
                Add the body of a grammar to the dict of the grammar.
                """
                self.grammar[head].add(body)
                """
                Check if each symbol is terminal or not and then add it in the list
                """
                for symbol in body:
                    if not symbol.isupper() and symbol != 'ε':
                        self.terminals.add(symbol)
                    elif symbol.isupper():
                        self.nonterminals.add(symbol)
                """
                Union set of terminals and nonterminals. and add in the symbols list
                """
                self.symbols = self.terminals | (self.nonterminals)
    """
    Find first and follow of this grammar
    """

    def first_follow(self):
        """
        Union setA and setB and set to setA, and return if the setA size was increased
        """
        def union(set_1, set_2):
            set_1_len = len(set_1)
            set_1 |= set_2
            return set_1_len != len(set_1)
        """
        Initialize First map with , symbol and empty set
        """
        first = {symbol: set() for symbol in self.symbols}
        """
        Since first of terminal is terminal itself, so update it
        """
        first.update((terminal, {terminal}) for terminal in self.terminals)
        """
        Initialize Follow map with each non terminal symbol as key and empty set as value
        """
        follow = {symbol: set() for symbol in self.nonterminals}
        """
        Set $ as Follow of start symbol
        """
        follow[self.start].add('$')

        while True:
            """
            create a bool updated value and set it to false
            """
            updated = False
            """
            For each head and bodies of this grammar
            """
            for head, bodies in self.grammar.items():
                """
                For the list of bodies of each head
                """
                for body in bodies:
                    """
                    for each symbol in the body
                    """
                    for symbol in body:
                        if symbol != 'ε':
                            """
                            If the symbol is not epsilon
                            unioon with the first of the head, a non terminal with the first the symbol in body
                            """
                            updated |= union(
                                first[head], first[symbol]-set('ε'))
                            """
                            Check if the epsilon is present in the first of the symbol.
                            If its not present then break the loop
                            """
                            if 'ε' not in first[symbol]:
                                break
                        else:
                            """
                            If the symbol is epsilon then set the epsilon to the first of the head of the current production of the grammar
                            """
                            updated |= union(first[head], set('ε'))
                    else:
                        """
                        This else block runs if the loop is broken because of the break condition
                        """
                        updated |= union(first[head], set('ε'))
                    """
                    get follow of the head of current production statement
                    """
                    follow_head = follow[head]
                    for symbol in reversed(body):
                        if symbol == 'ε':
                            """
                            If the symbol is epsilon then skip it
                            """
                            continue
                        if symbol in follow:
                            """
                            If the symbol is in follow then add follow of the head of current prod except the epsilon
                            """
                            updated |= union(
                                follow[symbol], follow_head - set('ε'))
                        if 'ε' in first[symbol]:
                            """
                            If the epsilon is in first of the symbol then
                            """
                            follow_head = follow_head | first[symbol]
                        else:
                            follow_head = first[symbol]
            if not updated:
                self.first = first
                self.follow = follow
                return first, follow
    """
    Print first and follow of the grammar
    """

    def print_first_follow(self):
        if len(self.first) == 0 or len(self.follow) == 0:
            return
        from texttable import Texttable
        my_table = Texttable(max_width=0)
        my_table.header(["SYMBOL", "FIRST"])
        for key, value in self.first.items():
            my_table.add_row([key, "  ".join(value)])
        print(my_table.draw())
        print('\n')
        my_table = Texttable(max_width=0)
        my_table.header(["SYMBOL", "FOLLOW"])
        for key, value in self.follow.items():
            my_table.add_row([key, "  ".join(value)])
        print(my_table.draw())
        print('\n')

    """
    Print the information of this grammar
    """

    def print_info(self):
        from texttable import Texttable
        my_table = Texttable(max_width=0)
        my_table.header(["TYPE", "VALUE"])
        my_table.add_row(['TERMINALS', "  ".join(self.terminals)])
        my_table.add_row(['NON-TERMINALS', "  ".join(self.nonterminals)])
        augment_table = Texttable(max_width=0)
        augment_table.set_deco(deco=0)
        for i, val in enumerate(self.grammar_list):
            head, _, body = val.partition(' -> ')
            augment_table.add_row([head, '->', body])
        my_table.add_row(['AUGMENTED GRAMMAR', augment_table.draw()])
        print(my_table.draw())
        print('\n')
