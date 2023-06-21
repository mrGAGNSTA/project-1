import os
from utils.intermediatecode import *

# В скрипте определены три словаря: "comparisons", "operations" и "data_types".
# Они содержат соответствия операторов, знаков сравнения
# и типов данных их соответствующим инструкциям языка ассемблера.
comparisons = {
    '<':'jl',
    '>':'jg',
    '==':'je',
    '!=':'jne',
    '>=':'jge',
    '<=':'jle',
}

operations = {
    '+':"add",
    '-':"sub",
    '*':"mul",
    '/':"div"
}

registers = [
    'rax',
    'rbx',
    'rcx',
    'rdx',
    'r8',
    'r9',
    'r10',
    'r11',
    'r12',
    'r13',
    'r14',
    'r15',

]

data_types={'int':8,'int32':8,'int64':8,'int16':8}

# Функция "handle_variables" обрабатывает входные переменные и возвращает их в формате,
# удобном для генерации кода на языке ассемблера.
def handle_variables(a):
    if(str(a).isdigit()):
        return int(a)
    else:
        return f'[{a}]'

# Этот класс инициализируется параметрами для входных кодов, идентификаторов, констант и временной карты.
# Затем он использует эти данные для создания объявлений переменных, разделов данных, разделов кода,
# функций и записи выходных данных в файл.
class CodeGeneration:
    def __init__(self,CodeArray,identifiers,constants,tempmap):
        self.arr = CodeArray
        self.identifiers = identifiers
        self.constants = constants
        self.tempmap = tempmap
        self.f = open('output.asm', 'w')

        self.generate_variables()
        self.start()
        self.generate_code()
        self.end()
        self.generate_functions()
        self.Run()

    def pr(self,s):
        self.f.write(s+'\n')

    # Функция "generate_variables" генерирует объявления переменных в разделе .bss кода на языке ассемблера.
    # Она также объявляет некоторые буферы, используемые в функции печати.
    def generate_variables(self):
        self.pr("""section .bss
\tdigitSpace resb 100
\tdigitSpacePos resb 8\n""")
        for i in self.identifiers:
            self.pr(f"\t{i} resb {data_types[self.identifiers[i]]}")

    # Функция "start" генерирует объявления данных в разделе .data кода на языке ассемблера.
    # Она также генерирует метку "globl _start", которая отмечает начало основной функции в коде на языке ассемблера.
    def start(self):
        self.pr("""section .data\n\ttext db "start",10\n""")
        for i in self.constants:
            self.pr(f'\t{i} db "{self.constants[i]}",10,0')

        self.pr("""section .text\n\tglobal _start\n\n_start:\n""")

    # Функция "end" генерирует инструкцию системного вызова выхода, завершающую выполнение программы.
    def end(self):
        self.pr("""\n\tmov rax, 60\n\tmov rdi, 0\n\tsyscall\n""")

    # Функция "generate_code" обрабатывает входные коды и генерирует соответствующий код на языке ассемблера.
    # Она различает разные типы входных кодов, такие как коды присваивания, перехода, изменения, метки,
    # сравнения и печати.
    def generate_code(self):
        for code in self.arr.code:
            if(isinstance(code,AssignmentCode)):
                self.generate_assignment(code)
            elif(isinstance(code,JumbCode)):
                self.generate_jump(code)
            elif(isinstance(code,ChangeCode)):
                self.generate_small_assignment(code)
            elif(isinstance(code,LabelCode)):
                self.generate_label(code)
            elif(isinstance(code,CompareCode)):
                self.generate_compare(code);
            elif(isinstance(code,PrintCode)):
                self.generate_print(code);

    # Функция "generate_print" генерирует код для печати строки или числа.
    # Для чисел она вызывает функцию "_print_num", а для строк - функцию "_print_string".
    def generate_print(self,code):
        if(code.type=="string"):
            self.pr(f"\tmov rax,{code.value}")
            self.pr(f"\tcall _print_string")
        else:
            if(code.value in self.tempmap):
                val = self.tempmap[code.value]
            else:
                val = handle_variables(code.value)
            self.pr(f"mov rax,{val}")
            self.pr(f"\tcall _print_num")

    # Функция "generate_assignment" генерирует код для операции присваивания.
    # Она обрабатывает арифметические операции, если они есть, и сохраняет результат обратно в присвоенную переменную.
    def generate_assignment(self,code):
        left=handle_variables(code.left)
        self.pr(f"\tmov rax,{left}")
        if(code.op !=None):
            right = handle_variables(code.right)
            right = self.tempmap.get(code.right,right)
            op = operations[code.op]

            if(code.op in '+-'):
                self.pr(f"\t{op} rax,{right}")
            else:
                self.pr(f"\tmov rbx,{right}")
                self.pr(f"\t{op} rbx")

        self.pr(f"\tmov [{code.var}],rax")

    # Функция "generate_small_assignment" похожа на "generate_assignment", но не обрабатывает присваивание переменных.
    def generate_small_assignment(self,code):
        right = handle_variables(code.right)
        right = self.tempmap.get(code.right,right)
        op = operations[code.op]
        if(code.op in '+-'):
            self.pr(f"\t{op} rax,{right}")
        else:
            self.pr(f"\tmov rbx,{right}")
            self.pr(f"\t{op} rbx")
        self.pr(f"\tmov [{code.var}],rax")

    # Функция "generate_jump" генерирует инструкции перехода.
    def generate_jump(self,code):
        self.pr(f"\tjmp {code.dist}")

    # Функция "generate_label" генерирует метку для кода.
    def generate_label(self,code):
        self.pr(f'\t{code.label} : ')

    # Функция "generate_compare" генерирует инструкции для операций сравнения, таких как больше, меньше и т. д.
    def generate_compare(self,code):
        left = handle_variables(code.left)
        right = handle_variables(code.right)
        left = self.tempmap.get(code.left,left)
        right = self.tempmap.get(code.right,right)

        comp = comparisons[code.operation]
        label = code.jump
        self.pr(f"\tmov rax,{left}")
        self.pr(f"\tmov rbx,{right}")
        self.pr("\tcmp rax,rbx")
        self.pr(f"\t{comp} {label}")

    # функция "generate_functions" генерирует функции, используемые в коде,
    # включая функции печати и некоторые выделения буферов.
    def generate_functions(self):
        self.pr("""

_print_num:
    mov rcx, digitSpace
    mov rbx, 10
    mov [rcx], rbx
    inc rcx
    mov [digitSpacePos], rcx

_printRAXLoop:
    mov rdx, 0
    mov rbx, 10
    div rbx
    push rax
    add rdx, 48

    mov rcx, [digitSpacePos]
    mov [rcx], dl
    inc rcx
    mov [digitSpacePos], rcx

    pop rax
    cmp rax, 0
    jne _printRAXLoop

_printRAXLoop2:
    mov rcx, [digitSpacePos]

    mov rax, 1
    mov rdi, 1
    mov rsi, rcx
    mov rdx, 1
    syscall

    mov rcx, [digitSpacePos]
    dec rcx
    mov [digitSpacePos], rcx

    cmp rcx, digitSpace
    jge _printRAXLoop2

    ret


_print_string:
    push rax
    mov rbx, 0

_printLoop:
    inc rax
    inc rbx
    mov cl, [rax]
    cmp cl, 0
    jne _printLoop

    mov rax, 1
    mov rdi, 1
    pop rsi
    mov rdx, rbx
    syscall

    ret

        """)

    # Функция "Run" записывает выходные данные в файл, компилирует его в объектный файл,
    # связывает его в исполняемый файл и запускает сгенерированную программу.
    def Run(self):
        self.f.close()
        os.system("nasm -f elf64 output.asm")
        os.system("ld -m elf_x86_64 -s -o output output.o")
        os.system("./output")
