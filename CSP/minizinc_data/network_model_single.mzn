set of int: adj_x; 
set of int: adj_y; 
set of int: QoS; %bitrate, latency 
set of int: dim_server_res; 
set of int: num_servers; 

array[adj_x, adj_y] of int: target; 
array[num_servers, dim_server_res] of int: server_resources; 

array[QoS] of float: QoS_SE; 
set of int: num_options_SE;
set of int: SC_SE_br_factor; 
array[num_options_SE, adj_x, adj_y] of int: SC_SE_br; 
array[num_options_SE] of int: SC_SE_lat;
array[num_options_SE, num_servers, dim_server_res] of int: SC_SE_serv; 

array[QoS] of float: QoS_VPP;
set of int: num_options_VPP;
set of int: SC_VPP_br_factor;
array[num_options_VPP, adj_x, adj_y] of int: SC_VPP_br;
array[num_options_VPP] of int: SC_VPP_lat;
array[num_options_VPP, num_servers, dim_server_res] of int: SC_VPP_serv;

var num_options_SE: x_se_S1_B;
var num_options_VPP: x_VPP_S1_C;
var SC_SE_br_factor: x_se_br_factor; 
var SC_VPP_br_factor: x_VPP_br_factor;
constraint (SC_SE_lat[x_se_S1_B] <= QoS_SE[2]);
constraint (SC_VPP_lat[x_VPP_S1_C] <= QoS_VPP[2]);
constraint (x_se_br_factor >= QoS_SE[1]);
constraint (x_VPP_br_factor >= QoS_VPP[1]);

constraint forall(i in adj_x, j in adj_y)(SC_SE_br[x_se_S1_B, i, j] * x_se_br_factor  + SC_VPP_br[x_VPP_S1_C, i, j] * x_VPP_br_factor  <= target[i, j]);
constraint forall(k in num_servers, j in dim_server_res)(SC_SE_serv[x_se_S1_B, k, j] + SC_VPP_serv[x_VPP_S1_C, k, j] <= server_resources[k, j]);

solve satisfy;