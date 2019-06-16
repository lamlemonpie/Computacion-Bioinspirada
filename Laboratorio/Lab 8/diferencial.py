import math
import time
import datetime
import numpy as np

def function(x,y):
    return x*math.sin(4*math.pi*x) - y*math.sin(4*math.pi*y + math.pi)+1

class Diferencial:
    def __init__(self,function,populationSize,F,CR,generations):
        self.min            = -1
        self.max            = 2
        self.function       = function
        self.populationSize = populationSize
        self.F              = F
        self.CR             = CR
        self.generations    = generations


        self.population = self.generatePopulation()
        print("Población Inicial:\n",self.population,"\n")
        
        for i in range(self.generations):
            print("\nGENERACIÓN ", i+1)
            self.fitness    = self.fit(self.population)
            print("Fitness:\n",self.fitness,"\n")
            newpopulation = []
            targetPos = 0 #posición del target vector.
            while(len(newpopulation) < self.populationSize ):
                bucle = True
                while(bucle):
                    # Primeros 3 para mutar.
                    indivs_index = self.select_indiv()
                    print("Se eligieron: ",indivs_index)
                    indivs       = self.population[indivs_index]
                    v            = self.mutation(indivs[2],indivs[0],indivs[1])
                    print("Mutación: ",v)
                    trialVector  = self.crossover(v, self.population[targetPos])
                    print("Trial Vector: ", trialVector)
                    bucle        = self.checkBoundaries(trialVector)
                    if(bucle == True):
                        print("Trial Vector fuera de limites: ",trialVector,"\nReintentando.")


                fitTV        = self.fit([trialVector])
                # Comparamos si el fitness nuevo es mejor que el fitness del TargetV.
                if( fitTV > self.fitness[ targetPos ]):
                    print("Se añade el Trial Vector")
                    newpopulation.append(trialVector)
                else:
                    print("Sobrevive el Target Vector")
                    newpopulation.append( self.population[targetPos] )
                targetPos+=1
                print("\n")
                

            self.population = np.array(newpopulation)
            print("Nueva Población:\n",self.population)

        self.fitness = self.fit(self.population)
        maximum = np.argsort(self.fitness)[-1]
        self.best = self.population[maximum]
        print("El máximo es: ", self.best, " con: ",self.fitness[maximum])



    def generatePopulation(self):
        return np.array([[np.random.uniform(self.min,self.max) for i in range(2)]for j in range(self.populationSize)])

    def fit(self,population):
        return np.array([self.function(vals[0],vals[1]) for vals in population])
        
    def select_indiv(self):
        return np.array([np.random.randint(self.populationSize)  for i in range (3) ])

    def mutation(self,v3,v1,v2):
        return v3 + (self.F * (v1 - v2))

    def crossover(self,v,targetVector):
        for i in range (len(v)):
            rand = np.random.uniform(0,1)
            if(rand < self.CR):
                targetVector[i] = v[i]
        return targetVector                

    #Si el gen está fuera de rango retorna True para volver a calcular nuevamente.
    def checkBoundaries(self,gen):
        for i in range(len(gen)):
            if( (gen[i] < self.min) or (gen[i] > self.max)):
                return True
        return False

        

def main():
    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    comienzo = time.time()
    gen      = Diferencial(function,populationSize = 50,F = 0.5, CR = 0.9,generations = 80)
    final    = time.time()
    print("\nFIN DEL PROCESO", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    print("Tiempo:",final-comienzo)

if __name__ == "__main__":
    main()