import random
import secrets
import numpy as np
import time
import datetime


class GeneticAlgo:
    def __init__(self,caminos,population_size,probCross,probMut,generations):
        self.population_size = population_size
        self.caminos         = caminos
        self.genotype_size   = len(caminos[0])
        self.probCross       = probCross
        self.probMut         = probMut
        self.generations     = generations

        self.generateDictionary()
        self.generatePopulation()
        print("Población:",self.population)
        for generation in range(0,self.generations):
            print("\nGENERACION:",generation+1)
            self.fitPopulation = self.fitness(self.population)
            print("Fitness:",self.fitPopulation)
            self.probability()
            newPopulation = []
            for i in range(0,self.population_size//2):
                parent1 = self.population[self.roulette()]
                parent2 = self.population[self.roulette()]
                print("Cruzamiento:",i+1)
                print("Padre 1: ", parent1, " -- ","Padre 2:",parent2)
                child1,child2 = self.crossover(parent1,parent2)
                newPopulation.append(child1)
                newPopulation.append(child2)
            newPopulation   = np.array(newPopulation)
            newFitness      = self.fitness(newPopulation)
            self.population = np.concatenate((self.population,newPopulation))
            self.fitPopulation   = np.concatenate((self.fitPopulation,newFitness))
            newIndeces           = np.argsort(self.fitPopulation)[:self.population_size]
            self.population      = self.population[newIndeces]
            print("Nueva población:", self.population)

    def generateDictionary(self):
        dic = []
        for i in range (0,self.genotype_size):
            dic.append((chr(65+i),i))
        self.dictionary =  dict(dic)


    def generatePopulation(self):
        population = []
        for i in range(0,self.population_size):
            dictionary = list(self.dictionary.keys())
            gen = ""
            while len(dictionary)>0:
                val = secrets.choice(dictionary)
                gen += val
                dictionary.remove(val)
            population.append(gen)
        self.population = np.array(population)

    def fitness(self,population):
        fit = []
        for i in population:
            fi = 0
            for j in range(0,self.genotype_size-1):
                fi+= self.caminos[self.dictionary[i[j]]][self.dictionary[i[j+1]]]
            fit.append(fi)
        return np.array(fit)

    def probability(self):
        #Minimizamos complementando los valores al valor máximo
        prob = self.fitPopulation.max() - self.fitPopulation +1
        prob = prob/sum(prob)
        print("Probabilidad:",prob)
        self.populationProb = np.cumsum(prob)
        print("Probabilidad acum:",self.populationProb)

    def roulette(self):
        rand = np.random.uniform(0,1)
        for i in range(0,self.population_size):
            if (self.populationProb[i] > rand):
                return i

    def crossover(self,parent1,parent2):
        rand0 = np.random.uniform(0,1)
        if(rand0 < self.probCross/100): #Probabilidad para cruzarse
            limits = np.sort([np.random.randint(0,self.genotype_size) for i in range(2)])
            print("Limites:", limits)
            p1,p2     = np.array(list(parent1)), np.array(list(parent2))
            for i in range(limits[0],limits[1]+1): #para tocar el ultimo elemento
                val1,val2 = p1[i],p2[i]
                pos2      = np.where(p2 == val1)[0][0] #Posición del valor en el otro padre2
                pos1      = np.where(p1 == val2)[0][0] #Posición del valor en el otro padre2
                p1[pos1]  = val1
                p2[pos2]  = val2
                p1[i],p2[i] = val2,val1 #intercambiamos valores

            child1 = "".join(p1)
            child2 = "".join(p2)

        else:
            print("Hijos iguales a padres")
            child1,child2 = parent1,parent2
        print("Hijo 1: ", child1, " -- ","Hijo 2: ",child2)

        child1 = self.checkMutation(child1)
        child2 = self.checkMutation(child2)
        return child1,child2

    def checkMutation(self,child):
        rand = np.random.uniform(0,1)
        #Probabilidad de mutar
        if(rand < self.probMut/100):

            limits = np.sort([np.random.randint(0,self.genotype_size) for i in range(2)])
            print("Mutando:", child, " en límite:", limits)
            child  = np.array(list(child))
            sub    = child[limits[0]:limits[1]+1]
            np.random.shuffle(sub)
            child[limits[0]:limits[1]+1] = sub
            child  = "".join(child)
            print("Mutado:", child)
        return child


def main():

    caminos = np.array([
            [0,2,2,1,4],
            [2,0,3,2,3],
            [2,3,0,2,2],
            [1,2,2,0,4],
            [4,3,2,4,0]])

    # caminos = np.array([
    #             [0,12,3,23,1,5,23,56,12,11],
    #             [12,0,9,18,3,41,45,5,41,27],
    #             [3,9,0,89,56,21,12,48,14,29],
    #             [23,18,89,0,87,46,75,17,50,42],
    #             [1,3,56,87,0,55,22,86,14,33],
    #             [5,41,21,46,55,0,21,76,54,81],
    #             [23,45,12,75,22,21,0,11,57,48],
    #             [56,5,48,17,86,76,11,0,63,24],
    #             [12,41,14,50,14,54,57,63,0,9],
    #             [11,27,29,42,33,81,48,24,9,0]
    #             ])

    print("Los caminos:\n",caminos)

    print("\nCOMIENZO PROCESO: ", datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

    comienzo = time.time()
    genetic  = GeneticAlgo(caminos = caminos,population_size=10,probCross=90,probMut=10,generations=10)
    final    = time.time()

    print("\nFIN DEL PROCESO")
    print("Tiempo:",final-comienzo)


if __name__ == '__main__':
    main()
