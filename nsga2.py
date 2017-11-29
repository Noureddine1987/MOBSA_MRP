'''
Deb, Kalyanmoy, et al.
"A Fast Elitist Non-dominated Sorting Genetic Algorithm for Multi-objective Optimisation: NSGA-II."
International Conference on Parallel Problem Solving From Nature Springer-Verlag, 2000:849-858.
'''
from algorithm.individual import IndividualMRP
from algorithm.parameter import PM, PC, POPULATION_SIZE, MAX_NUMBER_FUNCTION_EVAL
from problem.mrp.multicast_routing_problem import MulticastRoutingProblem as MRP
from algorithm.operator import fast_nondominated_sort, crowding_distance_sort
from algorithm.util import write_list_to_json, plot_pf, plot_ps, write_performance, read_json_as_list
from solution.solution_trim import trim_solution
from algorithm.performance import cal_IGD, cal_GD, cal_HV

import numpy
import random
import copy
import os
import json

import matplotlib.pyplot as plot

class IndividualNSGA(IndividualMRP):
    
    def __init__(self):
        super(IndividualNSGA, self).__init__()
    

class NondominatedSortGeneticAlgorithm2(object):
    
    def __init__(self, problem):
        self.problem = problem
        self.current_poplist = []
        self.pre_poplist = []
    
    def init_population(self):
        for i in xrange(POPULATION_SIZE):
            ind = IndividualNSGA()
            ind.initialize(IndividualMRP.create_chromosome(self.problem.num_link), self.problem)
            self.current_poplist.append(ind)
        
    def copy_current_to_pre(self):
        self.pre_poplist = []
        for ind in self.current_poplist:
            self.pre_poplist.append(ind.copy())
            
    def make_new_population(self):
        union_poplist = []
        union_poplist.extend(self.current_poplist)
        union_poplist.extend(self.pre_poplist)
        
        pareto_rank_set_list = fast_nondominated_sort(union_poplist)
        crowding_distance_sort(pareto_rank_set_list)
        
        self.current_poplist = []
        for pareto_rank_set in pareto_rank_set_list:
            if len(self.current_poplist) < POPULATION_SIZE:
                if (len(pareto_rank_set) + len(self.current_poplist)) <= POPULATION_SIZE:
                    for ind in pareto_rank_set:
                        self.current_poplist.append(ind.copy())
                else:
                    current = len(self.current_poplist)
                    for i in range(POPULATION_SIZE - current):
                        self.current_poplist.append(pareto_rank_set[i].copy())

    def evolution(self):
        self.current_poplist = []
        for i in range(POPULATION_SIZE):
            x = 0
            y = 0
            while x == y:
                x = random.randint(0, POPULATION_SIZE-1)
                y = random.randint(0, POPULATION_SIZE-1)
            ind1 = self.pre_poplist[x]
            ind2 = self.pre_poplist[y]
            
            if ind1.pareto_rank < ind2.pareto_rank:
                self.current_poplist.append(ind1.copy())
            elif ind1.pareto_rank == ind2.pareto_rank and ind1.crowding_distance > ind2.crowding_distance:
                self.current_poplist.append(ind1.copy())
            else:
                self.current_poplist.append(ind2.copy())
                
        for i in range(POPULATION_SIZE/2):
            if random.random() < PC:
                self.current_poplist[i].crossover(self.current_poplist[POPULATION_SIZE-i-1])
        
        for ind in self.current_poplist:
            ind.mutation()
        
    def main(self):
        self.init_population()
        self.copy_current_to_pre()
        
        gen = 0
        while gen < MAX_NUMBER_FUNCTION_EVAL:
            # print "Gen >>> ", gen
            self.make_new_population()
            self.copy_current_to_pre()
            self.evolution()
            gen += 1
            
        
if __name__ == '__main__':
    topo = 'topo1'
    problem = MRP()
    problem.initialize(topo)
    
    pideal = read_json_as_list(topo, 'ideal')
    x = pideal[0]['delay'] + (pideal[0]['delay'] - pideal[len(pideal) - 1]['delay']) * 0.1
    y = pideal[len(pideal) - 1]['loss'] + (pideal[len(pideal) - 1]['loss'] - pideal[0]['loss']) * 0.1
    ref = [x, y]
    
    IGD = []
    GD = []
    HV = []
    for i in range(10):
        print 'Runtime >>> ', i + 1
        test = NondominatedSortGeneticAlgorithm2(problem)
        test.main()
        write_list_to_json(topo, 'nsga2', test.pre_poplist)
        
        preal = read_json_as_list(topo, 'nsga2')
        
        IGD.append(cal_IGD(pideal, preal))
        GD.append(cal_GD(pideal, preal))
        HV.append(cal_HV(preal, ref))
    
    per = {'IGD': IGD,
           'GD': GD,
           'HV': HV}
    
    write_performance('performance', topo, 'nsga2', per)
    
    # topo = ['topo2','topo3','topo4','topo5','topo6']
    #
    # for item in topo:
    #     print "Topo init", item
    #     problem = MRP()
    #     problem.initialize(item)
    #
    #     pf_list = []
    #
    #     for i in range(10):
    #         print "Runtime >>> ",i+1
    #         test = NondominatedSortGeneticAlgorithm2(problem)
    #         test.main()
    #         pf_list.extend(test.pre_poplist)
    #
    #     pf_ = fast_nondominated_sort(pf_list)[0]
    #     for i in range(0, len(pf_)):
    #         for j in range(len(pf_) - 1, i + 1, -1):
    #             if pf_[i].is_equal(pf_[j]):
    #                 pf_.pop(j)
    #
    #     write_list_to_json(item, 'nsga2', pf_)
    
    
    # # trim_solution('topo1')
    #


    # # plot_pf('topo1', 'nsga2')
    #
    # plot_ps('topo1', ['nsga2', 'mobas', 'ideal'], ['r+', 'go', 'b*'], '')
    # plot_ps('topo1', ['nsga2'], ['g.--'], 'NSGA2')