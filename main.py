from Compiler.LexicalAnalyzer import Lexer
from Compiler.Parser import Parser
from Compiler.Intermediate_Code_Generation import IntermidiateCodeGeneration
from Compiler.Code_Optimization import CodeOptimization
from Compiler.Code_Generation import CodeGeneration

counter = 0


while True:
    counter += 1
    f = open("read.txt", 'r')
    a = f.read()

    try:
        arr = Lexer(a).get_tokens();
        print('TOKENS:')
        print('type, lexeme\n')
        print(arr)

        tree = Parser(arr).get_root();
        print("-" * 50)
        print('AST:\n')
        print(tree)
        print("-" * 50)

        print("\nSymbol Table:")
        print(tree)

        code, identifiers, constants = IntermidiateCodeGeneration(tree).get_code();
        #print("\n")
        #print("-" * 50)
        #print("Intermediate Code Generation:\n")
        #print(identifiers)
        #print(constants, "\n")
        #code.print_extra()
        #print("-" * 50)

        code, identifiers, constants, tempmap = CodeOptimization(code, identifiers, constants).get_code();
        print("\n")
        print("-" * 50)
        print('Code Optimization:\n')
        print(identifiers)
        print(constants, "\n")
        code.print_extra()
        print("-"*50)

        print("-"*50)
        print(f"[{counter}] : ", end="\n\n")
        CodeGeneration(code, identifiers, constants, tempmap)
        print("-"*50)

    except Exception as e:
        print(e)

    f.close()
    input()
