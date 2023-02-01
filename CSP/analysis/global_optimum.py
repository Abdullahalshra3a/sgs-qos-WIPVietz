from minizinc import Instance, Model, Solver
import numpy as np
# # Load n-Queens model from file
# nqueens = Model("aust.mzn")
# # Find the MiniZinc solver configuration for Gecode
# gecode = Solver.lookup("gecode")
# # Create an Instance of the n-Queens model for Gecode
# instance = Instance(gecode, nqueens)
# # Assign 4 to n
# instance["nc"] = 3
# result = instance.solve() # instance.minimize
# # Output the array q
# print(result)

gecode = Solver.lookup("gecode")

model = Model("optimize_schedules_model.mzn")
instance = Instance(gecode, model)

#instance["target"] = [100, 100]
instance["A"] = range(0, 3)
instance["B"] = range(0, 1)

result = instance.solve()
print(result)





#instance["A"] = range(3, 8)  # MiniZinc: 3..8
#print(np.array(range(3, 8)))
#B={5, 4, 3, 2, 1}
#instance["B"] = B # MiniZinc: {4, 3, 2, 1, 0}
#print(B)
#result = instance.solve()
#print(np.array(result["X"]))  # range(0, 5)
#assert isinstance(result["X"], range)
#print(result["Y"])  # {0, 2, 4}
#assert isinstance(result["Y"], set)