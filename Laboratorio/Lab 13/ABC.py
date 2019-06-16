from prettytable import PrettyTable
import math
import time
import datetime
import numpy as np

def function(x,y):
    return x*math.sin(4*math.pi*x) - y*math.sin(4*math.pi*y + math.pi)+1


class ABC:
    def __init__(self, function, lowlim, highlim, CS, NS, dimension, generations):
        self.function  = function
        self.CS        = CS
        self.NS        = NS
        self.dimension = dimension
        self.limit     = (self.CS*self.dimension)/2
        self.lowlim    = lowlim
        self.highlim   = highlim

        self.generations = generations

        self.best        = None
        self.bestEval    = None
        self.bestFit     = float('-inf') #Mejor fit es positivo.
        
        #Comienzo del algoritmo

        self.population      = self.generatePopulation()
        self.populationEval  = self.eval(self.population)
        self.populationFit   = self.fitness(self.populationEval)
        self.counter         = np.zeros(self.NS,dtype=np.uint16)
        self.printTable("Población Inicial",self.population,self.populationEval,self.populationFit,self.counter)

        for i in range(self.generations):
            print("-"*50); print("\nGENERACIÓN {} DE {}:".format(i+1,self.generations))
            
            #Soluciones Candidatas 1 (ABEJAS EMPLEADAS)
            self.firstCandidateSolutions()
            self.printTable("Soluciones Candidatas",self.candidates,self.candidatesEval,self.candidatesFit)
            self.keepBestCandidates()
            self.printTable("Población Actualizada",self.population,self.populationEval,self.populationFit,self.counter)
            
            #Soluciones Candidatas a partir de probabilidad. (ABEJAS OBSERVADORAS)
            self.probability()
            self.printTable("Soluciones con Probabilidad",self.population,self.populationEval,self.populationFit,self.counter,self.populationProb,self.populationProbAcum)
            self.secondCandidateSolutions()
            self.checkLimit()
            self.updateBest()
            self.printCandidate("Mejor solución",0,self.best,self.bestEval,self.bestFit)

        
    def generatePopulation(self):
        return np.array([ [ np.random.uniform(self.lowlim,self.highlim) for i in range (self.dimension) ]  for j in range (self.NS) ])
    
    def eval(self,population):
        return np.array( [ self.function(i[0],i[1]) for i in population  ]  )

    def fitness(self,population):
        return np.array( [  1/(1+i) if (i>=0) else 1 + abs(i) for i in population ]   )


    def firstCandidateSolutions(self):
        candidates = []
        for i in range( len( self.population ) ):
            k=i
            while(k==i):
                k = np.random.randint(0,self.NS)      #Solución a escoger, diferente a sí mismo.
            j   = np.random.randint(0,self.dimension) #Qué valor de dimensión a modificar.
            fi  = np.random.uniform(-1,1)             #Valor aleatorio
            print("\nSolución {}:\nk:{}\nj:{}\nfi:{}".format(i,k,j,round(fi,4)))
            v   = self.population[i][j] + fi * ( self.population[i][j]  - self.population[k][j] ) #Calculamos al valor de posición de la solución.
            sol    = np.copy(self.population[i]) #Copiamos el original para actualizar.
            sol[j] = v                           #Actualizamos el valor de posición.
            sol    = self.checkBoundaries(sol)   #Revisamos si el candidato se sale del rango.
            candidates.append(sol)               #Añadimos a lista de candidatos.
        self.candidates     = np.array(candidates)
        self.candidatesEval = self.eval(self.candidates)
        self.candidatesFit  = self.fitness(self.candidatesEval)
    

    def secondCandidateSolutions(self):
        for i in range ( self.NS  ):
            print("\nCandidata {}:".format(i+1))
            chosen = self.roulette()
            k  = chosen
            while(k == chosen):
                k = np.random.randint(0,self.NS)
            j   = np.random.randint(0,self.dimension)  #Qué valor de dimensión a modificar.
            fi  = np.random.uniform(-1,1)              #Valor aleatorio
            print("Elegido:{}\nk:{}\nj:{}\nfi:{}".format(chosen,k,j,round(fi,4)))
            v   = self.population[chosen][j] + fi * ( self.population[chosen][j]  - self.population[k][j] ) #Calculamos al valor de posición de la solución.
            sol     = np.copy(self.population[chosen]) #Copiamos el original para actualizar.
            sol[j]  = v                                #Actualizamos el valor de posición.
            sol     = self.checkBoundaries(sol)        #Revisamos si el candidato se sale del rango.
            solEval = self.eval([sol])[0]
            print("Soleval",solEval) 
            solFit  = self.fitness([solEval])[0]
            print("solfit",solFit)
            
            self.printCandidate("Candidato de la solución {}".format(chosen),chosen,sol,solEval,solFit)

            if (  solFit < self.populationFit[chosen] ):
                print("Candidato {}({}) es mejor que solución antigua {}({})".format( sol.round(decimals=4),round(solFit,4),self.population[chosen].round(decimals=4),round(self.populationFit[chosen],4 )))
                self.population[chosen]     = sol
                self.populationEval[chosen] = solEval
                self.populationFit[chosen]  = solFit
                self.counter[chosen]        = 0
            else:
                self.counter[i]+= 1
                print("Candidato {}({}) no es mejor que solución antigua {}({})".format( sol.round(decimals=4),round(solFit,4),self.population[chosen].round(decimals=4),round(self.populationFit[chosen],4 )))
            
            self.printTable("Población Actualizada",self.population,self.populationEval,self.populationFit,self.counter)


    def keepBestCandidates(self):
        for i in range ( len ( self.population ) ):
            if ( self.candidatesFit[i] < self.populationFit[i] ):
                print("Candidato {}({}) es mejor que solución antigua {}({})".format( self.candidates[i].round(decimals=4),round(self.candidatesFit[i],4),self.population[i].round(decimals=4),round(self.populationFit[i],4) ))
                self.population[i]     = self.candidates[i]
                self.populationEval[i] = self.candidatesEval[i]
                self.populationFit[i]  = self.candidatesFit[i]
                self.counter[i]        = 0
            else:
                self.counter[i]+= 1
                print("Candidato {}({}) no es mejor que solución antigua {}({})".format( self.candidates[i].round(decimals=4),round(self.candidatesFit[i],4),self.population[i].round(decimals=4),round(self.populationFit[i],4) ))
        self.candidates = self.candidatesEval = self.candidatesFit = None
         

    def checkLimit(self):
        for i in range ( len( self.population ) ):
            if ( self.counter[i] > self.limit ):
                print("Se ha llegado al límite en la solución {}. Reiniciando".format(self.population[i]))
                self.population[i]     = np.array([ np.random.uniform(self.lowlim,self.highlim) for i in range (self.dimension) ])
                self.populationEval[i] = self.eval( [self.population[i]] )[0] 
                self.populationFit[i]  = self.fitness( [self.populationEval[i]] )[0]

    def updateBest(self):
        bestLocal = self.populationFit.argmax()
        if( self.populationFit[bestLocal] > self.bestFit  ):
            print("Se actualiza la mejor solución")
            self.best     = self.population[bestLocal]
            self.bestEval = self.populationEval[bestLocal]
            self.bestFit  = self.populationFit[bestLocal]
        else:
            print("Se mantiene la mejor solución")
            

    def probability(self):
        self.populationProb     = self.populationFit/sum(self.populationFit)
        self.populationProbAcum = np.cumsum(self.populationProb)

    def roulette(self):
        rand = np.random.uniform(0,1)
        for i in range( self.NS ):
            if(self.populationProbAcum[i] > rand):
                return i

    def checkBoundaries(self,solution):
        checked = False
        for i in range ( len( solution ) ):
            if( solution[i] > self.highlim or solution[i] < self.lowlim ):
                checked = True
                solution[i] = np.random.uniform(self.lowlim,self.highlim)
        if(checked): print("La solución está fuera de rango, reiniciando")

        return solution


    #Funcion para imprimir la tabla suponiendo que es de 2 dimensiones.
    def printTable(self,titulo,pop,eval,fit,cont=[],prob=[],probacum=[]):
        print("\n"+titulo)
        table = PrettyTable()
        if( len( cont ) <= 0 ):
            table.field_names = ["#","x1","x2","Evaluated","Fitness"]
            for i in range(len(pop)):
                vals = [i+1, pop[i][0].round(decimals=4),pop[i][1].round(decimals=4),eval[i].round(decimals=4), fit[i].round(decimals=4) ]
                table.add_row( vals )
            
        elif(  len ( cont ) > 0 and len ( prob ) <= 0 ):
            table.field_names = ["#","x1","x2","Evaluated","Fitness","Cont"]
            for i in range(len(pop)):
                vals = [i+1, pop[i][0].round(decimals=4),pop[i][1].round(decimals=4),eval[i].round(decimals=4), fit[i].round(decimals=4),cont[i] ]
                table.add_row( vals )

        elif (  len ( prob ) > 0 ):
            table.field_names = ["#","x1","x2","Evaluated","Fitness","Probability","Accum Prob","Cont"]
            for i in range(len(pop)):
                vals = [i+1, pop[i][0].round(decimals=4),pop[i][1].round(decimals=4),eval[i].round(decimals=4), fit[i].round(decimals=4),prob[i].round(decimals=4),probacum[i].round(decimals=4),cont[i] ]
                table.add_row( vals )
        
        
        print (table.get_string(header=True, border=True))

    #Funcion para imprimir el candidato
    def printCandidate(self,titulo,num,cand,eval,fit):
        print("\n"+titulo)
        table = PrettyTable()
        table.field_names = ["#","x1","x2","Evaluated","Fitness"]
        vals = [num, cand[0].round(decimals=4),cand[1].round(decimals=4),eval.round(decimals=4), fit.round(decimals=4) ]
        table.add_row( vals )
        print (table.get_string(header=True, border=True))

def main():
    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    comienzo = time.time()
    bees     = ABC(function,lowlim = -1, highlim = 2,  CS = 6, NS = 3, dimension = 2, generations=100)
    final    = time.time()
    print("\nFIN DEL PROCESO", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print("Tiempo:",final-comienzo)

if __name__ == '__main__':
    main()
    