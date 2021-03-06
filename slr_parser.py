from grammar import Grammar


class SLRParser:
    """
    Pass the augmented grammar here
    """

    def __init__(self, G: Grammar):
        self.G_prime = G
        self.G_indexed = []
        """
        For head and bodies in grammar items
        """
        for head, bodies in self.G_prime.grammar.items():
            """
            For each body in bodies of each grammar item
            """
            for body in bodies:
                self.G_indexed.append((head, body))
        """
        Save first and follow of the grammar
        """
        self.G_prime.first_follow()
        self.first = self.G_prime.first
        self.follow = self.G_prime.follow
        """
        Get the Canonical C items
        """
        self.canonical = self.items(self.G_prime)
        """
        Get the action
        """
        self.action = list(self.G_prime.terminals)+["$"]
        self.goto = list(self.G_prime.nonterminals-{self.G_prime.start})
        self.parse_table_symbols = self.action+self.goto
        self.parse_table = self.construct_parse_table()

    """
    Get the canonical item for the grammar
    """

    def items(self, G_prime: Grammar):
        """
        Get the closure for this grammar
        """
        canonicalItems = [self.closure(
            {G_prime.start: {('.', G_prime.start[:-1])}})]

        while True:
            """
            get length of the canonical items
            """
            item_len = len(canonicalItems)

            for I in canonicalItems.copy():
                """
                For each item in the closure
                """
                for X in G_prime.symbols:
                    """
                    For each symbol in the grammar
                    perform goto on the symbol
                    """
                    goto = self.eval_goto(I, X)

                    if goto and goto not in canonicalItems:
                        """
                        If goto is not in the closure add it
                        """
                        canonicalItems.append(goto)

            if item_len == len(canonicalItems):
                return canonicalItems

    """
    Evaluated goto on a provided canonical item with a given non terminal
    Here I is a canonical item set
    X is a symbol
    """

    def eval_goto(self, I, X):
        goto = {}
        """
        For head and bodies in the canonical item
        """
        for head, bodies in I.items():
            """
            for each symbol in the body, which may include a .
            """
            for body in bodies:
                """
                if dot is not in the last position
                """
                if '.' in body[:-1]:
                    """
                    Get the dot position
                    """
                    dot_pos = body.index('.')

                    if body[dot_pos + 1] == X:
                        """
                        If the symbol after dot is the same as the symbol passed in the function
                        Dont get confused with \ here this is just to move the current line to new one to compensate space
                        """
                        replaced_dot_body = body[:dot_pos] + \
                            (X, '.') + body[dot_pos + 2:]
                        """
                        For head and bodies in the closure of the current item nonterminal,
                        and the replaced dot body add goto items calculated now
                        """
                        for C_head, C_bodies in self.closure({head: {replaced_dot_body}}).items():
                            goto.setdefault(C_head, set()).update(C_bodies)

        return goto

    """
    Get the closure of the grammar instance
    I passed is the map of nonterminal symbols and the augmented production with a '.' attached to it
    {
      "E":{ ('.', 'E') }
    }
    """

    def closure(self, I):
        J = I

        while True:
            item_len = len(J)
            """
            For head and body in the passed map
            """
            for head, bodies in J.copy().items():
                for body in bodies.copy():
                    """
                    Check if there is . in the production exept the last item
                    E -> a.Bc is pass
                    E -> aBc.  wont pass
                    """
                    if '.' in body[:-1]:
                        """
                        Get the symbol after dot
                        """
                        symbol_after_dot = body[body.index('.') + 1]
                        """
                        Check if the symbol after dot is a non terminals
                        """
                        if symbol_after_dot in self.G_prime.nonterminals:
                            """
                            Repopulate the grammars and add to the canonical items
                            Here symbol after dot will be a non terminal
                            """
                            for G_body in self.G_prime.grammar[symbol_after_dot]:
                                """
                                Add the nonterminal in the reference passed in the function
                                """
                                J.setdefault(symbol_after_dot, set()).add(
                                    ('.',) if G_body == ('??',) else ('.',) + G_body)
            """
            Check if the length of the map is the same as before
            """
            if item_len == len(J):
                return J

    """
    Construct the parse table
    """

    def construct_parse_table(self):
        """
        Initialize the parse table
        """
        parse_table = {r: {c: '' for c in self.parse_table_symbols}
                       for r in range(len(self.canonical))}
        """
        For each canonical item
        """
        for i, I in enumerate(self.canonical):
            """
            For each head, bodies in the canonical item
            """
            for head, bodies in I.items():
                """
                For each body in the bodies
                """
                for body in bodies:
                    """
                    If . is  in the last position
                    """
                    if '.' in body[:-1]:
                        """
                        If the body is not in the parse table
                        """
                        symbol_after_dot = body[body.index('.') + 1]

                        if symbol_after_dot in self.G_prime.terminals:
                            """
                            Shift here, calculate the shift state for the parsing table
                            """
                            s = f's{self.canonical.index(self.eval_goto(I, symbol_after_dot))}'

                            """
                            Check if the shift state is not in the parse_table[i] and for the symbol after dot
                            """
                            if s not in parse_table[i][symbol_after_dot]:
                                """
                                reduce reduce conflict happened here
                                """
                                if 'r' in parse_table[i][symbol_after_dot]:
                                    parse_table[i][symbol_after_dot] += '/'

                                parse_table[i][symbol_after_dot] += s

                    elif body[-1] == '.' and head != self.G_prime.start:
                        """
                        If the last item of the body is . and if the head of the item iterated is not the start symbol
                        """
                        """
                        For each head and body of the indexed grammars
                        """
                        for j, (G_head, G_body) in enumerate(self.G_indexed):
                            """
                            if the head is the same as the head of the indexed grammar
                            and if  body is ??
                            or if the body is .
                            or if the body except last is in the body of the indexed grammar
                            """
                            if G_head == head and (G_body == body[:-1] or G_body == ('??',) and body == ('.',)):
                                """
                                Read the follow of the given grammar
                                """
                                for f in self.follow[head]:
                                    """
                                    Reduce term is being added here
                                    """
                                    if parse_table[i][f]:
                                        """
                                        if already exists, then a reduce reduce conflict is here
                                        """
                                        parse_table[i][f] += '/'
                                    """
                                    Add reduce item in the parse table
                                    """
                                    parse_table[i][f] += f'r{j}'
                                """
                                Break from the enumeration loop if inside the if condition
                                """
                                break

                    else:
                        """
                        This is the acceptance state
                        """
                        parse_table[i]['$'] = 'acc'
            """
            For each nonterminal symbol in the grammar
            """
            for a in self.G_prime.nonterminals:  # CASE 3
                j = self.eval_goto(I, a)
                """
                perform goto in each nonterminal
                """
                if j in self.canonical:
                    """
                    For each item in canonical
                    """
                    parse_table[i][a] = self.canonical.index(j)

        return parse_table

    """
    Draw parse table
    """

    def draw_parse_table(self):
        from texttable import Texttable
        print('PARSING TABLE:')
        action_goto_table = Texttable(max_width=0)
        for r in range(len(self.canonical)+1):
            if r == 0:
                arr = ['STATE'] + self.parse_table_symbols
                action_goto_table.add_row(arr)
            else:
                row = []
                for c in self.parse_table_symbols:
                    row.append(self.parse_table[r-1][c])
                row = [r-1]+row
                action_goto_table.add_row(row)
        print(action_goto_table.draw())

    def parse_input_string(self, input_string: str):
        from texttable import Texttable

        print('PARSING INPUT STRING:')
        buffer = f'{input_string} $'.split()
        pointer = 0
        a = buffer[pointer]
        stack = ['0']
        symbols = ['']
        results = {
            'step': [''],
            'stack': ['STACK'] + stack,
            'symbols': ['SYMBOLS'] + symbols,
            'input': ['INPUT'],
            'action': ['ACTION']
        }

        step = 0
        while True:
            s = int(stack[-1])
            step += 1
            results['step'].append(f'({step})')
            results['input'].append(' '.join(buffer[pointer:]))

            if a not in self.parse_table[s]:
                results['action'].append(f'ERROR: unrecognized symbol {a}')
                break

            elif not self.parse_table[s][a]:
                results['action'].append(
                    'ERROR: input cannot be parsed by given grammar')
                break

            elif '/' in self.parse_table[s][a]:
                action = 'reduce' if self.parse_table[s][a].count(
                    'r') > 1 else 'shift'
                results['action'].append(
                    f'ERROR: {action}-reduce conflict at state {s}, symbol {a}')
                break

            elif self.parse_table[s][a].startswith('s'):
                number = self.parse_table[s][a][1:]
                results['action'].append(f'shift {number}')
                stack.append(self.parse_table[s][a][1:])
                symbols.append(a)
                results['stack'].append(' '.join(stack))
                results['symbols'].append(' '.join(symbols))
                pointer += 1
                a = buffer[pointer]

            elif self.parse_table[s][a].startswith('r'):
                head, body = self.G_indexed[int(self.parse_table[s][a][1:])]
                results['action'].append(
                    f'reduce by {head} -> {" ".join(body)}')

                if body != ('??',):
                    stack = stack[:-len(body)]
                    symbols = symbols[:-len(body)]

                stack.append(str(self.parse_table[int(stack[-1])][head]))
                symbols.append(head)
                results['stack'].append(' '.join(stack))
                results['symbols'].append(' '.join(symbols))

            elif self.parse_table[s][a] == 'acc':
                results['action'].append('accept')

                break

        self.results = results
        return

    def print_parsing_result(self):
        from texttable import Texttable
        table = Texttable(max_width=0)
        results = self.results
        symbol = self.results['symbols'][1:]
        stack = self.results['stack'][1:]
        stack = [e.strip().split(" ") for e in stack]
        symbol = [e.strip().split(" ") for e in symbol]
        stack_symbol = []
        for st_element, sy_element in zip(stack, symbol):
            total = st_element + sy_element
            length = len(total)
            value = []

            for i in range(length):
                if(i % 2 == 0):
                    index = int(i/2)
                    value.append(st_element[index])
                else:
                    index = int((i-1)/2)
                    value.append(sy_element[index])
            value = " ".join(value).strip()
            stack_symbol.append(value)
        table.header(['', 'STACK', 'INPUT', 'ACTION'])
        input_arr = results['input'][1:]
        action_arr = results['action'][1:]
        for i in range(len(input_arr)):
            table.add_row([i, stack_symbol[i], input_arr[i], action_arr[i]])
        print(table.draw())
