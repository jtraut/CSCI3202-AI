#Jake Traut
#CSCI 3202 
#Runs with Assignment3.txt file in same directory, no use of command line 

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
			
	#your code goes here
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

def Astar(graph, start, end):
	vopen = [] #list of open vertex 
	vclosed = [] #list of closed vertex
	adj = []
	f[start] = 0
	parents = {}
	evaluated = []
	vopen.append(start)
	vertex = start 
	nextvertex = start
	while vopen != []:
		#print "open nodes: {0}".format(vopen)
		#print "closed nodes: {0}".format(vclosed)
		#print "current vertex {0} with distance {1}".format(vertex,f[vertex])	
		minweight = 1000
		for openvertex in vopen:
			if gn[openvertex] < minweight: #distance to openvertex
				minweight = gn[openvertex]
				nextvertex = openvertex
		vertex = nextvertex		
		vopen.remove(vertex)
		if vertex not in evaluated:
			evaluated.append(vertex)
		
		if vertex != end:
			vclosed.append(vertex)
			adj = graph.findVertex(vertex)
			if adj:
				for i in range(0, len(adj)):
					if adj[i] not in vclosed: 
						adjV = adj[i]
						weight = graph.edges[vertex,adjV]
						gn[adjV] = gn[vertex] + weight
						if f[adjV] == 0:
							f[adjV] = gn[adjV] + heuristic[adjV]
						else:
							temp = gn[adjV] + heuristic[adjV]
						
						parents[adjV] = vertex
						if adjV in vopen:
							if temp < f[adjV] or f[adjV] == 0:
								f[adjV] = temp 
						else:
							vopen.append(adjV)
		else:
			break
			
	finalpath = vertex
	finalvertex = parents[vertex]
	while vertex is not start:
		parent = parents[vertex]
		finalpath = parent + " " + finalpath
		vertex = parent 
	
	print "A* solution: {0} distance {1}".format(finalpath, f[finalvertex])
	print "A* evaluated {0} nodes".format(len(evaluated))
	print evaluated
	
def dijkstra(graph, start, end):
	startV = start 
	endV = end 
	solved = {}
	distance = {} 
	solved[startV] = True
	solved[endV] = False
	distance[startV] = 0
	solvedlist = []
	adj = []
	parents = {} 
	evaluated = []
	
	solvedlist.append(startV)
	evaluated.append(startV)
	while not solved[endV]:
		minDistance = 1000
		solvedV = None 
		for s in solvedlist:
			adj = graph.findVertex(s)
			if adj != False:
				for y in range(0,len(adj)):
					adjV = adj[y]
					if adjV not in evaluated:
						evaluated.append(adjV)
					if adjV not in solvedlist: 
						dist = distance[s] + graph.edges[s, adjV]
						if dist < minDistance:
							solvedV = adjV
							minDistance = dist
							parent = s

		if solvedV != None:					
			distance[solvedV] = minDistance
			parents[solvedV] = parent
			solved[solvedV] = True
			solvedlist.append(solvedV)

	finalpath = solvedV
	finalvertex = parents[solvedV]
	while solvedV is not start:
		parent = parents[solvedV]
		finalpath = parent + " " + finalpath
		solvedV = parent 
		
	print "Dijkstra's solution: {0} distance: {1}".format(finalpath, distance[end])
	print "Dijkstra's evaulated {0} nodes".format(len(evaluated))
	print evaluated

g = Graph()
heuristic = {}
f = {}
gn = {}
paths = []


with open('Assignment3.txt') as data:
	for line in data:
		if line[0] == "[": 
			v1 = line[1] #vertex 1
			v2 = line[3] #vertex 2
			w = int(line[5])  #edge weight
			if v1 not in g.verticies: g.addVertex(v1)
			if v2 not in g.verticies: g.addVertex(v2)
			g.addEdge(v1,v2,w)
		elif len(line) >= 4:
			hv = line[0] #heuristic vertex
			hw = line[2:] #heuristic weight 
			heuristic[hv] = int(hw)
			f[hv] = 0 #default fn values
			gn[hv] = 0
			#print "heuristic value for {0} is {1}".format(hv,hw)
			
Astar(g,'S','F')

dijkstra(g,'S','F')
