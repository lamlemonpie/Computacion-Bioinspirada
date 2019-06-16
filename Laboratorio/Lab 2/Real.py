import random
import numpy as np
import time
import datetime


def func(gen):
    return gen[0]-gen[1]+gen[2]-gen[3]+gen[4]


class GenAlgo:
    def __init__(self,fit,population_size,genotype_size,probCross,probMut,generations):
        self.fit             = fit
        self.population_size = population_size
        self.genotype_size   = genotype_size
        self.probCross       = probCross
        self.probMut         = probMut
        self.generations     = generations
        self.tourmnt         = 3
        self.genMinRange     = -100
        self.genMaxRange     = 100
        self.betha           = -0.5
        self.bethaMin        = -0.5
        self.bethaMax        = 1.5

        self.generatePopulation()
        print(self.population)
        for generation in range(0,self.generations):
            print("\n\nGENERATION:",generation+1)
            self.fitness = self.fitn(self.population)
            newPopulation = []
            for i in range(0,self.population_size):
                print("\n")
                parent1 = self.tournament()
                print("Padre1:",parent1)
                parent2 = self.tournament()
                print("Padre2:",parent2)
                print("Cruzamiento:",i+1)
                child = self.crossover(parent1,parent2)
                print("Nuevo hijo:", child)
                newPopulation.append(child)
            newPopulation   = np.array(newPopulation)
            newFitness      = self.fitn(newPopulation)
            self.population = np.concatenate((self.population,newPopulation))
            self.fitness    = np.concatenate((self.fitness,newFitness))
            newIndeces      = np.argsort(self.fitness)[-self.population_size:]
            self.population = self.population[newIndeces]
            print("Nueva población:", self.population)

    def generatePopulation(self):
        self.population = np.array([[np.random.uniform(self.genMinRange,self.genMaxRange) for i in range(self.genotype_size)] for j in range(self.population_size)])

    def fitn(self,population):
        return np.array([ self.fit(i) for i in population ])


    def tournament(self):
        indices = np.random.randint(0,self.population_size,self.tourmnt)
        print("Tomamos:",indices)
        chosen  = np.take(self.fitness, indices)
        print("Elegidos:",chosen)
        max     = np.argmax(chosen)
        return self.population[max]

    def blx(self,a,b,bet):
        return a + bet*(b - a)

    def crossover(self,parent1,parent2):
        rand0 = np.random.uniform(0,1)
        if(rand0 < self.probCross/100): #Probabilidad para cruzarse
            child = self.blx(parent1,parent2,self.betha)
            while self.checkLimits(child):
                betha = np.random.uniform(self.bethaMin,self.bethaMax)
                print("El hijo se pasa de límite, betha=",betha)
                child = self.blx(parent1,parent2,betha)
                #self.checkLimits(child)
        else:
            child = parent1
        child = self.checkMutation(child)

        return child

    def checkLimits(self,child):
        for i in range (0,len(child)):
            if( (child[i] > self.genMaxRange) or (child[i] < self.genMinRange)):
                return True # No está en limite
        return False # Si está en limite

    def checkMutation(self,child):
        rand = np.random.uniform(0,1)
        #Probabilidad de mutar
        if(rand < self.probMut/100):
            print("Mutando:", child)
            pos        = random.randrange(0,self.genotype_size)
            nuevoVal   = np.random.uniform(self.genMinRange,self.genMaxRange)
            child[pos] = nuevoVal
            print("Mutado:", child)
        return child

    def newBest(self):
        fitness = fit

def main():
    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

    comienzo = time.time()
    genetic  = GenAlgo(func,population_size=10,genotype_size=5,probCross=90,probMut=10,generations=1000)
    final    = time.time()

    print("\nFIN DEL PROCESO")
    print("Tiempo:",final-comienzo)


if __name__ == '__main__':
    main()
