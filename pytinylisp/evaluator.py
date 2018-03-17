#coding=utf-8

import operator as op
from functools import reduce


def preprocess(code):
    chars = ["(", ")", "'", "[", "]"]
    for char in chars:
        code = code.replace(char, " {} ".format(char))
    return code


def tokenize(code):
    return code.split()


class LispOperator(object):
    @staticmethod
    def add(*params):
        return reduce(lambda a, b: a + b, params)

    @staticmethod
    def minus(*params):
        return params[0] - params[1]

    @staticmethod
    def multiply(*params):
        return reduce(lambda a, b: a*b, params)


    @staticmethod
    def car(*params):
        return params[0]


    @staticmethod
    def cdr(*params):
        return params[1:]

    @staticmethod
    def cons(*params):
        if len(params) != 2:
            raise Exception("cons: arity mismatch")
        return (params[0], params[1])


class Environment(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.var_dict = {}

        if parent is None:
            self.init_top()

    def lookup(self, name):
        if name in self.var_dict:
            return self.var_dict[name]
        else:
            if self.parent is None:
                raise Exception("variable not defined: {}".format(name))
            else:
                return self.parent.lookup(name)

    def set(self, name, value):
        self.var_dict[name] = value

    def init_top(self):
        self.var_dict['+'] = LispOperator.add
        self.var_dict['-'] = LispOperator.minus
        self.var_dict['*'] = LispOperator.multiply
        self.var_dict['/'] = op.truediv


        self.var_dict['car'] = LispOperator.car
        self.var_dict['cdr'] = LispOperator.cdr
        self.var_dict['cons'] = LispOperator.cons

        self.var_dict['<'] = op.lt
        self.var_dict['>'] = op.gt
        self.var_dict['='] = op.eq

def parse(token_stack):
    token = token_stack.pop()
    if token == '[':
        node = []
        while token_stack[-1] != ']':
            node.append(parse(token_stack))
        token_stack.pop()
    elif token == '(':
        # node = [token_stack.pop()]
        node = []
        while token_stack[-1] != ')':
            node.append(parse(token_stack))
        token_stack.pop()
    elif token == "'":
        # if token_stack[-1] != '(':
        #     raise Exception('bad syntax')
        node = ["quote"] + [parse(token_stack)]
    else:
        node = token
    return node



def isnumber(s):
    try:
        float(s)
        return True
    except:
        return False



def make_lambda(param_names, body_node, env):
    def new_func(*params):
        new_env = Environment(parent=env)
        for i, param_name in enumerate(param_names):
            new_env.set(param_name, params[i])
        return eval_lisp(body_node, new_env)
    return new_func

def eval_lisp(node, env):
    if not isinstance(node, list):
        if isnumber(node):
            return float(node)
        else:
            return env.lookup(node)
    if node[0] == 'quote':
        if isnumber(node[1]):
            return float(node[1])
        else:
            return node[1]
    elif node[0] == 'variable':
        return env.lookup(node[1])
    elif node[0] == 'begin':
        for child in node[1:-1]:
            eval_lisp(child, env)
        return eval_lisp(node[-1], env)
    elif node[0] == 'display':
        params = [eval_lisp(child, env) for child in node[1:]]
        print(*params)
        return None
    elif node[0] == 'if':
        if eval_lisp(node[1], env):
            return eval_lisp(node[2], env)
        else:
            if len(node) == 4:
                return eval_lisp(node[3], env)
            else:
                return None
    elif node[0] == 'define':
        if isinstance(node[1], list):
            # function
            env.set(node[1][0], make_lambda(node[1][1:], node[2], env))
        else:
            # variable
            env.set(node[1], eval_lisp(node[2], env))
        return None
    elif node[0] == 'let':
        new_env = Environment(parent=env)
        for local_bind_tuple in node[1]:
            new_env.set(local_bind_tuple[0], eval_lisp(local_bind_tuple[1], env))
        for body in node[2:-1]:
            eval_lisp(body, new_env)
        return eval_lisp(node[-1], new_env)
    elif node[0] == 'lambda':
        return make_lambda(node[1], node[2], env)
    else:
        func_name = node[0]
        params = [eval_lisp(child, env) for child in node[1:]]
        return env.lookup(func_name)(*params)





# code = "(begin (define (f x) (+ x 10.5)) (define x 70) (f 10) (display 'abc) (display 5))"


with open("code.rkt", "r", encoding="utf-8") as f:
    code = f.read()
# code = "(begin (define x (cons 3 5)) (display (cdr x)))"

preprocessed_code = preprocess(code)
tokens = tokenize(preprocess(code))
token_stack = list(reversed(tokens))

node = parse(token_stack)
# print(node)
env = Environment()
print(eval_lisp(node, env))
# print(env.var_dict)

# print(tokens)