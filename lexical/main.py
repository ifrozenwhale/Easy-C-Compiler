from lexical import Lex
if __name__ == '__main__':
    lex = Lex()
    filepath = './test2.cpp'
    lex.run(filepath, preprocess=False)
    lex.print_static_data()
