import numpy as np
import secrets
import regex
import time
import datetime
import sys
import copy 


class PromGen:
    def __init__(self,input,output,populationSize,probRep,probCross,probMut,generations,error):
        self.input          = np.array(input)
        self.output         = np.array(output)
        self.populationSize = populationSize
        self.probRep        = probRep
        self.probCross      = probCross
        self.probMut        = probMut
        self.generations    = generations
        self.error          = error
        self.variable       = ['x']
        self.terminal       = ['-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5']
        self.functions      = ['*','/','+','-']
        
        self.population = self.generatePopulation()
        self.populationInitial = copy.copy(self.population)
        print("Población Inicial:\n", self.population )
        # generation = 0
        # while True:
        for generation in range(0,self.generations):
            print("\nGENERACION:",generation+1)
            self.populationFit = self.fit(self.population)
            print("Población:\n",self.population)
            print("Fitness:\n",self.populationFit)
            self.probability()
            newPopulation = []

            while(len(newPopulation) <= self.populationSize ):
            
                rand = np.random.uniform(0,1)
                print("\nNúmero Aleatorio: ", rand," entonces:",end = '')                    

                if(rand < self.probCross/100):
                    print(" Se cruza\n")
                    parent1 = self.population[self.roulette()]
                    parent2 = self.population[self.roulette()]
                    child1,child2 = self.crossover(parent1,parent2)
                    newPopulation.append(child1)
                    newPopulation.append(child2)
                elif(rand < (self.probCross+self.probMut)/100):
                    print(" Se Muta\n")
                    parent1 = self.population[self.roulette()]
                    child1 = self.mutation(parent1)
                    newPopulation.append(child1)
                else:
                    print(" Se reproduce\n")
                    parent1 = self.population[self.roulette()]
                    print("Padre1/Hijo1:",parent1)
                    newPopulation.append(parent1)
                
            
            newPopulation        = np.array(newPopulation)
            print("\nFitness newPopulation ",generation+1, " :")
            newFitness           = self.fit(newPopulation)
            self.population      = np.concatenate((self.population,newPopulation))
            self.populationFit   = np.concatenate((self.populationFit,newFitness))
            newIndeces           = np.argsort(self.populationFit)[:self.populationSize]
            self.population      = self.population[newIndeces]
            print("\nNueva población:", self.population)
            
            # if( self.populationFit[newIndeces[0]] < self.error ):
            #     break
            # generation+=1

        print("Fitness:",self.fit(self.population))
        print("\nNueva población:", self.population)
            

    def generatePopulation(self):
        population = []
        for i in range (self.populationSize):
            population.append(self.generatePreorder())       
        return population

    def chooseVarTerm(self):
        chooser = np.random.randint(2)
        if(chooser):
            return np.random.choice(self.variable)
        return np.random.choice(self.terminal)

    def generatePreorder(self,level=1):
        preorder = ''.join('('+np.random.choice(self.functions)+' ('+np.random.choice(self.functions)+' '+self.chooseVarTerm()+' '+self.chooseVarTerm()+')'\
                    +' ('+np.random.choice(self.functions)+' '+self.chooseVarTerm()+' '+self.chooseVarTerm()+'))')
        return preorder

    # Código de:
    # http://aguo.us/writings/prefix-notation.html
    # Modificado para aceptar numeros negativos y decimales.
    def calcEval(self,exp):
        m = regex.match(r'\(([-+\/\*]) ((?R)) ((?R))\)|(-?\d+\.?[\d+]?)|[-+\/\*]', exp)
        try:
            if all(map(m.group, [1, 2, 3])):  # exp is a procedure call
                return eval(' '.join([str(self.calcEval(m.group(i))) for i in [2, 1, 3]]))
            return eval(exp) if m.group(4) else exp  # exp is a number / an operator
        except AttributeError:
            sys.exit("EL GEN NO ESTÁ CORRECTO: "+exp)
            

    # Reemplazamos el valor de x con un valor y lo evaluamos.
    def replaceEval(self,exp,val):
        prev = exp.replace('x',val)
        return self.calcEval(prev)

    def ECM(self,gen):
        difs = []
        for i in range(0,len(self.input)):
            f = self.replaceEval(gen,str(self.input[i]))
            dif = abs(f-self.output[i])
            difs.append(dif)
            #print("%10.5f%10.5f" % (f,dif)  )
        sum = 0
        for i in range(0,len(difs)):
            sum += pow(difs[i],2)
        ecm = sum/len(difs)
        print("ECM:",ecm,"\n")
        return ecm 

    # Realizamos el ECM de la población
    # caso exista una división por 0, generamos otro gen.
    def fit(self,population):
        fit = []
        modif = 0
        mod = False
        for i in range(len(population)):
            print(i,": calculando con ",population[i])
            while True:
                if(mod):
                    new = self.generatePreorder()
                    print("Anterior:",population[i])
                
                    tmp = list(population[:i])
                    tmp.extend([new])
                    tmp.extend(list(population[i+1:]))
                    population = tmp
                    
                    print("Nuevo valor:",population[i])
                    
                    mod=False
                    modif+=1
                try:
                    ecm = self.ECM( population[i])
                    break
                except ZeroDivisionError:
                    print(population[i]," evaluado da división por 0, generando nuevo valor de pos",i)
                    mod=True
                
            fit.append(ecm)
        print("Se realizaron ", modif, " modificaciones a la población.")
        return np.array(fit)

    def probability(self):
         #Minimizamos complementando los valores al valor máximo
        prob = self.populationFit.max() - self.populationFit +1    
        prob = prob/sum(prob)
        print("Probabilidad:",prob)
        self.populationProb = np.cumsum(prob)
        print("Probabilidad acum:",self.populationProb)

    def roulette(self):
        rand = np.random.uniform(0,1)
        for i in range(0,self.populationSize):
            if (self.populationProb[i] > rand):
                return i

    # Utilizamos el regex para dividir los padres rápidamente 
    # (añadimos detectar valor x).
    def crossover(self,parent1,parent2):
        print("Padre 1: ", parent1, " -- ","Padre 2:",parent2)
        p1 = regex.match(r'\(([-+\/\*]) ((?R)) ((?R))\)|(-?[x\d]+\.?[\d+]?)|[-+\/\*]', parent1)
        p2 = regex.match(r'\(([-+\/\*]) ((?R)) ((?R))\)|(-?[x\d]+\.?[\d+]?)|[-+\/\*]', parent2)
        
        child1 = "("+p1.group(1)+" "+p1.group(2)+" "+p2.group(3)+")"
        child2 = "("+p2.group(1)+" "+p2.group(2)+" "+p1.group(3)+")"
        print("Hijo 1: ", child1, " -- ","Hijo 2:",child2)
        return child1, child2
    


    def mutation(self,gen):
        print("Mutamos:",gen)
        g = regex.match(r'\(([-+\/\*]) ((?R)) ((?R))\)|(-?[x\d]+\.?[\d+]?)|[-+\/\*]', gen)
        pos = np.random.randint(1,4)
        group = g.group(pos).replace('(','').replace(')','')
        group = group.split()
        val = secrets.choice(group)
        print("Mutaremos:",val)
        if(val in self.functions):
            repl = secrets.choice(self.functions)
        else:
            repl = self.chooseVarTerm()
            
        print("Con:",repl)
        gs = [g.group(1),g.group(2),g.group(3)]
        
        gs[pos-1] = g.group(pos).replace(val,repl,1)
        
        child1 = "("+gs[0]+" "+gs[1]+" "+gs[2]+")"
        print("Mutado:",child1)
        return child1




def main():
    input   = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    output  = [0,0.005,0.02,0.045,0.08,0.125,0.18,0.245,0.32,0.405]

    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    
    comienzo = time.time()
    gen = PromGen(input,output,populationSize = 20,probRep = 10, probCross = 40,probMut = 50,generations = 700, error = 10**-10)
    final    = time.time()

    print("\nFIN DEL PROCESO", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print("Tiempo:",final-comienzo)

    print("Población inicial:",gen.populationInitial)

if __name__ == "__main__":
    main()