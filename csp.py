"""CSP (Constraint Satisfaction Problems) problems and solvers. (Chapter 6)."""

# CLASS FROM https://github.com/aimacode/aima-python/ slightly modified for performance (see tag @modified)
# the proof about performance can be found in the files original_results.txt and modified_results.txt
# @modified: removed unused imports


class CSP:
    """This class describes finite-domain Constraint Satisfaction Problems.
    A CSP is specified by the following inputs:
        variables   A list of variables; each is atomic (e.g. int or string).
        domains     A dict of {var:[possible_value, ...]} entries.
        neighbors   A dict of {var:[var,...]} that for each variable lists
                    the other variables that participate in constraints.
        constraints A function f(A, a, B, b) that returns true if neighbors
                    A, B satisfy the constraint when they have values A=a, B=b

    In the textbook and in most mathematical definitions, the
    constraints are specified as explicit pairs of allowable values,
    but the formulation here is easier to express and more compact for
    most cases. (For example, the n-Queens problem can be represented
    in O(n) space using this notation, instead of O(N^4) for the
    explicit representation.) In terms of describing the CSP as a
    problem, that's all there is.

    However, the class also supports data structures and methods that help you
    solve CSPs by calling a search function on the CSP. Methods and slots are
    as follows, where the argument 'a' represents an assignment, which is a
    dict of {var:val} entries:
        assign(var, val, a)     Assign a[var] = val; do other bookkeeping
        unassign(var, a)        Do del a[var], plus other bookkeeping
        nconflicts(var, val, a) Return the number of other variables that
                                conflict with var=val
        curr_domains[var]       Slot: remaining consistent values for var
                                Used by constraint propagation routines.
    The following methods are used only by graph_search and tree_search:
        actions(state)          Return a list of actions
        result(state, action)   Return a successor of state
        goal_test(state)        Return true if all constraints satisfied
    The following are just for debugging purposes:
        nassigns                Slot: tracks the number of assignments made
        display(a)              Print a human-readable representation
    """

# added a variable to save the number of backtracks
# in my opinion it is better to show the backtracks instead of the assignments
    def __init__(self, variables, domains, neighbors, constraints):
        """Construct a CSP problem. If variables is empty, it becomes domains.keys()."""
        variables = variables or list(domains.keys())
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints
        self.initial = ()
        self.curr_domains = None
        self.nassigns = 0
        self.n_bt = 0

    def reduce_domains(self):
        """Perform initial domain reduction based on unary constraints."""
        for var in self.variables:
            unary_constraints = [val for val in self.domains[var] if self.constraints(var, val, var, val)]
            self.domains[var] = unary_constraints

    def preprocess(self):
        """Perform initial domain reduction before applying AC3."""
        self.reduce_domains()

    def assign(self, var, val, assignment):
        """Add {var: val} to assignment; Discard the old value if any."""
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        """Remove {var: val} from assignment.
        DO NOT call this if you are changing a variable to a new value;
        just call assign for that."""
        if var in assignment:
            del assignment[var]

# @Modified: the original used a recursive function, in my opinion this one looks better
#            and is easier to understand

    def nconflicts(self, var, val, assignment):
        """Return the number of conflicts var=val has with other variables."""
        count = 0
        for var2 in self.neighbors.get(var):
            val2 = None
            if assignment.__contains__(var2):
                val2 = assignment[var2]
            if val2 is not None and self.constraints(var, val, var2, val2) is False:
                count += 1
        return count

    def display(self, assignment):
        """Show a human-readable representation of the CSP."""
        # Subclasses can print in a prettier way, or display with a GUI
        print('CSP:', self, 'with assignment:', assignment)

    def goal_test(self, state):
        """The goal is to assign all variables, with all constraints satisfied."""
        assignment = dict(state)
        return (len(assignment) == len(self.variables)
                and all(self.nconflicts(variables, assignment[variables], assignment) == 0
                        for variables in self.variables))

    # These are for constraint propagation

    def support_pruning(self):
        """Make sure we can prune values from domains. (We want to pay
        for this only if we use it.)"""
        if self.curr_domains is None:
            self.curr_domains = {v: list(self.domains[v]) for v in self.variables}

    def suppose(self, var, value):
        """Start accumulating inferences from assuming var=value."""
        self.support_pruning()
        removals = [(var, a) for a in self.curr_domains[var] if a != value]
        self.curr_domains[var] = [value]
        return removals

    def prune(self, var, value, removals):
        """Rule out var=value."""
        self.curr_domains[var].remove(value)
        if removals is not None:
            removals.append((var, value))

    def choices(self, var):
        """Return all values for var that aren't currently ruled out."""
        return (self.curr_domains or self.domains)[var]

    def restore(self, removals):
        """Undo a supposition and all inferences from it."""
        for B, b in removals:
            self.curr_domains[B].append(b)


# ______________a________________________________________________________________
# Constraint Propagation with AC-3

def AC3(csp, queue=None, removals=None, display_tree=True):
    """[Figure 6.3]"""
    if queue is None:
        queue = [(Xi, Xk) for Xi in csp.variables for Xk in csp.neighbors[Xi]]
    csp.support_pruning()

    ac3_tree = {}  # to store information about removed values and added arcs in the AC3 tree

    def add_to_tree(Xi, Xj, removed_values, added_arcs):
        if display_tree:
            ac3_tree[(Xi, Xj)] = {'removed_values': removed_values, 'added_arcs': added_arcs}

    while queue:
        (Xi, Xj) = queue.pop()

        if revise(csp, Xi, Xj, removals):
            removed_values = set(csp.domains[Xi]) - set(csp.curr_domains[Xi])
            added_arcs = []
            if not csp.curr_domains[Xi]:
                return False
            for Xk in csp.neighbors[Xi]:
                if Xk != Xi:
                    queue.append((Xk, Xi))
                    added_arcs.append(((Xk, Xi)))
            add_to_tree(Xi, Xj, removed_values, added_arcs)
            #print(queue)

    if display_tree:
        print("============================================================\n")
        print_ac3_tree(ac3_tree)

    return True

def print_ac3_tree(tree):
    """Print a human-readable representation of the AC3 tree."""
    print("AC3 Tree:")
    for (Xi, Xj), info in tree.items():
        removed_values = info['removed_values']
        added_arcs = info['added_arcs']
        print(f"{Xi} -> {Xj}: Removed {removed_values}, Queue {added_arcs}")
        print("============================================================\n")




def revise(csp, Xi, Xj, removals):
    """Return true if we remove a value."""
    revised = False
    for x in csp.curr_domains[Xi][:]:
        # If Xi=x conflicts with Xj=y for every possible y, eliminate Xi=x
        if all(not csp.constraints(Xi, x, Xj, y) for y in csp.curr_domains[Xj]):
            csp.prune(Xi, x, removals)
            revised = True
    return revised

# ______________________________________________________________________________
# CSP Backtracking Search

# Variable ordering


# @Modified: we just want the first one that haven't been assigned so returning fast is good
def first_unassigned_variable(assignment, csp):
    """The default variable order."""
    for var in csp.variables:
        if var not in assignment:
            return var


# @Modified: the original used a function from util files and was harder to understand,
#            it also apparently used 2 for loops: one to find the minimum and
#            other one to create a list (and a lambda function)
def mrv(assignment, csp):
    """Minimum-remaining-values heuristic."""
    vars_to_check = []
    size = []
    for v in csp.variables:
        if v not in assignment.keys():
            vars_to_check.append(v)
            size.append(num_legal_values(csp, v, assignment))
    return vars_to_check[size.index(min(size))]


# @Modified: the original used a function count and a list, in my opinion it is faster to
#            just count with a loop 'for' without calling external functions
def num_legal_values(csp, var, assignment):
    if csp.curr_domains:
        return len(csp.curr_domains[var])
    else:
        count = 0
        for val in csp.domains[var]:
            if csp.nconflicts(var, val, assignment) == 0:
                count += 1
        return count

# Value ordering


def unordered_domain_values(var, assignment, csp):
    """The default value order."""
    return csp.choices(var)


def lcv(var, assignment, csp):
    """Least-constraining-values heuristic."""
    return sorted(csp.choices(var),
                  key=lambda val: csp.nconflicts(var, val, assignment))


# Inference


def no_inference(csp, var, value, assignment, removals):
    return True


def forward_checking(csp, var, value, assignment, removals):
    """Prune neighbor values inconsistent with var=value."""
    for B in csp.neighbors[var]:
        if B not in assignment:
            for b in csp.curr_domains[B][:]:
                if not csp.constraints(var, value, B, b):
                    csp.prune(B, b, removals)
            if not csp.curr_domains[B]:
                return False
    return True


def mac(csp, var, value, assignment, removals):
    """Maintain arc consistency."""
    return AC3(csp, [(X, var) for X in csp.neighbors[var]], removals, True)

# The search, proper

# @Modified: we should notice that with MRV it works good since the partial initial state
#            leaves some variables with unitary domain so we will start to assign these variables.
#            Added csp.n_bt+=1


def backtracking_search(csp,
                        select_unassigned_variable,
                        order_domain_values,
                        inference):
    """[Figure 6.5]"""
    def backtrack(assignment):
        if len(assignment) == len(csp.variables):
            return assignment
        var = select_unassigned_variable(assignment, csp)
        for value in order_domain_values(var, assignment, csp):
            if 0 == csp.nconflicts(var, value, assignment):
                csp.assign(var, value, assignment)
                removals = csp.suppose(var, value)
                if inference(csp, var, value, assignment, removals):
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                    else:
                        csp.n_bt += 1
                csp.restore(removals)
        csp.unassign(var, assignment)
        return None

    result = backtrack({})
    assert result is None or csp.goal_test(result)
    return result


def different_values_constraint(A, a, B, b):
    """A constraint saying two neighboring variables must differ in value."""
    return a != b

