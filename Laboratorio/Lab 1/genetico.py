import random
import numpy as np
import time
import datetime

def fitness(x):
    return -pow(x,2)-6*x+1


class GeneticAlgo:
    def __init__(self,fitness,population_size,genotype_size,cross,probCross,probMut,generations):
            self.fitness         = fitness
            self.population_size = population_size
            self.genotype_size   = genotype_size
            self.cross           = cross
            self.probCross       = probCross
            self.probMut         = probMut
            self.generations     = generations

            self.generatePopulation()
            print("\nGENERATION 0:",self.population)
            print( [self.fixSize(bin(n)[2:]) for n in self.population])
            for generation in range(0,self.generations):
                print("\nGENERATION:",generation+1)
                self.probability()
                for i in range(0,self.population_size//2):
                    parent1 = self.population[self.roulette()]
                    parent2 = self.population[self.roulette()]
                    print("Cruzamiento:",i+1)
                    child1,child2 = self.crossover(parent1,parent2)
                    self.population = np.append(self.population,[child1,child2])

                #Guardamos los mejores n para la siguiente generación
                self.population.sort()
                self.population = self.population[-self.population_size:]
                print("Nueva Población:",self.population)
                print( [self.fixSize(bin(n)[2:]) for n in self.population])


    def generatePopulation(self):
        self.population = np.random.randint(0,pow(2,self.genotype_size)-1,self.population_size)
        #print(self.population)

    def probability(self):

        fitness_applied       = fitness(self.population)
        print("Fitness:",fitness_applied)
        #normalizamos
        fitness_applied          = fitness_applied+abs(min(fitness_applied))+1
        print("FitnessNorm:",fitness_applied)
        #calculamos la probabilidad y la probabilidad acumulada
        self.population_prob  = (fitness_applied/sum(fitness_applied))
        print("Probability:",self.population_prob)
        self.population_prob  = np.cumsum(self.population_prob)
        print("Probability acum:",self.population_prob)

    def roulette(self):
        rand = np.random.uniform(0,1)
        for i in range(0,self.population_size):
            if (self.population_prob[i] > rand):
                return i

    def crossover(self, parent1, parent2):
        rand0 = np.random.uniform(0,1)
        if(rand0 < self.probCross/100): #Probabilidad para cruzarse
            p1     = self.fixSize(bin(parent1)[2:])
            p2     = self.fixSize(bin(parent2)[2:])
            print("Padre 1: ", p1, " -- ","Padre 2:",p2)
            child1 = p1[:self.cross] + p2[self.cross:]
            child2 = p2[:self.cross]  + p1[self.cross:]
            print("Hijo 1: ", child1, " -- ","Hijo 2:",child2)
            child1 = int(child1,2)
            child2 = int(child2,2)
            #Probabilidad de mutar para cada hijo
            child1 = self.checkMutation(child1)
            child2 = self.checkMutation(child2)

        else:
            print("Hijos iguales a padres")
            child1,child2 = parent1,parent2
            print("Hijo 1: ", bin(child1)[2:], " -- ","Hijo 2:",bin(child2)[2:])
        return child1,child2

    def checkMutation(self,genotype):
        rand = np.random.uniform(0,1)
        #Probabilidad de mutar
        if(rand < self.probMut/100):
            genotype = self.mutate(genotype)
        return genotype

    #https://wiki.python.org/moin/BitManipulation
    #Modificamos el bit aleatorio.
    def mutate(self,genotype):
        posMut = random.randint(0,self.genotype_size-1)
        print("Mutando:",bin(genotype)[2:], " - Pos:",posMut)
        #Creamos una mascara con el bit de posicion
        mask = 1 << (posMut)
        genotype = genotype^mask
        print("Mutado:",bin(genotype)[2:])
        return (genotype)

    #Para hacer el cruzamiento ambos padres deben de ser igual tamaño
    #Algunos numeros al tener 0 a la izquierda, omiten estos
    #Añadiremos 0 para poder hacer el cruzamiento correctamente.
    def fixSize(self,genotype):
        if(len(genotype)==self.genotype_size):
            return genotype
        else:
            remaining = self.genotype_size - len(genotype)
            return '0'*remaining + genotype


def main():

    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

    comienzo = time.time()
    genetic  = GeneticAlgo(fitness,population_size=6,genotype_size=6,cross=2,probCross=90,probMut=10,generations=10)
    final    = time.time()

    print("\nFIN DEL PROCESO")
    print("Tiempo:",final-comienzo)

if __name__ == '__main__':
    main()
