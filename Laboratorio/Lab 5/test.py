import numpy as np
import regex

variable       = ['x']
terminal       = ['-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5']
functions      = ['*','/','+','-']   

   
def chooseVarTerm():
    chooser = np.random.randint(2)
    if(chooser):
        return np.random.choice(variable)
    return np.random.choice(terminal)

def generatePreorder(level=1):
    if(level == 1):
        fuct    = np.random.choice(functions)
        return '('+fuct+' '+generatePreorder(0)+' '+generatePreorder(0)+')'
    else:
        fuct    = np.random.choice(functions)
        left    = chooseVarTerm()
        right   = chooseVarTerm()
        return '('+fuct+' '+left+' '+right+')'

def checkGen(exp):
    m = regex.match(r'\(([-+\/\*]) ((?R)) ((?R))\)|(-?[x\d]+\.?[\d+]?)|[-+\/\*]', exp)
    try:
        if all(map(m.group, [1, 2, 3])):  # exp is a procedure call
            print("todo bien", exp)
            return 0
    except AttributeError:
            print("todo mal: ",exp)
            return 1


    # def mutation(self,gen):
    #     print("Mutamos:",gen)
    #     tmp  = gen+""
    #     tmp  = tmp.replace('(','')
    #     tmp  = tmp.replace(')','')
    #     vals = tmp.split()
    #     val  = secrets.choice(vals)
    #     if(val in self.variable):
    #         repl = secrets.choice(self.variable)
    #     elif(val in self.functions):
    #         repl = secrets.choice(self.functions)
    #     else:
    #         repl = secrets.choice(self.terminal)
    #     print("val:",val)
    #     print("repl:",repl)
    #     child1 = gen.replace(val,repl,1)
    #     print("Mutado:",child1)
    #     return child1
malos = 0
for i in range(0,5000):
    val = generatePreorder()
    print("val:",val)
    malos += checkGen(val)
print("Malos:",malos)