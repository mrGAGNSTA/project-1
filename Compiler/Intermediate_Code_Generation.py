from utils.Tokens import *
from utils.TreeNodes import *
from utils.intermediatecode import *

# TCounter класс используется для генерации уникальных имен временных переменных путем
# добавления к символьному префиксу их номера (счетчика)
class TCounter:
    def __init__(self,char):
        self.counter = 1;
        self.char = char

    def increase(self):
        self.counter+=1;

    def reset(self):
        self.counter=1;

    def get(self):
        return f'{self.char}{self.counter}';


# Класс IntermidateCodeGeneration принимает синтаксическое дерево в качестве входного параметра,
# инициализирует различные переменные, такие как счетчик временной переменной (t), счетчик меток (l)
# и счетчик строковых констант (s).
class IntermidiateCodeGeneration:
    def __init__(self, tree_root):
        self.root = tree_root
        self.code = InterCodeArray()
        self.t = TCounter('T')
        self.l = TCounter('L')
        self.s = TCounter('S')
        self.identifiers = {}
        self.constants = {}
        self.execute_statement(tree_root)


    # Метод execute_exp генерирует код для арифметических выражений путем рекурсивной оценки левых
    # и правых подвыражений. Он генерирует инструкцию присваивания, которая присваивает результат
    # выражения новой временной переменной.
    def execute_exp(self, root):
        if isinstance(root, IdentifierNode) or isinstance(root, NumberNode):
            return root.get_num()
        else:
            left = self.execute_exp(root.left)
            op = root.op_tok.value
            right = self.execute_exp(root.right)

            if isinstance(left, float) or isinstance(right, float):
                cur_t = self.t.get()
                self.identifiers[cur_t] = 'float'
                self.t.increase()
                self.code.append(AssignmentCode(cur_t, str(left), op, str(right)))
                return cur_t
            else:
                cur_t = self.t.get()
                self.identifiers[cur_t] = 'int'
                self.t.increase()
                self.code.append(AssignmentCode(cur_t, left, op, right))
                return cur_t

    def execute_assignment(self,root):
        right = self.execute_exp(root.expression)
        self.code.append(AssignmentCode(root.identifier.value,right))


    # Методы execute_if и execute_while генерируют код для конструкций if-else и циклов while соответственно.
    def execute_if(self,root):
        self.execute_condition(root.if_condition);

        body = self.l.get();self.l.increase()
        end_if = self.l.get();self.l.increase()

        if(root.else_body):
            goto_else_end = self.l.get();self.l.increase()
            self.code.append(JumbCode(goto_else_end))
            self.code.append(LabelCode(body))
            self.execute_statement(root.if_body)
            self.code.append(JumbCode(end_if))
            self.code.append(LabelCode(goto_else_end))
            self.execute_statement(root.else_body)
            self.code.append(LabelCode(end_if))
        else:
            self.code.append(JumbCode(end_if))
            self.code.append(LabelCode(body))
            self.execute_statement(root.if_body)
            self.code.append(LabelCode(end_if))

    def execute_while(self,root):
        start_loop = self.l.get();self.l.increase()
        self.code.append(LabelCode(start_loop))

        self.execute_condition(root.condition);
        body = self.l.get();self.l.increase()

        end_while = self.l.get();self.l.increase()

        self.code.append(JumbCode(end_while))
        self.code.append(LabelCode(body))
        self.execute_statement(root.body)
        self.code.append(JumbCode(start_loop))
        self.code.append(LabelCode(end_while))

    # Метод execute_condition генерирует код для операций сравнения.
    def execute_condition(self,root):
        left = self.execute_exp(root.left_expression)
        compare = root.comparison.value
        right = self.execute_exp(root.right_expression)

        body = self.l.get()

        self.code.append(CompareCode(left,compare,right,body))

    # Метод execute_print генерирует код для инструкций вывода print. Если аргументом является строка,
    # он генерирует новую строковую константу и добавляет ее в список строковых констант.
    # Если аргументом является целочисленное выражение, он вычисляет выражение и генерирует инструкцию вывода
    # с результатом.
    def execute_print(self, root):
        if root.type == "string":
            self.constants[self.s.get()] = root.value
            right = self.s.get()
            self.s.increase()
            self.code.append(PrintCode("string", right))
        elif root.type == "int":
            right = self.execute_exp(root.value)
            self.code.append(PrintCode("int", right))
        elif root.type == "float":
            right = self.execute_exp(root.value)
            self.code.append(PrintCode("float", right))

    # Метод execute_declaration генерирует код для объявления переменной.
    # Он добавляет каждый объявленный идентификатор в словарь идентификаторов вместе с его типом.
    def execute_declaration(self,root):
        type = root.declaration_type
        for i in root.identifiers:
            self.identifiers[i.value]=type.value

    # Метод execute_statement выполняет соответствующий метод в зависимости от типа инструкции,
    # разобранной в синтаксическом дереве.
    def execute_statement(self,root):
        if(root==None):
            return ;

        if(isinstance(root,Statement)):
            self.execute_statement(root.left)
            self.execute_statement(root.right)
        elif(isinstance(root,IfStatement)):
            self.execute_if(root)
        elif(isinstance(root,WhileStatement)):
            self.execute_while(root)
        elif(isinstance(root,PrintStatement)):
            self.execute_print(root)
        elif(isinstance(root,Declaration)):
            self.execute_declaration(root)
        elif(isinstance(root,Assignment)):
            self.execute_assignment(root)


    # Метод get_code возвращает сгенерированный промежуточный код, а также словари типов
    # идентификаторов и строковых констант.
    def get_code(self):
        return self.code,self.identifiers,self.constants
