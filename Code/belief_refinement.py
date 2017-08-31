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

path_beliefs = list()
path_abstract = list()

belief_true_next = set()

'''
stores information about the path in the counterexample tree along which we will refine
each element of the list is a set of partitions forming the belief in the current position
'''
toRefine = list()
refine_states = set()
neg_states = set()
prefix_length = 0

def analyse_counterexample(fname,gwg,partitionGrid,belief_safety,belief_liveness,target_reachability,targets):
    global visited_nodes
    global visited_pairs

    global path_beliefs
    global path_abstract
    
    global belief_true_next
     
    global toRefine
    global prefix_length
    global refine_states
    global neg_states 
    
    visited_nodes = set()
    visited_pairs = set()

    path_beliefs = list()
    path_abstract = list()
    
    belief_true_next = set()
    
    toRefine = list()  
    prefix_length = 0
    refine_states = set()
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
            invisibilityset[n][s] = visibility.invis(gwg,s) #- set(gwg.targets[n])
            if s in gwg.obstacles:
                invisibilityset[n][s] = {-1}

    def traverse_counterexample_safety(fname,gwg,partitionGrid,belief_safety,ind,agentstate_parent):

        global visited_nodes
        global visited_pairs
        
            
        global belief_true_next
        
        global toRefine
        global refine_states
        global neg_states
        
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
            return
        if content[ind+1] == 'With no successors.': # terminal state
            return

        # environment position
        envstate = int(''.join(str(e) for e in envstatebin)[::-1],2)
        if envstate < len(xstates):
            belief_true = {xstates[envstate]}
            #print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            beliefstate = beliefstate - set(gwg.targets[0])
            belief_true = copy.deepcopy(belief_true_next)
            #print 'Environment position is ', beliefstate    
 
 
        if (((ind,frozenset(belief_true)) in visited_pairs)): # already explored
            return       
        
        visited_pairs.add((ind,frozenset(belief_true)))
        
        
        # compute true belief for successor nodes w.r.t. current position of agent
        belief_true_next = set()
        for s in (belief_true - set(gwg.targets[0])):
            for a in gwg.actlist:
                for t in np.nonzero(gwg.prob[a][s])[0]:
                    if t in gwg.targets[0]: 
                        continue # do not add goal locations
                    belief_true_next.add(t)
        belief_true_next = belief_true_next - set(gwg.walls)
        belief_true_next = belief_true_next.intersection(invisibilityset[0][agentstate])    
        
      
        
        if len(beliefstate) > 0:
            
            # invisible states in belief w.r.t. previous position of agent
            belief_invisible = beliefstate.intersection(invisibilityset[0][agentstate_parent])
            belief_visible = beliefstate - invisibilityset[0][agentstate_parent]
        
            if len(belief_invisible) > 0 and len(belief_true) == 0:
                print 'UNCONCRETIZABLE PATH'
                print 'AGENT STATE',agentstate_parent
                print 'ABSTRACT BELIEF', beliefstate
                print 'ABSTRACT BELIEF INVISIBLE', belief_invisible
                
                refine_states = copy.deepcopy(belief_true)
                  
                # partitions in the leaf node that will be refined
                tr = set()
                for b in beliefcombs[envstate - len(xstates)]:
                    tr.add(b)
                    neg_states = neg_states.union(partitionGrid[b].difference(belief_visible))
                    toRefine.append(tr)
                return

            if len(belief_invisible) > belief_safety: # belief violates constraint
                if len(belief_true) <= belief_safety: # true belief satisfies constraint
                    print 'SAFETY'
                    print 'AGENT STATE',agentstate_parent
                    print 'ABSTRACT BELIEF', beliefstate
                    print 'ABSTRACT BELIEF INVISIBLE', belief_invisible
                    print 'TRUE BELIEF',belief_true
                    
                    refine_states = copy.deepcopy(belief_true)
                    leaf_plus_vis = belief_visible.union(belief_true)
                   
                    # partitions in the leaf node that will be refined
                    tr = set()
                    for b in beliefcombs[envstate - len(xstates)]:
                        tr.add(b)
                        neg_states = neg_states.union(partitionGrid[b].difference(leaf_plus_vis))
                    toRefine.append(tr)
                return
        
        
        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        belief_true_next_current = copy.deepcopy(belief_true_next)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        for succ in range(0,len(content),2):
            belief_true_next = copy.deepcopy(belief_true_next_current)
            if (int(content[succ].split(' ')[1]) in nextposstates):
                if (not((succ,frozenset(belief_true_next)) in visited_pairs) and not(len(belief_true_next)==0 and succ in visited_nodes)):
                    traverse_counterexample_safety(fname,gwg,partitionGrid,belief_safety,succ,agentstate)
                    if toRefine:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine.append(tr)
                        return
        return

    def traverse_counterexample_liveness(fname,gwg,partitionGrid,belief_liveness,ind,agentstate_parent):

        global visited_nodes
        global visited_pairs
        
        global belief_true_next
        
        global toRefine
        global prefix_length
        global refine_states
        global neg_states
        
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
            #print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            beliefstate = beliefstate - set(gwg.targets[0])
            belief_true = copy.deepcopy(belief_true_next)
            #print 'Environment position is ', beliefstate    

         
        if (((ind,frozenset(belief_true)) in visited_pairs)): # already explored
            return
        visited_pairs.add((ind,frozenset(belief_true)))
        path_beliefs.append((ind,frozenset(belief_true)))
           
        # agent position
        if len(agentstatebin) > 0:
            agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
            #print 'Agent position is ', agentstate
        else: # failure state
            path_beliefs.pop()
            return
        if content[ind+1] == 'With no successors.': # terminal state
            path_beliefs.pop()
            return

        # invisible states in belief w.r.t. previous position of agent
        belief_invisible = beliefstate.intersection(invisibilityset[0][agentstate_parent])
        belief_visible = beliefstate.difference(invisibilityset[0][agentstate_parent])

        path_abstract.append((envstate,frozenset(belief_invisible),frozenset(belief_visible)))

        if len(belief_invisible) > 0 and len(belief_true) == 0:
            print 'UNCONCRETIZABLE PATH'
            print 'AGENT STATE',agentstate_parent
            print 'ABSTRACT BELIEF', beliefstate
            print 'ABSTRACT BELIEF INVISIBLE', belief_invisible    
            
            refine_states = copy.deepcopy(belief_true)
                  
            # partitions in the leaf node that will be refined
            tr = set()
            for b in beliefcombs[envstate - len(xstates)]:
                tr.add(b)
                neg_states = neg_states.union(partitionGrid[b].difference(belief_visible))
                toRefine.append(tr)
            
            prefix_length = 0    
            path_beliefs.pop()
            path_abstract.pop()
            return
            
        # compute true belief for successor nodes w.r.t. current position of agent
        belief_true_next = set()
        for s in (belief_true - set(gwg.targets[0])):
            for a in gwg.actlist:
                for t in np.nonzero(gwg.prob[a][s])[0]:
                    if t in gwg.targets[0]: 
                        continue # do not add goal locations
                    belief_true_next.add(t)
        belief_true_next = belief_true_next - set(gwg.walls)
        belief_true_next = belief_true_next.intersection(invisibilityset[0][agentstate])    
                            
        
        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        belief_true_next_current = copy.deepcopy(belief_true_next)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        for succ in range(0,len(content),2):
            belief_true_next = copy.deepcopy(belief_true_next_current)
            if (int(content[succ].split(' ')[1]) in nextposstates):
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
                    beliefstate_succ = beliefstate_succ - set(gwg.targets[0])
                belief_visible_succ = beliefstate_succ - invisibilityset[0][agentstate]
                belief_invisible_succ = beliefstate_succ.intersection(invisibilityset[0][agentstate])
                
                good_loop = False
                for (s,t), (e,bi,bv) in zip(reversed(path_beliefs),reversed(path_abstract)):
                    if (s,t) == (succ,frozenset(belief_true_next)):
                        break
                    if len(bi) <= belief_liveness:
                        good_loop = True
                        break

                #if good_loop:
                #    continue
                    
                if belief_true_next and (succ,frozenset(belief_true_next)) in path_beliefs and len(belief_true_next) <= belief_liveness and len(belief_invisible_succ) > belief_liveness:
                    print 'LIVENESS'
                    print 'AGENT STATE',agentstate
                    print 'ABSTRACT BELIEF', beliefstate_succ
                    print 'ABSTRACT BELIEF INVISIBLE', belief_invisible_succ
                    print 'TRUE BELIEF',belief_true_next
                    
                    #print 'PATH BELIEFS', path_beliefs
                    #print 'SUCC', (succ,frozenset(belief_true_next))
                    
                    prefix_length = path_beliefs.index((succ,frozenset(belief_true_next)))
                   
                    refine_states = copy.deepcopy(belief_true_next)
                    leaf_plus_vis = belief_visible_succ.union(belief_true_next)
                           
                    tr_succ = set()
                    if envstate_succ >= len(xstates):
                        for b in beliefcombs[envstate_succ - len(xstates)]:
                            neg_states = neg_states.union(partitionGrid[b].difference(leaf_plus_vis))
                            tr_succ.add(b)
                    toRefine.append(tr_succ)
                    
                 
                    tr = set()
                    if envstate >= len(xstates):
                        for b in beliefcombs[envstate - len(xstates)]:
                            tr.add(b)
                    toRefine.append(tr)

                    path_beliefs.pop()
                    path_abstract.pop()
                    return                

                if (not((succ,frozenset(belief_true_next)) in visited_pairs) and not(len(belief_true_next) == 0 and succ in visited_nodes)): 
                    traverse_counterexample_liveness(fname,gwg,partitionGrid,belief_liveness,succ,agentstate)
                    if toRefine:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine.append(tr)
                        path_beliefs.pop()
                        path_abstract.pop()
                        return
        path_beliefs.pop()    
        path_abstract.pop()
        return
        
    def traverse_counterexample_ltl(fname,gwg,partitionGrid,targets,ind,agentstate_parent):

        global visited_nodes
        global visited_pairs
        
        global belief_true_next
        
        global toRefine
        global refine_states
        global neg_states
        
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
            #print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            beliefstate = beliefstate - set(gwg.targets[0])
            belief_true = copy.deepcopy(belief_true_next)
            #print 'Environment position is ', beliefstate    

         
        if (((ind,frozenset(belief_true)) in visited_pairs)): # already explored
            return
        visited_pairs.add((ind,frozenset(belief_true)))
           
        # agent position
        if len(agentstatebin) > 0:
            agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
            #print 'Agent position is ', agentstate
        else: # failure state
            return
        if content[ind+1] == 'With no successors.': # terminal state
            return

        # invisible states in belief w.r.t. previous position of agent
        belief_invisible = beliefstate.intersection(invisibilityset[0][agentstate_parent])
        belief_visible = beliefstate.difference(invisibilityset[0][agentstate_parent])

        # compute true belief for successor nodes w.r.t. current position of agent
        belief_true_next = set()
        for s in (belief_true - set(gwg.targets[0])):
            for a in gwg.actlist:
                for t in np.nonzero(gwg.prob[a][s])[0]:
                    if t in gwg.targets[0]: 
                        continue # do not add goal locations
                    belief_true_next.add(t)
        belief_true_next = belief_true_next - set(gwg.walls)
        belief_true_next = belief_true_next.intersection(invisibilityset[0][agentstate])    

        if len(belief_invisible) > 0 and len(belief_true) == 0:
            print 'UNCONCRETIZABLE PATH'
            print 'AGENT STATE',agentstate_parent
            print 'ABSTRACT BELIEF INVISIBLE', belief_invisible
            print 'ABSTRACT BELIEF', beliefstate
                
            refine_states = copy.deepcopy(belief_true)
                  
            # partitions in the leaf node that will be refined
            tr = set()
            for b in beliefcombs[envstate - len(xstates)]:
                tr.add(b)
                neg_states = neg_states.union(partitionGrid[b].difference(belief_visible))
                toRefine.append(tr)
            
            return
            
        if (len(belief_invisible) > len(belief_true)):
            print 'LTL'
            print 'AGENT STATE',agentstate_parent
            print 'ABSTRACT BELIEF', beliefstate
            print 'ABSTRACT BELIEF INVISIBLE', belief_invisible
            print 'TRUE BELIEF',belief_true
                    
                
            refine_states = copy.deepcopy(belief_true)
            leaf_plus_vis = copy.deepcopy(belief_visible.union(belief_true))
        
            # belief state imprecise: refine for LTL spec
            tr = set()
            for b in beliefcombs[envstate - len(xstates)]:
                tr.add(b)
                neg_states = neg_states.union(partitionGrid[b].difference(leaf_plus_vis))
            toRefine.append(tr)
            return                           

        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        belief_true_next_current = copy.deepcopy(belief_true_next)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        for succ in range(0,len(content),2):
            belief_true_next = copy.deepcopy(belief_true_next_current)
            if (int(content[succ].split(' ')[1]) in nextposstates):
                if (not((succ,frozenset(belief_true_next)) in visited_pairs) and not(not belief_true_next and succ in visited_nodes)): 
                    traverse_counterexample_ltl(fname,gwg,partitionGrid,targets,succ,agentstate)
                    if toRefine:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine.append(tr)
                        return
        return
        
    def traverse_counterexample_liveness_basic(fname,gwg,partitionGrid,belief_liveness,ind,agentstate_parent):

        global visited_nodes
        global visited_pairs
        
        global belief_true_next
        
        global toRefine
        global refine_states
        global neg_states
            
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
            #print 'Environment position is ', xstates[envstate]
        else:
            for b in beliefcombs[envstate - len(xstates)]:
                beliefstate = beliefstate.union(partitionGrid[b])
            beliefstate = beliefstate - set(gwg.targets[0])
            belief_true = copy.deepcopy(belief_true_next)
            #print 'Environment position is ', beliefstate    


        if (((ind,frozenset(belief_true)) in visited_pairs)): # already explored
            return
        visited_pairs.add((ind,frozenset(belief_true)))

        # agent position
        if len(agentstatebin) > 0:
            agentstate = xstates[int(''.join(str(e) for e in agentstatebin)[::-1], 2)]
            #print 'Agent position is ', agentstate
        else: # failure state
            return
        if content[ind+1] == 'With no successors.': # terminal state
            return

        # invisible states in belief w.r.t. previous position of agent
        belief_invisible = beliefstate.intersection(invisibilityset[0][agentstate_parent])
        belief_visible = beliefstate - invisibilityset[0][agentstate_parent]

        
        # compute true belief for successor nodes w.r.t. current position of agent
        belief_true_next = set()
        for s in (belief_true - set(gwg.targets[0])):
            for a in gwg.actlist:
                for t in np.nonzero(gwg.prob[a][s])[0]:
                    if t in gwg.targets[0]: 
                        continue # do not add goal locations
                    belief_true_next.add(t)
        belief_true_next = belief_true_next - set(gwg.walls)
        belief_true_next = belief_true_next.intersection(invisibilityset[0][agentstate])    

        if len(belief_invisible) > 0 and len(belief_true) == 0:
            print 'UNCONCRETIZABLE PATH'
            print 'AGENT STATE',agentstate_parent
            print 'ABSTRACT BELIEF', beliefstate
            print 'ABSTRACT BELIEF INVISIBLE', belief_invisible
                    
            refine_states = copy.deepcopy(belief_true)
                  
            # partitions in the leaf node that will be refined
            tr = set()
            for b in beliefcombs[envstate - len(xstates)]:
                tr.add(b)
                neg_states = neg_states.union(partitionGrid[b].difference(belief_visible))
                toRefine.append(tr)
            
            return
            
        leaf_plus_vis = belief_visible.union(belief_true)
        
        if len(beliefstate) > 0:
            if len(belief_invisible) >  len(belief_true): 
            # belief violates the constraint and true belief satisfies constraint
                print 'LIVENESS'
                print 'AGENT STATE',agentstate_parent
                print 'ABSTRACT BELIEF', beliefstate
                print 'ABSTRACT BELIEF INVISIBLE', belief_invisible
                print 'TRUE BELIEF',belief_true
                
                # partitions in the leaf node that will be refined
                tr = set()
                for b in beliefcombs[envstate - len(xstates)]:
                    tr.add(b)
                    neg_states = neg_states.union(partitionGrid[b].difference(leaf_plus_vis))
                toRefine.append(tr)

            
                refine_states = copy.deepcopy(belief_true)
                    
                return

        '''
        recurse over the successors (subtrees) of the current node, searching for a leaf node to refine
        if in some subtree such node is found, add the current node to the counterexample and return 
        '''
        belief_true_next_current = copy.deepcopy(belief_true_next)
        nextposstates = map(int,content[ind+1][18:].split(', '))
        for succ in range(0,len(content),2):
            belief_true_next = copy.deepcopy(belief_true_next_current)
            if (int(content[succ].split(' ')[1]) in nextposstates):
                if (not((succ,frozenset(belief_true_next)) in visited_pairs) and not((not belief_true_next) and succ in visited_nodes)): 
                    traverse_counterexample_liveness_basic(fname,gwg,partitionGrid,belief_liveness,succ,agentstate)
                    if toRefine:
                        tr = set()
                        if envstate >= len(xstates):
                            for b in beliefcombs[envstate - len(xstates)]:
                                tr.add(b)
                        toRefine.append(tr)
                        return
        return

 
    if belief_safety > 0:
        traverse_counterexample_safety(fname,gwg,partitionGrid,belief_safety,0,gwg.current[0])
        ref = 'safety'
        
    if not toRefine and belief_liveness > 0:
        visited_nodes = set()   
        visited_pairs = set()   

        path_beliefs = list()
        path_abstract = list()

        belief_true_next = set()

        traverse_counterexample_liveness(fname,gwg,partitionGrid,belief_liveness,0,gwg.current[0])
        ref = 'liveness'
    
    if not toRefine and target_reachability:
        visited_nodes = set()   
        visited_pairs = set()   

        belief_true_next = set()

        traverse_counterexample_ltl(fname,gwg,partitionGrid,targets,0,gwg.current[0])
        ref = 'ltl'
    if not toRefine:
        ref = 'none'    
        
    return (ref,toRefine,refine_states,neg_states,prefix_length)

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

    
