from lexical import Lex
if __name__ == '__main__':
    lex = Lex()
    filepath = './mytest.cpp'
    lex.run(filepath, preprocess=False)
    lex.print_static_data()
