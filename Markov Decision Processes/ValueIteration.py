#Artificial Intelligence: A Modern Approach

# Search AIMA
#AIMA Python file: mdp.py

"""Markov Decision Processes (Chapter 17)

First we define an MDP, and the special case of a GridMDP, in which
states are laid out in a 2-dimensional grid.  We also represent a policy
as a dictionary of {state:action} pairs, and a Utility function as a
dictionary of {state:number} pairs.  We then define the value_iteration
and policy_iteration algorithms."""


#Answers
"""
1. What action is assigned in the terminal states?

Action is assigned to None to prohibit further moving.

2. Where are the transition probabilities defined in the program, and what are those probabilities?

The transition probabilities are defined in the T (transition model) function of the GridMDP class.
The probabilities are an 80% chance to complete the intended action, a 10% chance to go right of the intended move, 
and another 10% chance to go left of the intented move.

3. What function needs to be called to run value iteration?	

You call the value_iteration function with two parameters; the MDP and an epsilon value.
If you want to get a policy out of this, you can pass that result (the utility mapping) along with the MDP into the best_policy function.

4. When you run value_iteration on the MDP provided, the results are stored in a variable called myMDP. What is the utility of (0,1), (3,	1), and (2,	2)?

(0,1): 0.398
(3,1): -1.0
(2,2): 0.795

5. How are actions represented, and what are the possible actions for each state in the program?

Actions are represented by an (x, y) vector that describes the direction of the next move.
The action (0,-1) translates to moving south (or down). 

Your actions are you can move a unit NSEW or stay put depending on current state and the surrounding environment.  
At a terminal state you wouldn't continue to move, and the borders restrict moving further in its respective direction.

"""
from utils import *

orientations = [(1,0), (0, 1), (-1, 0), (0, -1), (2, 0), (0, 2), (-2, 0), (0, -2)]
jumplist = [(2,0), (0, 2), (-2, 0), (0, -2)]

class MDP:
    """A Markov Decision Process, defined by an initial state, transition model,
    and reward function. We also keep track of a gamma value, for use by
    algorithms. The transition model is represented somewhat differently from
    the text.  Instead of T(s, a, s') being  probability number for each
    state/action/state triplet, we instead have T(s, a) return a list of (p, s')
    pairs.  We also keep track of the possible states, terminal states, and
    actions for each state. [page 615]"""

    def __init__(self, init, actlist, terminals, gamma=.9):
        update(self, init=init, actlist=actlist, terminals=terminals,
               gamma=gamma, states=set(), reward={})

    def R(self, state):
        "Return a numeric reward for this state."
        return self.reward[state]

    def T(state, action):
        """Transition model.  From a state and an action, return a list
        of (result-state, probability) pairs."""
        abstract

    def actions(self, state):
        """Set of actions that can be performed in this state.  By default, a
        fixed list of actions, except for terminal states. Override this
        method if you need to specialize by state."""
        if state in self.terminals:
            return [None]
        else:
			return self.actlist

class GridMDP(MDP):
    """A two-dimensional grid MDP, as in [Figure 17.1].  All you have to do is
    specify the grid as a list of lists of rewards; use None for an obstacle
    (unreachable state).  Also, you should specify the terminal states.
    An action is an (x, y) unit vector; e.g. (1, 0) means move east."""
    def __init__(self, grid, terminals, init=(0, 0), gamma=.9):
        grid.reverse() ## because we want row 0 on bottom, not on top
        MDP.__init__(self, init, actlist=orientations,
                     terminals=terminals, gamma=gamma)
        update(self, grid=grid, rows=len(grid), cols=len(grid[0]))
        for x in range(self.cols):
            for y in range(self.rows):
                self.reward[x, y] = grid[y][x]
                if grid[y][x] is not None:
                    self.states.add((x, y))

    def T(self, state, action):
		if action == None:
			return [(0.0, state)]
		
		next_state = vector_add(state, action)
		if next_state not in self.states:
			return [(0.0, state)]
		
		if action in jumplist:
			return [(0.5, self.go(state, action)),
					(0.5, state)]
		else:
			return [(0.8, self.go(state, action)),
                    (0.1, self.go(state, turn_right(action))),
                    (0.1, self.go(state, turn_left(action)))]

    def go(self, state, direction):
		"Return the state that results from going in this direction."
		state1 = vector_add(state, direction)
		return if_(state1 in self.states, state1, state)

    def to_grid(self, mapping):
        """Convert a mapping from (x, y) to v into a [[..., v, ...]] grid."""
        return list(reversed([[mapping.get((x,y), None)
                               for x in range(self.cols)]
                              for y in range(self.rows)]))

    def to_arrows(self, policy):
        chars = {(1, 0):'>', (0, 1):'^', (-1, 0):'<', (0, -1):'v', None: '.'}
        return self.to_grid(dict([(s, chars[a]) for (s, a) in policy.items()]))


def value_iteration(mdp, epsilon=0.001):
    "Solving an MDP by value iteration. [Fig. 17.4]"
    U1 = dict([(s, 0) for s in mdp.states])
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    while True:
        U = U1.copy()
        delta = 0
        for s in mdp.states:
            U1[s] = R(s) + gamma * max([sum([p * U[s1] for (p, s1) in T(s, a)])
                                        for a in mdp.actions(s)])
            delta = max(delta, abs(U1[s] - U[s]))
        if delta < epsilon * (1 - gamma) / gamma:
             return U

def best_policy(mdp, U):
    """Given an MDP and a utility function U, determine the best policy,
    as a mapping from state to action. (Equation 17.4)"""
    pi = {}
    for s in mdp.states:
        pi[s] = argmax(mdp.actions(s), lambda a:expected_utility(a, s, U, mdp))
    return pi

def expected_utility(a, s, U, mdp):
    "The expected utility of doing a in state s, according to the MDP and U."
    return sum([p * U[s1] for (p, s1) in mdp.T(s, a)])


def policy_iteration(mdp):
    "Solve an MDP by policy iteration [Fig. 17.7]"
    U = dict([(s, 0) for s in mdp.states])
    pi = dict([(s, random.choice(mdp.actions(s))) for s in mdp.states])
    while True:
        U = policy_evaluation(pi, U, mdp)
        unchanged = True
        for s in mdp.states:
            a = argmax(mdp.actions(s), lambda a: expected_utility(a,s,U,mdp))
            if a != pi[s]: 
				pi[s] = a
				unchanged = False
        if unchanged:
            return pi

def policy_evaluation(pi, U, mdp, k=20):
    """Return an updated utility mapping U from each state in the MDP to its
    utility, using an approximation (modified policy iteration)."""
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    for i in range(k):
        for s in mdp.states:
            U[s] = R(s) + gamma * sum([p * U[s1] for (p, s1) in T(s, pi[s])])
    return U

myMDP = GridMDP([[0, 0, 0, 0, -1, 0, -1, -1, 0, 50],
			[None, None, -1, -1, 0, -.5, None, 0, None, 0],
			[0, 0, 0, 0, 0, -.5, None, 0, 0, 0],
			[None, 2, None, None, None, -.5, 0, 2, None, 0],
			[None, 0, 0, 0, 0, None, -1, -.5, -1, 0],
			[0, -.5, None, 0, 0, None, 0, 0, None, 0],
			[0, -.5, None, 0, -1, None, 0, -1, None, None],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
			terminals=[(9,7)])

myMDP2 = GridMDP([[-.05, -.05, -.05, -.05, -1, -.05, -1, -1, -.05, 50],
			[None, None, -1, -1, -.05, -.5, None, -.05, None, -.05],
			[-.05, -.05, -.05, -.05, -.05, -.5, None, -.05, -.05, -.05],
			[None, 2, None, None, None, -.5, -.05, 2, None, -.05],
			[None, -.05, -.05, -.05, -.05, None, -1, -.5, -1, -.05],
			[-.05, -.5, None, -.05, -.05, None, -.05, -.05, None, -.05],
			[-.05, -.5, None, -.05, -1, None, -.05, -1, None, None],
			[-.05, -.05, -.05, -.05, -.05, -.05, -.05, -.05, -.05, -.05]],
			terminals=[(9,7)], gamma=.9)

U = value_iteration(myMDP, .001)
U2 = value_iteration(myMDP2, .001)

P = policy_iteration(myMDP)
P2 = policy_iteration(myMDP2)

bestP = best_policy(myMDP, U)
bestP2 = best_policy(myMDP2, U2)

i = 0
j = 0
state = (i,j)
terminal = (9,7)
			
print "Policy for MDP2"
#reformatting the print for easier comprehension 			
for i in range (0,10):
	for j in range (0, 8):
		if (myMDP.R((i,j)) != None):
			print "State {0}: Action {1}".format((i,j), P2[(i,j)])
			
#print out the desired path of states
i = 0
j = 0
state = (i,j)

print "\nDesired path"
while (state in myMDP.states and state != terminal):
	print "{0} -> ".format(state),
	action = P[state]
	
	if (action == (1,0)):
		i = i + 1
	elif (action == (-1,0)):
		i = i - 1
	elif (action == (0,1)):
		j = j + 1
	elif (action == (0,-1)):
		j = j - 1
	
	if (action == (2,0)):
		i = i + 2
	elif (action == (-2,0)):
		i = i - 2
	elif (action == (0,2)):
		j = j + 2
	elif (action == (0,-2)):
		j = j - 2
	next_state = (i,j)
	if (next_state not in myMDP.states):
		print "Hit wall: {0}".format(next_state)
	elif next_state == terminal: print "Terminal state: {0}".format(next_state)
	
	state = next_state

i = 0
j = 0
state = (i,j)

print "\nDesired path 2"
while (state in myMDP.states and state != terminal):
	print "{0} -> ".format(state),
	action = P2[state]

	if (action == (1,0)):
		i = i + 1
	elif (action == (-1,0)):
		i = i - 1
	elif (action == (0,1)):
		j = j + 1
	elif (action == (0,-1)):
		j = j - 1
			
	if (action == (2,0)):
		i = i + 2
	elif (action == (-2,0)):
		i = i - 2
	elif (action == (0,2)):
		j = j + 2
	elif (action == (0,-2)):
		j = j - 2
	next_state = (i,j)
	if (next_state not in myMDP.states):
		print "Hit wall: {0}".format(next_state)
	elif next_state == terminal: print "Terminal state: {0}".format(next_state)
	
	state = next_state	
	
if P == P2: print "\nSame policy"
else: print "\nDifferent policy"

'''
myMDP = GridMDP([[-0.04, -0.04, -0.04, +1],
                     [-0.04, None,  -0.04, -1],
                     [-0.04, -0.04, -0.04, -0.04]],
                    terminals=[(3,1),(3,2)])

#AI: A Modern Approach by Stuart Russell and Peter Norvig	Modified: Jul 18, 2005
'''
