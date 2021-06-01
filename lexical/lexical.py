class Lex:

    def __init__(self):
        self.other_char_list = ['\n', '\t']
        self.border_char_list = {'+', '-', '*',
                                 '(', ')', '/', '{', '}', ';', ',', ' ', '\n', '\t'}
        self.reserved_words_list = ['int', 'bool', 'void', 'return','struct',
                                    'while', 'if', 'else', 'put', 'get', 'true', 'false']

        self.token_list = []
        self.symbol_table = {}
        self.symbol_table_id = {}
        self.symbol_idx = 0
        self.state = 0
        self.attr_dict = {}
        for e in self.border_char_list:
            self.attr_dict[e] = ''
        for e in self.reserved_words_list:
            self.attr_dict[e] = ''
        self.attr_dict['<'] = 'LT'
        self.attr_dict['<='] = 'LE'
        self.attr_dict['<>'] = 'NE'
        self.attr_dict['>'] = 'GT'
        self.attr_dict['>='] = 'GE'
        self.attr_dict['!'] = 'NON'
        self.attr_dict['&&'] = 'AND'
        self.attr_dict['&'] = 'BAND'
        self.attr_dict['||'] = 'OR'
        self.attr_dict['|'] = 'BOR'
        self.attr_dict['=='] = 'EQ'
        self.attr_dict['='] = ''

    def print_line(self, info):
        n = len(info)
        nstar = (50 - n) // 2
        print('* ' * nstar, info, '* ' * nstar)

    def filter(self, text):
        p, i = 0, 0
        result = ''
        text_len = len(text)
        while True:
            if i == text_len:
                break
            try:
                if text[i] == '/' and text[i + 1] == '/':
                    while text[i] != '\n':
                        i += 1
                if text[i] == '/' and text[i + 1] == '*':
                    i += 2
                    while text[i] != '*' and text[i + 1] != '/':
                        i += 1
                    i += 2
            except IndexError:
                print('/ mismatch')
                exit(0)

            while i < text_len - 1 and text[i] == ' ' and text[i + 1] == ' ':
                i += 1
            if text[i] not in self.other_char_list:
                result += text[i]
                p += 1

            i += 1
        return result

    def insert_symbol(self, symbol):
        if symbol in self.symbol_table.keys():
            return self.symbol_table[symbol]
        self.symbol_table[symbol] = self.symbol_idx
        self.symbol_table_id[self.symbol_idx] = symbol
        self.symbol_idx += 1
        return self.symbol_idx - 1

    def insert_token(self, token, attr):
        if token in ['', ' ', '\n']:
            return
        if isinstance(attr, int):
            self.token_list.append((token, attr, (self.cur_line, self.cur_row)))
        else:
            self.token_list.append((token, attr, (self.cur_line, self.cur_row)))

    def print_error(self, info):
        print(f'{info} at line {self.cur_line}, char at {self.i}')

    def scanner(self, s):

        def case0(tk, c):
            if c.isalpha():
                return 1
            elif c >= '1' and c <= '9':
                return 2
            elif c == '<':
                return 5
            elif c == '>':
                return 6
            elif c == '=':
                return 7
            elif c in self.border_char_list:
                if tk == '!':
                    self.insert_token('RELATION', tk)
                    return 0
                elif tk not in ['', ' ']:
                    self.insert_token('LOGIC', tk)
                    return 0
                else:
                    return 0

            elif c == '&':
                return 9
            elif c == '|':
                return 11
            elif c == '0':
                return 17
            else:
                self.print_error("invalid symbol  " + c)
                return -1

        def case1(tk, c):
            if c.isalnum():
                return 1
            else:
                if self.in_border(c):
                    if tk in self.reserved_words_list:
                        self.insert_token(tk, '')
                        return 0
                    else:
                        idx = self.insert_symbol(tk)
                        self.insert_token('id', idx)
                        return 0
                else:
                    self.print_error("invalid variable name")
                    exit(-1)
                    return -1

        def case2(tk, c):
            if c.isdigit():
                return 3
            elif self.in_border(c):
                self.insert_token('digit', int(tk))
                return 0
            else:
                self.print_error('invalid number or variable name')
                return -1

        def case3(tk, c):
            if c.isdigit():
                return 4
            elif self.in_border(c):
                self.insert_token('digit', int(tk))
                return 0
            else:
                self.print_error("invalid 10 dec base number express")
                return -1

        def case4(tk, c):
            if c.isdigit():
                return 16
            elif self.in_border(c):
                self.insert_token('digit', int(tk))
                return 0
            else:
                self.print_error("invalid 10 dec base number express")
                return -1

        def case16(tk, c):
            if c not in self.border_char_list:
                self.print_error('invalid int number(should in range 0-9999)')
                return -1
            elif self.in_border(c):
                self.insert_token('digit', int(tk))
                return 0
            else:
                self.print_error("invalid 10 dec base number express")
                return -1

        def case5(tk, c):
            if c in ['=', '>']:
                return 13
            elif self.in_border(c):
                self.insert_token('RELATION', tk)
                return 0
            else:

                self.print_error("invalid relation operator")
                return -1

        def case6(tk, c):
            if c == '=':
                return 15
            elif self.in_border(c):
                self.insert_token('RELATION', tk)
                return 0
            else:
                self.print_error("invalid relation operator < " + c)
                return -1

        def case7(tk, c):
            if c == '=':
                return 8
            elif self.in_border(c):
                self.insert_token('ASSIGN-OP', tk)
                return 0
            else:
                self.print_error("invalid relation operator = " + c)
                return -1

        def case8(tk, c):
            if self.in_border(c):
                self.insert_token('RELATION', tk)
                return 0
            else:
                self.print_error("invalid relation operator == " + c)
                return -1

        def case9(tk, c):
            if c == '&':
                return 10
            elif self.in_border(c):
                self.insert_token('LOGIC', tk)
                return 0
            else:
                self.print_error("invalid logic operator & " + c)
                return -1

        def case10(tk, c):
            if self.in_border(c):

                self.insert_token('LOGIC', tk)
                return 0
            else:
                self.print_error("invalid logic operator & " + c)
                return -1

        def case11(tk, c):
            if c == '|':
                return 12
            elif self.in_border(c):
                self.insert_token('LOGIC', tk)
                return 0
            else:
                self.print_error("invalid logic operator | " + c)
                return -1

        def case12(tk, c):
            if self.in_border(c):

                self.insert_token('LOGIC', tk)
                return 0
            else:
                self.print_error("invalid logic operator | " + c)
                return -1

        def case13(tk, c):
            if self.in_border(c):
                self.insert_token('RELATION', tk)
                return 0
            else:
                self.print_error("invalid relation operator < " + c)
                return -1

        def case15(tk, c):
            if self.in_border(c):
                self.insert_token('RELATION', tk)
                return 0
            else:
                self.print_error("invalid relation operator <=" + c)
                return -1

        def case17(tk, c):
            if c == 'x':
                return 19
            elif '1' <= c <= '7':
                return 18
            elif self.in_border(c):
                self.insert_token('digit', 0)
                return 0
            else:
                self.print_error('invalid number base expression')
                return -1

        def case18(tk, c):
            if '1' <= c <= '7':
                return 18
            elif self.in_border(c):
                self.insert_token('digit', int(tk, 8))
                return 0
            else:
                self.print_error('invalid 8 Oct base expression')
                return -1

        def case19(tk, c):
            if c.isdigit() or 'a' <= c <= 'f':
                return 20
            else:
                self.print_error('invalid 16 Hex base expression')
                return -1

        def case20(tk, c):
            if c.isdigit() or 'a' <= c <= 'f':
                return 20
            elif self.in_border(c):
                self.insert_token('digit', int(tk, 16))
                return 0
            else:
                self.print_error('invalid 16 Hex base expression')
                return -1

        switch = {
            0: case0,
            1: case1,
            2: case2,
            3: case3,
            4: case4,
            5: case5,
            6: case6,
            7: case7,
            8: case8,
            9: case9,
            10: case10,
            11: case11,
            12: case12,
            13: case13,
            15: case15,
            16: case16,
            17: case17,
            18: case18,
            19: case19,
            20: case20
        }

        self.i = 0
        self.cur_line = 1
        self.cur_row = 1
        slen = len(s)

        tk = ''
        while s[self.i] in ['\n', '\t', ' ']:
            self.i += 1
            self.cur_row += 1
            if s[self.i] == '\n':
                self.cur_line += 1
                self.cur_row = 1
        while self.i < slen:
            # process comment
            while self.i + 1 < slen and s[self.i] == '/' and s[self.i + 1] == '/':
                # print(self.i, len(s))
                while self.i < slen and s[self.i] != '\n':
                    self.i += 1
                    self.cur_row += 1
                self.cur_line += 1
                self.cur_row = 1
                self.i += 1
                self.cur_row += 1
                while self.i < slen and s[self.i] in ['\n', '\t', ' ']:
                    self.i += 1
                    self.cur_row += 1
                    if s[self.i] == '\n':
                        self.cur_line += 1
                        self.cur_row = 1

            if self.i >= slen:
                break
            c = s[self.i]
            # print('char', c, 'state', self.state)
            self.state = switch[self.state](tk, c)

            tk += c
            if self.state != 0:
                self.i += 1
                self.cur_row += 1
                if self.state == -1:
                    while s[self.i] not in self.border_char_list:
                        if s[self.i] == '\n':
                            self.cur_line += 1
                            self.cur_row = 1
                        self.i += 1
                        self.cur_row += 1
                    self.i -= 1
                    self.cur_row -= 1
                    while s[self.i] in ['\n', '\t', ' ']:
                        if s[self.i] == '\n':
                            self.cur_line += 1
                            self.cur_row = 1
                        self.i += 1
                        self.cur_row += 1
                    self.state = 0
                    tk = ''
            else:
                if c in self.border_char_list:
                    self.insert_token(c, '')
                    self.i += 1
                    self.cur_row += 1
                tk = ''
                while self.i < slen and s[self.i] in ['\n', '\t', ' ']:
                    if s[self.i] == '\n':
                        self.cur_line += 1
                        self.cur_row = 1
                    self.i += 1
                    self.cur_row += 1

    def run(self, filename, preprocess=False):
        file = open(filename, encoding='utf8')
        text = file.read()
        self.print_line('origin data')

        print(text)
        if preprocess:
            text = self.filter(text)
            self.print_line('pre processed data')
            print(text)

        print()
        self.scanner(text)
        self.print_line('lexical result')
        for elem in self.token_list:
            print(elem)

    def create_tokens(self, filename):
        file = open(filename, encoding='utf8')
        text = file.read()
        self.scanner(text)
        # create new token_list
        tokens = []
        for k, v, pos in self.token_list:
            if v == '':
                tokens.append((k, '', pos))
            elif k == 'id':
                tokens.append((k, self.symbol_table_id[v], pos))
            elif k == 'digit':
                tokens.append((k, v, pos))
            else:
                tokens.append((v, '', pos))

        return tokens

    def print_static_data(self):
        self.print_line('statictics info')
        print('total code lines', self.cur_line)
        print('total characters counts', self.i)
        from collections import Counter
        counter = Counter(self.token_list)
        for elem, cnt in counter.items():
            if elem[0] == 'id':
                print(f'({self.symbol_table_id[elem[1]]}, {cnt})')
            elif elem[1] != '':
                print(f'({elem[0]}.{elem[1]}, {cnt})')
            else:
                print(f'({elem[0]}, {cnt})')

    def in_border(self, c):
        return c in self.border_char_list or c.isalnum() or c in ['=', '<', '>', '!', '&', '|']


if __name__ == '__main__':
    # file = open("./full_test.cpp", encoding='utssf8')
    filepath = 'struct_test.cpp'
    lex = Lex()
    lex.run(filepath, preprocess=False)
    # lex.print_static_data()
