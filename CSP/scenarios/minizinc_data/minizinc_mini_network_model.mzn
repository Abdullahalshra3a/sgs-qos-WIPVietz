set of int: adj_x;
set of int: adj_y;
set of int: QoS; %bitrate, latency
set of int: dim_server_res;
set of int: num_servers;

array[QoS] of float: QoS_SE;
array[QoS] of float: QoS_VPP;

set of int: num_options_SE;
set of int: num_devices_SE;
array[num_options_SE, adj_x, adj_y] of float: SC_SE_br;
array[num_options_SE, num_devices_SE] of float: SC_SE_lat;
array[num_options_SE, num_servers, dim_server_res] of int: SC_SE_serv;

set of int: num_options_VPP;
set of int: num_devices_VPP;
array[num_options_VPP, adj_x, adj_y] of float: SC_VPP_br;
array[num_options_VPP, num_devices_VPP] of float: SC_VPP_lat;
array[num_options_VPP, num_servers, dim_server_res] of int: SC_VPP_serv;

array[adj_x, adj_y] of float: target;
array[num_servers, dim_server_res] of int: server_resources;

var num_options_SE: x_se;
var num_options_VPP: x_vpp;

constraint forall(i in adj_x, j in adj_y)(SC_SE_br[x_se, i, j]  + SC_VPP_br[x_vpp, i, j] <= target[i, j]);
constraint forall(i in num_devices_SE)(SC_SE_lat[x_se, i] <= QoS_SE[2]);
constraint forall(i in num_devices_VPP)(SC_VPP_lat[x_vpp,i] <= QoS_VPP[2]);

constraint forall(k in num_servers, j in dim_server_res)(SC_VPP_serv[x_vpp, k, j] + SC_SE_serv[x_se, k , j] <= server_resources[k, j]);

solve satisfy;