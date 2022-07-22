"""Made by Dr. Fox
sequences module. Manipulate sequences connected to nested recurrences.

Members:
-Sequence: A class for representing sequences
-Recurrence: A class for representing recurrence relations
-seq_terms: A function for generating terms of a sequence
"""
import sympy

#Sequence class
#Represents an abstract sequence object
class Sequence:
    """A class representing abstract sequence objects
    
    Methods:
    -__init__(other = None)
    -set_value(idx, val)
    -set_default_values(cond_f, val_or_val_f)
    -__setitem__(key, val)
    -__getitem__(key)
    -__str__()
    """
    #Constructor
    #If no arguments are passed, generate an empty sequence
    #If a sequence is passed as an argument, make a copy of it
    #If a list-like object is passed as an argument,
    #initialize the sequence with the given values as initial
    #values, starting from index 1.
    def __init__(self, other = None):
        """Create a new sequence.
        
        By default, create an empty sequence.
        If a Sequence is passed as an argument, instead copy it.
        If a list-like object is passed as an argument, make that
        into initial conditions, starting from index 1.
        """
        if other is None:
            #Make a new sequence
            self.data = dict()
            self.default_data = []
        elif isinstance(other, Sequence):
            #Make a copy
            self.data = dict(other.data)
            self.default_data = list(other.default_data)
        else:
            #Make a new sequence with the data in other as
            #initial values, starting from index 1
            self.data = dict()
            self.default_data = []
            self[1:] = other
    
    def set_value(self, idx, val):
        """Put value val into index idx in the sequence."""
        self.data[idx] = val
    
    def __setitem__(self, key, val):
        """Override the indexing [] operator to allow assignment.
        
        If variable seq holds a Sequence:
        -seq[i] = j puts value j into index i.
        -seq[i:] = L (a list) puts the values of L into seq, starting at index i.
        -seq[i] = f (a function) puts value f(i) into index i.
        -seq[i:j] = k puts value k into indices i, i+1, i+2,...,j-1.
        -seq[i:j] = f (a function) puts values f(i), f(i+1),..., f(j-1) into indices i, i+1,...,j-1.
        -seq[f] = i (f a boolean-valued function) puts value i into every index where f is True.
        -seq[f] = g (f a boolean-valued function, g an integer-value function) puts value g(i) into every index i where f is true.
        The first two modes have "higher priority." They are not overwritten by other modes.
        """
        if isinstance(key, slice):
            #Deal with slices
            if key.step is None:
                step = 1
            else:
                step = key.step
            start = key.start
            stop = key.stop
            #Case 1: val is atomic
            if isinstance(val, int) or isinstance(val, sympy.Symbol) or callable(val):
                if start is None and stop is None:
                    #Deal with seq[:] = j and seq[::i] = j
                    if step == 1 or step == -1:
                        self.set_default_values(lambda x: True, val)
                    else:
                        self.set_default_values(lambda x: x % abs(step) == 0, val)
                elif start is None:
                    #Deal with seq[:i] = j and seq[:i:j] = k
                    if step == 1:
                        self.set_default_values(lambda x: x - stop < 0, val)
                    elif step > 1:
                        self.set_default_values(lambda x: x - stop < 0 and (stop - x) % step == 1, val)
                    elif step == -1:
                        self.set_default_values(lambda x: x - stop > 0, val)
                    elif step < -1:
                        self.set_default_values(lambda x: x - stop > 0 and (x - stop) % (-step) == 1, val)
                    else:
                        raise ValueError("Invalid step: %s" % str(step))
                elif stop is None:
                    #Deal with seq[i:] = j and seq[i::j] = k
                    if step == 1:
                        self.set_default_values(lambda x: x - start >= 0, val)
                    elif step > 1:
                        self.set_default_values(lambda x: x - start >= 0 and (x - start) % step == 0, val)
                    elif step == -1:
                        self.set_default_values(lambda x: x - start <= 0, val)
                    elif step < -1:
                        self.set_default_values(lambda x: x - start <= 0 and (start - x) % (-step) == 0, val)
                    else:
                        raise ValueError("Invalid step: %s" % str(step))
                elif step > 0:
                    #Deal with seq[i:j] = k and seq[i:j:s] = k for positive s
                    self.set_default_values(lambda x: x >= start and x < stop and (x - start) % step == 0, val)
                elif step < 0:
                    #Deal with seq[i:j:s] = k for negative s
                    self.set_default_values(lambda x: x <= start and x > stop and (start - x) % (-step) == 0, val)
                else:
                    raise ValueError("Invalid step: %s" % str(step))
            #Case 2: val is a list-like object
            else:
                if start is None and stop is None:
                    #"Deal" with seq[:] = L
                    raise ValueError("Cannot assign a list to an unspecified slice.")
                elif start is None:
                    #Deal with seq[:i] = L and seq[:i:j] = L
                    start = stop - len(val) * step
                elif stop is None:
                    #Deal with seq[i:] = L and seq[i::j] = L
                    stop = start + len(val) * step
                #Insert the values into the list
                i = start
                j = 0
                while j < len(val) and ((step > 0 and i - start < stop - start) or\
                                        (step < 0 and start - i < start - stop)):
                    self[i] = val[j]
                    i += step
                    j += 1
        elif callable(val):
            #Deal with seq[i] = f
            self.set_default_values(lambda x: x == key, val)
        else:
            #Deal with seq[i] = j
            self.set_value(key, val)
    
    def set_default_values(self, cond_f, val_or_val_f):
        """
        Use a conditional to set default values for a bunch of indices.
        
        Arguments:
        -cond_f: A boolean-valued function
        -val_or_val_f: A default value to insert into all indices where cond_f is true, or a function to call on all such indices to determine their values.
        """
        #Convert constant values to constant functions for uniformity purposes
        if not callable(val_or_val_f):
            val_f = lambda x: val_or_val_f
        else:
            val_f = val_or_val_f
        #Prepend the pair (cond_f, val_f) into the default data
        #That way, new entries override old ones.
        self.default_data.insert(0, (cond_f, val_f))
    
    def __getitem__(self, key):
        """Override the indexing [] operator to allow accessing entries.
        
        If variable seq holds a Sequence:
        -seq[i] gets the value at index i
        -seq[:] gets everything from index 1 until it first encounters None (may fail to terminate)
        -seq[i:] gets everything from index i until it first encounters None (may fail to terminate)
        -seq[:j] gets everything from index 1 until index j-1
        -seq[i:j] gets everything from index i until index j-1
        """
        if isinstance(key, slice):
            #Deal with slices
            if key.start is None:
                start = 1
            else:
                start = key.start
            if key.step is None:
                step = 1
            else:
                step = key.step
            stop = key.stop
            ret = []
            i = start
            #Handle all cases of slices/termination
            while (stop is None and self[i] is not None) or\
            (step > 0 and stop is not None and i - start < stop - start) or\
            (step < 0 and stop is not None and start - i < start - stop):
                ret.append(self[i])
                i += step
            return ret
        elif key in self.data:
            #The easy case! It's a specific value in the sequence.
            return self.data[key]
        else:
            #Look for it as a default value that was set somewhere.
            #If it's not found, the value is None.
            for default in self.default_data:
                try:
                    if default[0](key):
                        return default[1](key)
                except TypeError:
                    #Tried to do something like compare a symbol to a number
                    pass
            return None
    
    def __str__(self):
        """Get a string representation of the sequence (may fail to terminate)"""
        return str(self[:])
    
    def __repr__(self):
        """Get another string representation of the sequence (may fail to terminate)"""
        return repr(self[:])

#Recurrence class
#Container for symbolic expressions and symbols
class Recurrence:
    """Recurrence class.
    
    -Constructor takes a symbolic expression, along with two symbols: rec_sym is the symbol for the recurrence (Q), and var_sym is the symbol for the variable (n)
    -This is a "container class." Access its members directly. If rec is a recurrence, rec.expr is the symbolic expression, rec.rec_sym is the recurrence symbol, and rec.var_sym is the variable symbol.
    """
    def __init__(self, expr, rec_sym, var_sym):
        self.expr = expr
        self.rec_sym = rec_sym
        self.var_sym = var_sym

    def __str__(self):
        return str(self.expr)
    
    def __repr__(self):
        return repr(self.expr)

#Generate terms of a sequence
def seq_terms(ic, rec, start, stop, mutate = False):
    """Generate some terms of a sequence defined by a (nested) recurrence.
    
    Arguments:
    -ic: A Sequence object representing the initial conditions.
    -rec: A Recurrence object representing the recurrence relation.
    -start: The index to start computing terms from.
    -stop: One greater than the last index to compute a term at.
    -mutate: If True, ic will be modified to include all of the new terms (default False).
    Output:
    -A Sequence object containing the initial conditions along with the computed terms. It will not compute any terms besides these.
    """
    if not mutate:
        #Copy the initial condition Sequence to avoid mutating it
        ic = Sequence(ic)
    #This loop looks a little weird so it can accommodate symbolic arguments
    #It could otherwise just be: for n in range(start, stop)
    for nn in range(stop - start):
        n = nn + start
        if ic[n] is None:
            #This is a new terms we need to compute
            #Do the substitution
            expr = rec.expr.subs(rec.var_sym, n)
            #Reduce the tree
            def tree_reduce(expr):
                #Get the function at the root of the current subtree.
                fun = expr.func
                if fun.is_Atom:
                    #We're at a leaf of the tree.
                    return expr
                else:
                    #We're not at a leaf of the tree.
                    #Time to evaluate the arguments.
                    args = []
                    for i in range(len(expr.args)):
                        args.append(tree_reduce(expr.args[i]))
                        if args[-1] is None:
                            #Stop as soon as we get a None argument
                            return None
                    #All arguments now evaluated.
                    #Let's check if it's our recurrence function or a built-in function
                    if str(fun) == str(rec.rec_sym):
                        #Our recurrence. Look up the value.
                        return ic[args[0]]
                    else:
                        #Built-in function. Call it.
                        return fun(*args)
            #Actually do the reduction, now that we have the routine for reducing the tree
            ic[n] = tree_reduce(expr)
    #Return the Sequence
    return ic