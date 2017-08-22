__author__ = 'sudab'

import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gridworld import *
import counterexample_parser
import grid_partition
import Slugs_input
import Salty_input
import subprocess
import time
import copy
import counterexample_parser
import visibility

visited_nodes = set()   # stores already visited nodes
visited_pairs = set()   # stores already visited pairs of node and true belief

current_path = list()
path_beliefs = list()
path_abstract = list()

belief_true_next = set()
true_plus_vis_next = set()



'''
stores information about the path in the counterexample tree along which we will refine
each element of the list is a set of partitions forming the belief in the current position
'''
toRefine = list()
prefix_length = 0
leaf_belief = set()
neg_states = set()

def analyse_counterexample(fname,gwg,partitionGrid,belief_safety,belief_liveness,targets):
    global visited_nodes
    global visited_pairs

    global current_path
    global path_beliefs
    global path_abstract
    
    global belief_true_next
    global true_plus_vis_next
     
    global toRefine
    global prefix_length
    global leaf_belief
    global neg_states 
    
    visited_nodes = set()
    visited_pairs = set()

    current_path = list()
    path_beliefs = list()
    path_abstract = list()
    
    belief_true_next = set()
    true_plus_vis_next = set()
    
    toRefine = list()  
    prefix_length = 0
    leaf_belief = set()
    neg_states = set()
    
    with open(fname) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    xstates = list(set(gwg.states) - set(gwg.edges))
    allstates = copy.deepcopy(xstates)
    beliefcombs = counterexample_parser.powerset(partitionGrid.keys())
    for i in range(gwg.nstates,gwg.nstates+ len(beliefcombs)):
        allstates.append(i)

    invisibilityset = [dict.fromkeys(set(gwg.states) - set(gwg.edges),frozenset({gwg.nrows*gwg.ncols+1}))]*gwg.nagents
    for n in range(gwg.nagents):
        for s in set(gwg.states) - set(gwg.edges):
            invisibilityset[n][s] = visibility.invis(gwg,s) #- set(gw.targets[n])
            if s in gwg.obstacles:
                invisibilityset[n][s] = {-1}

    def traverse_counterexample_safety(fname,gwg,partitionGrid,belief_safety,ind,agentstate_parent):

        global visited_nodes
        global visited_pairs
        
        global current_path
            
        global belief_true_next
        global true_plus_vis_next
        
        global toRefine
        global leaf_belief
        global neg_states
        
        current_path.append(ind)
        visited_nodes.add(ind)
        #print 'INDEX IN COUNTEREXAMPLE ', ind
    
        envstatebin = []
        agentstatebin = []
        beliefstate = set()
        
        line = content[ind].split(' ')
        for r in line[6::]:
            if r[1] == 'y' or r[0] == 'y':
                envstatebin.append(r[-2])
            elif r[1] == 'x' or r[0] == 'x':
                agentstatebin.append(r[-2])
        
        # agent position
        if len(agentstatebin) > 0:
            agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
            #print 'Agent position is ', agentstate
        else: # failure state
            current_path.pop()
            return set()
        if content[ind+1] == 'With no successors.': # terminal state
            current_path.pop()
            return set()

        # environment position
        envstate = int(''.join(str(e) for e in envstatebin)[::-1],2)
        if envstate < len(xstates):
            belief_true = {xstates[envstate]}
            true_plus_vis = {xstates[envstate]}
            #print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            belief_true = copy.deepcopy(belief_true_next)
            true_plus_vis = copy.deepcopy(true_plus_vis_next)
            #print 'Environment position is ', beliefstate    
 
 
        if (((ind,frozenset(belief_true)) in visited_pairs)): # already explored
            current_path.pop()
            return set()       
        
        visited_pairs.add((ind,frozenset(belief_true)))
        
        
        # compute true belief for successor nodes w.r.t. current position of agent
        belief_true_next = set()
        for s in belief_true:
            for a in gwg.actlist:
                for t in np.nonzero(gwg.prob[a][s])[0]:
                    belief_true_next.add(t)
        belief_true_next = belief_true_next - set(gwg.walls)
        true_plus_vis_next = copy.deepcopy(belief_true_next)
        belief_true_next = belief_true_next.intersection(invisibilityset[0][agentstate])    
        
      
        if len(beliefstate) > 0:
            
            # invisible states in belief w.r.t. previous position of agent
            belief_invisible = beliefstate.intersection(invisibilityset[0][agentstate_parent])
            belief_visible = beliefstate - invisibilityset[0][agentstate_parent]
        
                     
            if len(belief_invisible) > belief_safety: # belief violates constraint
             
                if len(belief_true) <= belief_safety: # true belief satisfies constraint
                    print 'SAFETY'
                    print 'Invisible states in belief:', belief_invisible
                    print "Precise belief:", belief_true
                    
                    leaf_belief = copy.deepcopy(belief_true)
                    #leaf_belief = copy.deepcopy(true_plus_vis)
                    #leaf_belief = copy.deepcopy(belief_visible.union(belief_true))
                    print "LEAF BELIEF:", leaf_belief
                    leaf_plus_vis = belief_visible.union(belief_true)
                    
                    # partitions in the leaf node that will be refined
                    tr = set()
                    for b in beliefcombs[envstate - len(xstates)]:
                        tr.add(b)
                        neg_states = neg_states.union(partitionGrid[b].difference(leaf_plus_vis))
                    toRefine.append(tr)
                    
                    current_path.pop()
                    return leaf_belief
                else:
                    current_path.pop()
                    return set()     
        
        
        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        belief_true_next_current = copy.deepcopy(belief_true_next)
        true_plus_vis_next_current = copy.deepcopy(true_plus_vis_next)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        for succ in range(0,len(content),2):
            if (int(content[succ].split(' ')[1]) in nextposstates):
                if (not((succ,frozenset(belief_true_next_current)) in visited_pairs) and not(not belief_true_next_current and succ in visited_nodes) and not(succ in current_path)):
                    belief_true_next = copy.deepcopy(belief_true_next_current)
                    true_plus_vis_next = copy.deepcopy(true_plus_vis_next_current)
                    leaf_belief = traverse_counterexample_safety(fname,gwg,partitionGrid,belief_safety,succ,agentstate)
                    if toRefine:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine.append(tr)
                        current_path.pop()
                        return leaf_belief
        current_path.pop()    
        return set()

    def traverse_counterexample_liveness(fname,gwg,partitionGrid,belief_liveness,ind,agentstate_parent):

        global visited_nodes
        global visited_pairs
        global current_path   
        
        global belief_true_next
        global true_plus_vis_next
        
        global toRefine
        global prefix_length
        global leaf_belief
        global neg_states
        
        current_path.append(ind)
        visited_nodes.add(ind)
        #print 'INDEX IN COUNTEREXAMPLE ', ind
    
        envstatebin = []
        agentstatebin = []
        beliefstate = set()
        
        line = content[ind].split(' ')
        for r in line[6::]:
            if r[1] == 'y' or r[0] == 'y':
                envstatebin.append(r[-2])
            elif r[1] == 'x' or r[0] == 'x':
                agentstatebin.append(r[-2])
 
        # environment position
        envstate = int(''.join(str(e) for e in envstatebin)[::-1],2)
        if envstate < len(xstates):
            belief_true = {xstates[envstate]}
            true_plus_vis = {xstates[envstate]}
            #print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            belief_true = copy.deepcopy(belief_true_next)
            true_plus_vis = copy.deepcopy(true_plus_vis_next)
            #print 'Environment position is ', beliefstate    

         
        if (((ind,frozenset(belief_true)) in visited_pairs)): # already explored
            current_path.pop()
            return set()
        visited_pairs.add((ind,frozenset(belief_true)))
        path_beliefs.append((ind,frozenset(belief_true)))
           
        # agent position
        if len(agentstatebin) > 0:
            agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
            #print 'Agent position is ', agentstate
        else: # failure state
            current_path.pop()
            path_beliefs.pop()
            return set()
        if content[ind+1] == 'With no successors.': # terminal state
            current_path.pop()
            path_beliefs.pop()
            return set()

        # invisible states in belief w.r.t. previous position of agent
        belief_invisible = beliefstate.intersection(invisibilityset[0][agentstate_parent])
        belief_visible = beliefstate.difference(invisibilityset[0][agentstate_parent])

        path_abstract.append((envstate,frozenset(belief_invisible),frozenset(belief_visible)))

        # compute true belief for successor nodes w.r.t. current position of agent
        belief_true_next = set()
        for s in (belief_true - set(gwg.targets[0])):
            for a in gwg.actlist:
                for t in np.nonzero(gwg.prob[a][s])[0]:
                    belief_true_next.add(t)
        belief_true_next = belief_true_next - set(gwg.walls)
        true_plus_vis_next = copy.deepcopy(belief_true_next)
        belief_true_next = belief_true_next.intersection(invisibilityset[0][agentstate])    
                            

        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        belief_true_next_current = copy.deepcopy(belief_true_next)
        true_plus_vis_next_current = copy.deepcopy(true_plus_vis_next)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        for succ in range(0,len(content),2):
            if (int(content[succ].split(' ')[1]) in nextposstates):
                belief_true_next = copy.deepcopy(belief_true_next_current)
                true_plus_vis_next = copy.deepcopy(true_plus_vis_next_current)
                
                envstatebin_succ = []
                beliefstate_succ = set()
                line_succ = content[succ].split(' ')
                for r in line[6::]:
                    if r[1] == 'y' or r[0] == 'y':
                        envstatebin_succ.append(r[-2])
                envstate_succ = int(''.join(str(e) for e in envstatebin_succ)[::-1],2)
                if envstate_succ < len(xstates):
                    beliefstate_succ = {xstates[envstate]}
                else:
                    for b in beliefcombs[envstate_succ - len(xstates)]:
                        beliefstate_succ = beliefstate_succ.union(partitionGrid[b])
                belief_visible_succ = beliefstate_succ - invisibilityset[0][agentstate]
                belief_invisible_succ = beliefstate_succ.intersection(invisibilityset[0][agentstate])
                good_loop = False
                for (s,t), (e,bi,bv) in zip(reversed(path_beliefs),reversed(path_abstract)):
                    if (s,t) == (succ,frozenset(belief_true_next_current)):
                        break
                    if len(bi) < belief_liveness:
                        good_loop = True
                        break

                #if good_loop:
                #    continue
                    
                if belief_true_next_current and (succ,frozenset(belief_true_next_current)) in path_beliefs and len(belief_true_next_current) <= belief_liveness and len(belief_invisible_succ) > belief_liveness:
                    print 'LIVENESS'
                    print 'AGENT STATE',agentstate
                    print 'ABSTRACT BELIEF', beliefstate_succ
                    print 'TRUE BELIEF',belief_true_next_current
                    prefix_length = path_beliefs.index((succ,frozenset(belief_true_next_current)))
                   
                    leaf_belief = copy.deepcopy(belief_true_next)
                    #leaf_belief = copy.deepcopy(true_plus_vis_next)
                    #leaf_belief = copy.deepcopy(belief_visible_succ.union(belief_true_next_current))
                    print 'LEAF BELIEF',leaf_belief
                    leaf_plus_vis = belief_visible_succ.union(belief_true_next_current)
                           
                    tr_succ = set()
                    if envstate_succ >= len(xstates):
                        for b in beliefcombs[envstate_succ - len(xstates)]:
                            neg_states = neg_states.union(partitionGrid[b].difference(leaf_plus_vis))
                            if partitionGrid[b].intersection(belief_true_next):
                                tr_succ.add(b)
                        if not tr_succ:
                            for b in beliefcombs[envstate_succ - len(xstates)]:
                                tr_succ.add(b)            
                    toRefine.append(tr_succ)
                    
                    print 'NEG STATES 0', neg_states
                    
                    tr = set()
                    if envstate >= len(xstates):
                        for b in beliefcombs[envstate - len(xstates)]:
                            tr.add(b)
                    toRefine.append(tr)
                    current_path.pop()
                    path_beliefs.pop()
                    path_abstract.pop()
                    return leaf_belief                   
                if (not((succ,frozenset(belief_true_next_current)) in visited_pairs) and not((not belief_true_next_current) and succ in visited_nodes)): # and not(succ in current_path)
                    leaf_belief = traverse_counterexample_liveness(fname,gwg,partitionGrid,belief_liveness,succ,agentstate)
                    if toRefine:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine.append(tr)
                        current_path.pop()
                        path_beliefs.pop()
                        path_abstract.pop()
                        return leaf_belief
        current_path.pop()
        path_beliefs.pop()    
        path_abstract.pop()
        return set() 
        
    def traverse_counterexample_ltl(fname,gwg,partitionGrid,targets,ind,agentstate_parent):

        global visited_nodes
        global visited_pairs
        global current_path   
        
        global belief_true_next
        global true_plus_vis_next
        
        global toRefine
        global prefix_length
        global leaf_belief
        global neg_states
        
        current_path.append(ind)
        visited_nodes.add(ind)
        #print 'INDEX IN COUNTEREXAMPLE ', ind
    
        envstatebin = []
        agentstatebin = []
        beliefstate = set()
        
        line = content[ind].split(' ')
        for r in line[6::]:
            if r[1] == 'y' or r[0] == 'y':
                envstatebin.append(r[-2])
            elif r[1] == 'x' or r[0] == 'x':
                agentstatebin.append(r[-2])
 
        # environment position
        envstate = int(''.join(str(e) for e in envstatebin)[::-1],2)
        if envstate < len(xstates):
            belief_true = {xstates[envstate]}
            true_plus_vis = {xstates[envstate]}
            #print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            belief_true = copy.deepcopy(belief_true_next)
            true_plus_vis = copy.deepcopy(true_plus_vis_next)
            #print 'Environment position is ', beliefstate    

         
        if (((ind,frozenset(belief_true)) in visited_pairs)): # already explored
            current_path.pop()
            return set()
        visited_pairs.add((ind,frozenset(belief_true)))
        path_beliefs.append((ind,frozenset(belief_true)))
           
        # agent position
        if len(agentstatebin) > 0:
            agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
            #print 'Agent position is ', agentstate
        else: # failure state
            current_path.pop()
            path_beliefs.pop()
            return set()
        if content[ind+1] == 'With no successors.': # terminal state
            current_path.pop()
            path_beliefs.pop()
            return set()

        # invisible states in belief w.r.t. previous position of agent
        belief_invisible = beliefstate.intersection(invisibilityset[0][agentstate_parent])
        belief_visible = beliefstate.difference(invisibilityset[0][agentstate_parent])

        if len(beliefstate) > 0:
            path_abstract.append((envstate,frozenset(belief_invisible),frozenset(belief_visible)))
        else:
            path_abstract.append((envstate,frozenset(set()),frozenset(set())))

        # compute true belief for successor nodes w.r.t. current position of agent
        belief_true_next = set()
        for s in (belief_true - set(gwg.targets[0])):
            for a in gwg.actlist:
                for t in np.nonzero(gwg.prob[a][s])[0]:
                    belief_true_next.add(t)
        belief_true_next = belief_true_next - set(gwg.walls)
        true_plus_vis_next = copy.deepcopy(belief_true_next)
        belief_true_next = belief_true_next.intersection(invisibilityset[0][agentstate])    

        leaf_belief = copy.deepcopy(belief_true)
        #leaf_belief = copy.deepcopy(true_plus_vis)
        #leaf_belief = copy.deepcopy(belief_visible.union(belief_true))
        leaf_plus_vis = copy.deepcopy(belief_visible.union(belief_true))
        
        if len(beliefstate) > 0:
            if (len(belief_invisible) > len(belief_true)):
                # belief state imprecise: possibly refine for LTL spec
                if not toRefine:
                    tr = set()
                    for b in beliefcombs[envstate - len(xstates)]:
                        tr.add(b)
                        neg_states = neg_states.union(partitionGrid[b].difference(leaf_plus_vis))
                    toRefine.append(tr)
                    return leaf_belief                            

        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        belief_true_next_current = copy.deepcopy(belief_true_next)
        true_plus_vis_next_current = copy.deepcopy(true_plus_vis_next)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        for succ in range(0,len(content),2):
            if (int(content[succ].split(' ')[1]) in nextposstates):
                if (not((succ,frozenset(belief_true_next_current)) in visited_pairs) and not(not belief_true_next_current and succ in visited_nodes) and not(succ in current_path)):
                    belief_true_next = copy.deepcopy(belief_true_next_current)
                    true_plus_vis_next = copy.deepcopy(true_plus_vis_next_current)
                    leaf_belief = traverse_counterexample_ltl(fname,gwg,partitionGrid,targets,succ,agentstate)
                    if toRefine:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine.append(tr)
                        current_path.pop()
                        path_beliefs.pop()    
                        path_abstract.pop()
                        return leaf_belief
        current_path.pop()
        path_beliefs.pop()    
        path_abstract.pop()
        return set() 
        
    def traverse_counterexample_liveness_basic(fname,gwg,partitionGrid,belief_liveness,ind,agentstate_parent):

        global visited_nodes
        global visited_pairs
        global current_path   
        
        global belief_true_next
        global true_plus_vis_next
        
        global toRefine
        global leaf_belief
        global neg_states
            
        current_path.append(ind)
        visited_nodes.add(ind)
        #print 'INDEX IN COUNTEREXAMPLE ', ind
    
        envstatebin = []
        agentstatebin = []
        beliefstate = set()
        
        line = content[ind].split(' ')
        for r in line[6::]:
            if r[1] == 'y' or r[0] == 'y':
                envstatebin.append(r[-2])
            elif r[1] == 'x' or r[0] == 'x':
                agentstatebin.append(r[-2])
 
        # environment position
        envstate = int(''.join(str(e) for e in envstatebin)[::-1],2)
        if envstate < len(xstates):
            belief_true = {xstates[envstate]}
            true_plus_vis = {xstates[envstate]}
            #print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            belief_true = copy.deepcopy(belief_true_next)
            true_plus_vis = copy.deepcopy(true_plus_vis_next)
            #print 'Environment position is ', beliefstate    


        if (((ind,frozenset(belief_true)) in visited_pairs)): # already explored
            current_path.pop()
            return set()
        visited_pairs.add((ind,frozenset(belief_true)))
        path_beliefs.append((ind,frozenset(belief_true)))

        # agent position
        if len(agentstatebin) > 0:
            agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
            #print 'Agent position is ', agentstate
        else: # failure state
            current_path.pop()
            path_beliefs.pop()
            return set()
        if content[ind+1] == 'With no successors.': # terminal state
            current_path.pop()
            path_beliefs.pop()
            return set()

        # invisible states in belief w.r.t. previous position of agent
        belief_invisible = beliefstate.intersection(invisibilityset[0][agentstate_parent])
        belief_visible = beliefstate - invisibilityset[0][agentstate_parent]

        if len(beliefstate) > 0:
            path_abstract.append((envstate,frozenset(belief_invisible),frozenset(belief_visible)))
        else:
            path_abstract.append((envstate,frozenset(set()),frozenset(set())))
        
        
        # compute true belief for successor nodes w.r.t. current position of agent
        belief_true_next = set()
        for s in (belief_true - set(gwg.targets[0])):
            for a in gwg.actlist:
                for t in np.nonzero(gwg.prob[a][s])[0]:
                    belief_true_next.add(t)
        belief_true_next = belief_true_next - set(gwg.walls)
        true_plus_vis_next = copy.deepcopy(belief_true_next)
        belief_true_next = belief_true_next.intersection(invisibilityset[0][agentstate])    

      
        if len(beliefstate) > 0:
            if len(belief_invisible) > belief_liveness and len(belief_true) <= belief_liveness: 
            # belief violates the constraint and true belief satisfies constraint
                print 'LIVENESS'
                print 'Invisible states in belief:', belief_invisible
                print "Precise belief:", belief_true
                print "Belief vis:", belief_visible
                
                # partitions in the leaf node that will be refined
                tr = set()
                for b in beliefcombs[envstate - len(xstates)]:
                    tr.add(b)
                toRefine.append(tr)
                    
                leaf_belief = copy.deepcopy(true_plus_vis)
                #leaf_belief = copy.deepcopy(belief_visible.union(belief_true))
                    
                current_path.pop()    
                return leaf_belief

        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        belief_true_next_current = copy.deepcopy(belief_true_next)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        for succ in range(0,len(content),2):
            if (int(content[succ].split(' ')[1]) in nextposstates):
                belief_true_next = copy.deepcopy(belief_true_next_current)
                if (not((succ,frozenset(belief_true_next_current)) in visited_pairs) and not((not belief_true_next_current) and succ in visited_nodes) and not(succ in current_path)): 
                    leaf_belief = traverse_counterexample_liveness_basic(fname,gwg,partitionGrid,belief_liveness,succ,agentstate)
                    if toRefine:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine.append(tr)
                        current_path.pop()
                        path_beliefs.pop()
                        return leaf_belief
        current_path.pop()
        path_beliefs.pop()    
        return set() 

    #def traverse_counterexample_liveness(fname,gwg,partitionGrid,belief_liveness,ind,agentstate_parent):
        #global current_path 
        #global path_beliefs
            
        #global belief_true_next
        #global true_plus_vis_next
        
        #global toRefine
        
        #current_path.append(ind)
        ##print 'INDEX IN COUNTEREXAMPLE ', ind
        #envstatebin = []
        #agentstatebin = []
        #beliefstate = set()
        
        #line = content[ind].split(' ')
        #for r in line[6::]:
            #if r[1] == 'y' or r[0] == 'y':
                #envstatebin.append(r[-2])
            #elif r[1] == 'x' or r[0] == 'x':
                #agentstatebin.append(r[-2])
        
        ## agent position
        #if len(agentstatebin) > 0:
            #agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
            ##print 'Agent position is ', agentstate
        #else: # failure state
            #current_path.pop()
            #return set()
        #if content[ind+1] == 'With no successors.': # terminal state
            #current_path.pop()
            #return set()

        ## environment position
        #envstate = int(''.join(str(e) for e in envstatebin)[::-1],2)
        #if envstate < len(xstates):
            #belief_true = {xstates[envstate]}
            #true_plus_vis = {xstates[envstate]}
            ##print 'Environment position is ', xstates[envstate]
        #else:
            #for b in beliefcombs[envstate - len(xstates)]:
                #beliefstate = beliefstate.union(partitionGrid[b])
            #belief_true = copy.deepcopy(belief_true_next)
            #true_plus_vis = copy.deepcopy(true_plus_vis_next)
            ##print 'Environment position is ', beliefstate    
        
        
        ## compute true belief for successor nodes w.r.t. current position of agent
        #belief_true_next = set()
        #for s in belief_true:
            #for a in gwg.actlist:
                #for t in np.nonzero(gwg.prob[a][s])[0]:
                    #belief_true_next.add(t)
        #belief_true_next = belief_true_next - set(gwg.walls)
        #true_plus_vis_next = copy.deepcopy(belief_true_next)
        #belief_true_next = belief_true_next.intersection(visibility.invis(gwg,agentstate))    

      
        #if len(beliefstate) > 0:

            ## invisible states in belief w.r.t. previous position of agent
            #belief_invisible = beliefstate.intersection(visibility.invis(gwg,agentstate_parent))
            
            #if len(belief_invisible) > belief_liveness and len(belief_true) <= belief_liveness:
                #print 'CANDIDATE', ind
                
            #tr = set()
            #for b in beliefcombs[envstate - len(xstates)]:
                #tr.add(b)
            #path_beliefs.append((belief_invisible,belief_true,true_plus_vis,tr)) 
        
            #if (len(beliefstate) > len(belief_true)):
                ## belief state imprecise: possibly refine for LTL spec
                #if not toRefine:
                    #for b in beliefcombs[envstate - len(xstates)]:
                        #if b in toRefine:
                            #toRefine[b].append(belief_true)
                        #else:
                            #toRefine[b] = list()
                            #toRefine[b].append(belief_true)
        #else:
            #path_beliefs.append((belief_true,belief_true,true_plus_vis,set()))
        
        #'''
        #recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        #if in some subtree such node is found, add the current node to the counterexample and return 
        #'''
        #belief_true_next_current = copy.deepcopy(belief_true_next)
        #nextposstates = map(int,content[ind+1][18:].split(', '))
        #for succ in range(0,len(content),2):
            #if (int(content[succ].split(' ')[1]) in nextposstates):
                #if (succ not in current_path):
                    #belief_true_next = copy.deepcopy(belief_true_next_current)
                    #leaf_belief = traverse_counterexample_liveness(fname,gwg,partitionGrid,belief_liveness,succ,agentstate)
                    #if toRefine:
                        #return leaf_belief
                #else:# found the loop of a lasso path
                    #ref_found = False
                    #leaf_belief = set()
                    ##print 'LOOP', current_path, succ
                    #for (i,b) in zip(reversed(current_path),reversed(path_beliefs)):
                        #(b_invisible,b_true,true_visible,tr) = b
                                               
                        #if not ref_found and len(b_invisible) > belief_liveness and len(b_true) <= belief_liveness:
                            #ref_found = True
                            #leaf_belief = copy.deepcopy(true_visible)
                            #print 'LIVENESS', ind
                            #print 'Invisible states in belief:', b_invisible
                            #print "Precise belief:", b_true
                        #if i == succ and not ref_found:
                            #break
                        #if ref_found and tr:
                            #toRefine.append(tr)
                            #break
                        #if ref_found and not tr:
                            #break    
                    #if ref_found:
                        #return leaf_belief
        #if not toRefine:
            #current_path.pop()
            #path_beliefs.pop()
        #return set()
    
    if belief_safety > 0:
        leaf_belief = traverse_counterexample_safety(fname,gwg,partitionGrid,belief_safety,0,gwg.current[0])
        ref = 'safety'
        
    if not toRefine and belief_liveness > 0:
        visited_nodes = set()   
        visited_pairs = set()   

        current_path = list()
        path_beliefs = list()
        path_abstract = list()

        belief_true_next = set()
        true_plus_vis_next = set()

        leaf_belief = traverse_counterexample_liveness(fname,gwg,partitionGrid,belief_liveness,0,gwg.current[0])
        ref = 'liveness'
    if not toRefine and len(targets) > 0:
        visited_nodes = set()   
        visited_pairs = set()   

        current_path = list()
        path_beliefs = list()
        path_abstract = list()

        belief_true_next = set()
        true_plus_vis_next = set()

        leaf_belief = traverse_counterexample_ltl(fname,gwg,partitionGrid,targets,0,gwg.current[0])
        ref = 'ltl'
    if not toRefine:
        ref = 'none'    
        
    return (ref,toRefine,leaf_belief,neg_states,prefix_length)

def remove_leq(list_of_sets,a_set):
    subsumed = False
    keep = list()
    for s in list_of_sets:
        if s <= a_set:
            continue
        if s > a_set:
            subsumed = True
        keep.append(s)
    return (subsumed,keep)
    #return (False,list_of_sets)
    
