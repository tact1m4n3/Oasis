import sys, subprocess
from lexer import *
from parser import Parser
from compiler import Compiler
from sym import *

def main():
    if len(sys.argv) < 3:
        return

    inputfn = sys.argv[1]
    outfn = sys.argv[2]
    asmfn = outfn + '.asm'
    objfn = outfn + '.o'

    lexer = Lexer(inputfn)
    tokens = lexer.make_tokens()
    if lexer.error:
        return

    parser = Parser(tokens)
    tree = parser.parse_file()

    if parser.error:
        return
    print(tree)

    #  nasm -f macho64 test.asm
    #  ld -macosx_version_min 10.13 test.o -o test -lSystem
    
    context = GlobalContext()

    compiler = Compiler(asmfn)
    compiler.visit(tree, context)

    if compiler.error:
        return
    
    compiler.close_output_file()
    
    subprocess.Popen([f'nasm -f macho64 {asmfn}'], shell=True)
    subprocess.Popen([f'ld -macosx_version_min 10.13 {objfn} -o {outfn} -lSystem'], shell=True)
