import sys

import ply.yacc as yacc

from Cparser import Cparser
from Interpreter import Interpreter
from TypeChecker import TypeChecker

if __name__ == '__main__':

    filename = sys.argv[1] if len(sys.argv) > 1 else "ex2.txt"
    try:
        test_file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    Cparser = Cparser()
    parser = yacc.yacc(module=Cparser)
    text = test_file.read()

    ast = parser.parse(text, lexer=Cparser.scanner)
    typeChecker = TypeChecker()
    typeChecker.visit(ast)

    # jesli wizytor TypeChecker z implementacji w poprzednim lab korzystal z funkcji accept
    # to nazwa tej ostatniej dla Interpretera powinna zostac zmieniona, np. na accept2 ( ast.accept2(Interpreter()) )
    # tak aby rozne funkcje accept z roznych implementacji wizytorow nie kolidowaly ze soba
    ast.accept(Interpreter())

    # in future
    # ast.accept(OptimizationPass1())
    # ast.accept(OptimizationPass2())
    # ast.accept(CodeGenerator())
