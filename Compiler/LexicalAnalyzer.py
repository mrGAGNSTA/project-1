# Импорт классов Token и TokenArray из модуля Tokens в пакете utils.
from utils.Tokens import Token, TokenArray

# Списки ключевых слов и операторов сравнения.
keyword = ['if', 'else', 'while','int','print',"prints",'string','float']
comparison = ["==", ">", "<", "<=", "!=", '>=']

# Словарь разделителей и их соответствующих обозначений.
delimiters = {
    '(': "L1",
    ')': "R1",
    '{': "L2",
    '}': "R2",
    ';': 'SEMICOLON',
    ',':'SEPERATOR'
}
# Список ошибочных символов.
error = ['!', '@', '$', '&', '~', '`']

# Строка разделителей и список операций.
seperate_operations="(){ }[]\t\n+-*/=><"
operations = ['+', '-', '*', '/', '=', '==', '>', '<', '!=',
            '>=', '<=','++','--']

# Словарь соответствия операторов и их типов токенов.
TT = {
    '=':'Assign',
    '<':'COMPARISON',
    '>':'COMPARISON',
    '<=':'COMPARISON',
    '>=':'COMPARISON',
    '==':'COMPARISON',
    '!=':'COMPARISON',
    '+':'ARTH',
    '-':'ARTH',
    '*':'ARTH',
    '/':'ARTH',
    '++':'ARTH',
    '--':'ARTH',
}

# Функция valid_word проверяет, является ли переданное слово допустимым,
# то есть содержит только буквы, цифры или знак подчеркивания.
def valid_word(word):
    return word.replace('.', '', 1).isdigit() or word.isalpha() or word =='_'

# Класс Lexer - основной класс лексера. Он принимает текст программы и превращает его в список токенов.

class Lexer:
    def __init__(self,file):
        self.file = list(file)+['END']
        self.array = TokenArray()
        self.cur_position=0
        self.cur_char=self.file[0]
        self.line = 1
        self.create_tokens()

# Метод next() устанавливает текущий символ и позицию на следующий символ.
    def next(self):
        if(self.cur_position+1 < len(self.file)):
            self.cur_position+=1
        self.cur_char = self.file[self.cur_position]


    # Этот метод используется для обработки операторов во входном коде.
    # Он проверяет, является ли строка, состоящая из текущего символа и предыдущих символов, оператором.
    # Если да, то он добавляет текущий символ в переменную k и переходит к следующему символу.
    # Это продолжается до тех пор, пока текущая строка не будет являться оператором.
    # Затем он создает токен t с типом оператора и его значением и добавляет его в массив токенов.
    def make_operators(self):
        k=""
        while((k+self.cur_char) in operations ):
            k+=self.cur_char
            self.next()

        t = Token(TT[k],k,self.line)
        self.array.push(t)

    # Этот метод обрабатывает разделители во входном коде.
    # Он создает токен t с типом и значением разделителя, и добавляет его в массив токенов.
    def make_delimiter(self):
        t = Token(delimiters[self.cur_char],self.cur_char,self.line)
        self.next()
        self.array.push(t)


    # Этот метод обрабатывает слова во входном коде.
    # Он проверяет, является ли текущий символ допустимым символом в слове.
    # Если это так, он добавляет текущий символ в переменную cur и переходит к следующему символу.
    # Это продолжается до тех пор, пока текущий символ не перестанет быть допустимым символом в слове.
    # Затем он проверяет, является ли текущее слово ключевым словом.
    # Если это так, то он создает токен t с типом ключевого слова и его значением и добавляет его в массив токенов.
    # В противном случае он создает токен t с типом переменной и ее значением, и добавляет его в массив токенов.
    def make_word(self):
        cur=""
        while(self.cur_char!='END' and valid_word(self.cur_char)):
            cur+=self.cur_char
            self.next()

        if(cur in keyword):
            t = Token(cur.upper(),cur,self.line)
            self.array.push(t)
        else:
            t = Token("VAR",'V'+cur,self.line)
            self.array.push(t)

    # Этот метод обрабатывает комментарии в исходном коде.
    # Он переходит к следующему символу и продолжает переходить к следующему символу,
    # пока текущий символ не станет символом '#' или не будет достигнут конец исходного кода.
    def make_comment(self):
        self.next()
        while (self.cur_char!='END' and self.cur_char!='#'):
            self.next()
        self.next()

    # Этот метод обрабатывает строки во входном коде.
    # Он переходит к следующему символу и продолжает добавлять текущий символ в переменную cur до тех пор,
    # пока текущий символ не станет '"' или не будет достигнут конец входного кода.
    # Затем он создает токен t с типом строки и ее значением и добавляет его в массив токенов.
    def make_string(self):
        self.next()
        cur=""
        while (self.cur_char!='END' and self.cur_char!='"'):
            cur+=self.cur_char
            self.next()
        self.next()
        t = Token("string",cur,self.line)
        self.array.push(t)


    # make_number - функция, которая обрабатывает числа в исходном коде.
    # Она собирает все цифры, пока не встретит нецифровой символ,
    # а затем создает токен Token типа 'FLOAT' или 'INT', в зависимости от наличия десятичной точки.
    def make_number(self):
        num = ""
        dot_count = 0

        while self.cur_char != 'END' and self.cur_char.isdigit() or self.cur_char == '.':
            if self.cur_char == '.':
                if dot_count == 1:
                    raise Exception("Too many dots in number on line {}".format(self.line))
                else:
                    dot_count = 1

            num += self.cur_char
            self.next()

        if dot_count == 1:
            t = Token('FLOAT', num, self.line)
        else:
            t = Token('INT', num, self.line)

        self.array.push(t)

    # create_tokens - функция, которая создает токены из исходного кода.
    # Она работает до тех пор, пока не достигнет конца исходного кода,
    # и вызывает соответствующую функцию для обработки каждого символа.
    def create_tokens(self):
        while(self.cur_char != "END"):
            if(self.cur_char =='\n'):
                self.line+=1
                self.next()
            elif(self.cur_char in '\t '):
                self.next()
            elif(self.cur_char == '#'):
                self.make_comment()
            elif(self.cur_char == '"'):
                self.make_string()
            elif(self.cur_char in operations):
                self.make_operators()
            elif(self.cur_char in delimiters):
                self.make_delimiter()
            elif(self.cur_char.isalpha()):
                self.make_word()
            elif(self.cur_char.isdigit()):
                self.make_number()
            else:
                raise Exception("unknown char {} in line {}".format(self.cur_char,self.line));


    # get_tokens - функция, которая возвращает массив токенов.
    def get_tokens(self):
        return self.array


