"""
CSCI 3202 AI Assignment 5

Jake Traut

An implementation of simulated annealing for finding the most "fair" political districts boundaries.
Takes 'smallState.txt' or 'largeState.txt' as command line input 

10-10-16

"""
import sys
from math import exp
from random import randint 
from copy import deepcopy

#GLOBAL VARS
PARENTS = {}
VISITED = {}
OLD_SOLUTIONS = {} 	

VOTERS = []
NUM_DISTRICTS = 0
PER_DISTRICT = 0
TOTAL_VOTERS = 0
R_DISTRICTS = 0
D_DISTRICTS = 0
TIED = 0

class Graph:
	def __init__(self):
		self.verticies = {}
		self.edges = {}
			
	def addVertex(self, value):
		#check if value already exists
		if value in self.verticies:
			print "Vertex already exists"
		else:
			self.verticies[value] = []
			
	def addEdge(self, value1, value2, weight):
		if value1 in self.verticies and value2 in self.verticies:
			#add the edge
			self.verticies[value1].append(value2)
			self.verticies[value2].append(value1)
			self.edges[value1,value2] = weight
			self.edges[value2,value1] = weight
			#print "Edge weight between {0} and {1} is {2}".format(value1, value2, self.edges[value1,value2])
		else: #invalid vertex cant add an edge
			print "One or more vertices not found."
			return 
		
	def findVertex(self, value):
		if value in self.verticies:
			#find adjacent verticies 
			if self.verticies[value] != []:
				#print self.verticies[value]
				temp = []
				temp = self.verticies[value]
			return temp
		else:
			print "Not found."
			return False 
			
def DFS(graph, vertex, district): #recursive function that populates VISITED and PARENTS, used to check for contiguous districts 
	global VISITED, PARENTS 
	VISITED[vertex] = True
	adjacent = graph.findVertex(vertex)

	for node in adjacent:
		if not VISITED[node] and node in district: #extra case to see if districts are connected
			PARENTS[node] = vertex
			DFS(graph, node, district)			

def isValid(graph, solution): #is the solution valid (districts are contiguous)?
	for i in range(0, NUM_DISTRICTS):
		temp_distr = solution[i]
		#run DFS from smallest node in dist, and see if all in dist are connected
		global PARENTS, VISITED
		for i in range(0, TOTAL_VOTERS):
			VISITED[i] = False 
			PARENTS[i] = -1 
			
		root = min(temp_distr)
		
		DFS(graph, root, temp_distr)
		
		for vertex in temp_distr:
			if PARENTS[vertex] not in temp_distr:
				if (vertex != root):
					return False 
	return True 
			
def fitness(solution): #number of D districts compared to R districts 
	global D_DISTRICTS, R_DISTRICTS, TIED
	
	D_DISTRICTS = 0
	R_DISTRICTS = 0
	TIED = 0
	
	for i in range(0, NUM_DISTRICTS):
		temp_distr = solution[i]
		total_D = 0
		total_R = 0
		for voter in temp_distr:
			if (VOTERS[voter] == 'D'):
				total_D += 1
			elif (VOTERS[voter] == 'R'):
				total_R += 1		
		#print "total_D in districts {1}: {0}".format(total_D, i)		
		#print "total_R in distirct {1}: {0}".format(total_R, i)		
		voter_diff = total_D - total_R
		
		if (voter_diff > 0):
			D_DISTRICTS += 1
		elif (voter_diff < 0):
			R_DISTRICTS += 1
		elif (voter_diff == 0):
			TIED += 1
	dist_diff = abs(D_DISTRICTS - R_DISTRICTS) #want to minimize this value
	return dist_diff 
	

def isNew(solution): #check if a solution is a repeat
	global OLD_SOLUTIONS 
	exists = False 
	num_solutions = len(OLD_SOLUTIONS) 

	for i in range(0, num_solutions):
		if (solution == OLD_SOLUTIONS[i]):
			#print "solution already exists"
			exists = True 
			return False 
	if not exists:
		OLD_SOLUTIONS[num_solutions] = deepcopy(solution)
	
	return True		
	
def generateNeighbor(graph, solution):
	curr_sol = deepcopy(solution)	
	rand_distr = randint(0,NUM_DISTRICTS-1)
	temp_distr = curr_sol[rand_distr]
	
	rand_distr2 = randint(0, NUM_DISTRICTS-1)	
	while (rand_distr2 == rand_distr):
		rand_distr2 = randint(0, NUM_DISTRICTS-1)	
	
	temp_distr2 = curr_sol[rand_distr2]
	borders = False #does the 2nd district border the first?
	
	while not borders: #keep searching until find a district that borders temp_distr
		rand_index2 = randint(0, PER_DISTRICT-1)
		voter2 = temp_distr2[rand_index2]
		neighbors = graph.findVertex(voter2) 
		for neighbor in neighbors:
			if neighbor in temp_distr: #voter node in Dist2 borders Dist 
				borders = True
	
				#try to find another adj to swap
				found_swap = False
				for i in range(0, PER_DISTRICT):
					voter1 = temp_distr[i]
					if (voter1 != neighbor):
						voter1_neighbors = graph.findVertex(voter1)
						
						for voter1_neighbor in voter1_neighbors:
							if voter1_neighbor in temp_distr2:
								temp_distr[i] = voter2
								temp_distr2[rand_index2] = voter1
								temp_distr.sort()
								temp_distr2.sort()
								curr_sol[rand_distr] = temp_distr
								curr_sol[rand_distr2] = temp_distr2
								found_swap = True
								return curr_sol 
								
				if not found_swap:
					rand_index = randint(0, PER_DISTRICT-1) #more random but uncertain in getting results  
					rand_voter = temp_distr[rand_index]
					while (rand_voter == neighbor):
						rand_index = randint(0, PER_DISTRICT-1) 
						rand_voter = temp_distr[rand_index]
					
					temp_distr[rand_index] = voter2
					temp_distr2[rand_index2] = rand_voter
					temp_distr.sort()
					temp_distr2.sort()
					curr_sol[rand_distr] = temp_distr
					curr_sol[rand_distr2] = temp_distr2	
				
		if not borders:
			rand_distr2 = randint(0, NUM_DISTRICTS-1)
			temp_distr2 = curr_sol[rand_distr2]	
		
	return curr_sol 		
	

def simAnnealing(graph, T, k, alpha, initial_sol):
	T_min = .0001
	sol = deepcopy(initial_sol) #creates an editable copy of solution, rather than a pointer to initial if just set = 
	counter = 0
	
	while T > T_min:
		x = 0
		while x < 100:
			counter += 1
			#generate a random sol here 
			new_sol = generateNeighbor(graph, sol)
			if (isValid(graph, new_sol) and isNew(new_sol)):
				#print "new solution is valid"
				sol_fit = fitness(sol)
				new_sol_fit = fitness(new_sol)
				#evaluate deltaE (difference in fitness of new sol and prev sol)
				deltaE = new_sol_fit - sol_fit
				#if deltaE < 0 accept new solution
				if (deltaE < 0): 
					sol = new_sol
					#print "accepted solution {0}".format(len(OLD_SOLUTIONS))
				#else accept new sol with probability e^(-deltaE/(kT))
				else:
					prob = exp((-deltaE/(k*T)))
					prob_perc = prob * 100
					chance = randint(0,100)
					if (chance <= prob_perc):
						sol = new_sol
						#print "accepted solution {0} with probability {1}".format(len(OLD_SOLUTIONS), prob)
			#else: print "new solution NOT valid on {0} try".format(counter)		
			x += 1
		T = T * alpha 
	return sol 
		
	
def main():
	global NUM_DISTRICTS, PER_DISTRICT, VOTERS, TOTAL_VOTERS, OLD_SOLUTIONS
	
	filename = sys.argv[-1]

	if (filename != "smallState.txt" and filename != "largeState.txt"): #recieved no command line input or wrong input
		filename = "smallState.txt" #default to smallState
	
	if (filename == "smallState.txt"):
		NUM_DISTRICTS = 8
		PER_DISTRICT = 8	
	elif (filename == "largeState.txt"):
		NUM_DISTRICTS = 10
		PER_DISTRICT = 10
			
	#Process the data from txt file into list  
	VOTERS = []
	num_D = 0
	num_R = 0
	
	with open(filename) as state:
		for line in state:
			for voter in line:
				if (voter == 'D'):
					VOTERS.append(voter)
					num_D += 1
				elif (voter == 'R'):
					VOTERS.append(voter)
					num_R += 1		
	
	g = Graph()
	TOTAL_VOTERS = len(VOTERS)
	for i in range(0, TOTAL_VOTERS):
		g.addVertex(i)

	for i in range(0, TOTAL_VOTERS):
		if (i % PER_DISTRICT != PER_DISTRICT-1): #if not right most column  
			g.addEdge(i, i+1, 1)
		if (i + PER_DISTRICT <= TOTAL_VOTERS-1): #if not the bottom row
			g.addEdge(i, i+PER_DISTRICT, 1)
		
		
	percent_R = num_R / float(TOTAL_VOTERS) * 100
	percent_D = num_D / float(TOTAL_VOTERS) * 100	
	
	districts = {}	

	#producing an initial solution (each district is a row) 
	for i in range(0, NUM_DISTRICTS):
		temp_distr = []
		for j in range(0, PER_DISTRICT): 
			temp_distr.append(i*NUM_DISTRICTS + j) 
		districts[i] = temp_distr 
		#print districts[i]

	T = 1.0
	k = 85
	alpha = .95
	OLD_SOLUTIONS[0] = districts 
		
	best_solution = simAnnealing(g, T, k, alpha, districts)
	fitness(best_solution)

	print "Pary division in population: "
	print "***************************************"
	print "R: {0}%".format(percent_R)
	print "D: {0}%".format(percent_D)
	print "***************************************"
	
	print 
	print "Number of districts with a majority for each party: "
	print "***************************************"
	print "R: {0}".format(R_DISTRICTS)
	print "D: {0}".format(D_DISTRICTS)
	print "***************************************"
	
	print 
	print "Locations assigned to each district: "
	print "***************************************"
	for i in range(0, NUM_DISTRICTS):
		print "District {0}: {1}".format(i+1, best_solution[i])
	print "***************************************"

	print
	print "***************************************"
	print "Algorithm applied: Simulated Annealing"
	print "***************************************"
	
	print
	print "***************************************"	
	print "Number of search states explored: {0}".format(len(OLD_SOLUTIONS))
	print "***************************************"

if __name__ == "__main__":
	main()
