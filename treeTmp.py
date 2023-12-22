class Constraint:
    def __init__(self, var1, var2):
        self.var1 = var1
        self.var2 = var2

    def is_satisfied(self, assignment):
        # Implement your constraint satisfaction logic here
        # For simplicity, let's assume variables are integers
        return abs(assignment[self.var1] - assignment[self.var2]) > 1

class ArcConsistencyTree:
    def __init__(self, variables, constraints):
        self.variables = variables
        self.constraints = constraints
        self.arc_tree = {}

    def build_tree(self):
        for var1 in self.variables:
            for var2 in self.variables:
                if var1 != var2:
                    constraint = Constraint(var1, var2)
                    if constraint.is_satisfied({var1: 0, var2: 0}):
                        if var1 not in self.arc_tree:
                            self.arc_tree[var1] = []
                        self.arc_tree[var1].append(var2)

    def print_tree(self):
        for var, neighbors in self.arc_tree.items():
            print(f"{var} -> {neighbors}")

# Example usage:
variables = [1, 2, 3, 4]
constraints = [Constraint(1, 2), Constraint(1, 3), Constraint(2, 3), Constraint(3, 4)]
arc_tree = ArcConsistencyTree(variables, constraints)
arc_tree.build_tree()
arc_tree.print_tree()
