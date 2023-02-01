import os
import subprocess
path_to_mzn = "~/Programme/minibrass/smallexample_minisearch.mzn" #moving.mzn
path_to_dzn = "~/Programme/minibrass/moving.dzn"
# stream = os.popen('minizinc -a --solver Gecode ' + path_to_mzn + ' ' + path_to_dzn)
# output = stream.read()
# print(output)
#path_to_minibrass = "~/Programme/minibrass/minibrass"
path_to_minisearch = "~/Programme/minisearch/build/minisearch"

#path_to_mzn = "~/Programme/minibrass/smallexample_minisearch.mzn"

#sp = subprocess.Popen(["/bin/bash", "-i", "-c", "minizinc " + path_to_mzn + " " + path_to_dzn])
#sp.communicate()
#print(sp)
#compile minibrass

stream = os.popen(path_to_minisearch + " " + path_to_mzn)
output = stream.read()
print(output)