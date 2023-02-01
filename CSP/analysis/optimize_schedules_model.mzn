set of int: A;
set of int: B;

var A: varA;
var B: varB;

%constraint (A + B == 100);
%solve minimize forall (j in num_schedules)(4*flexibilities[j] > agent1 + agent2 + agent3)
solve minimize 150 - (varA + varB);


