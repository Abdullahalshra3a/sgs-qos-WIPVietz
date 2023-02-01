set of int: adj_x;
set of int: adj_y;
set of int: QoS; %bitrate, latency
set of int: dim_server_res;
set of int: num_servers;

array[QoS] of float: QoS_SE;
array[QoS] of float: QoS_VPP;
array[QoS] of float: QoS_AR;
array[QoS] of float: QoS_LM;
array[QoS] of float: QoS_CVC;

set of int: num_options_SE;
set of int: num_devices_SE;
array[num_options_SE, adj_x, adj_y] of float: SC_SE_br;
array[num_options_SE, num_devices_SE] of float: SC_SE_lat;
array[num_options_SE, num_servers, dim_server_res] of int: SC_SE_serv;

set of int: num_options_AR;
set of int: num_devices_AR;
array[num_options_AR, adj_x, adj_y] of float: SC_AR_br;
array[num_options_AR, num_devices_AR] of float: SC_AR_lat;
array[num_options_AR, num_servers, dim_server_res]of int: SC_AR_serv;

set of int: num_options_VPP;
set of int: num_devices_VPP;
array[num_options_VPP, adj_x, adj_y] of float: SC_VPP_br;
array[num_options_VPP, num_devices_VPP] of float: SC_VPP_lat;
array[num_options_VPP, num_servers, dim_server_res] of int: SC_VPP_serv;

set of int: num_options_LM;
set of int: num_devices_LM;
array[num_options_LM, adj_x, adj_y] of float: SC_LM_br;
array[num_options_LM, num_devices_LM] of float: SC_LM_lat;
array[num_options_LM, num_servers, dim_server_res] of int: SC_LM_serv;

set of int: num_options_CVC;
set of int: num_devices_CVC;
array[num_options_CVC, adj_x, adj_y] of float: SC_CVC_br;
array[num_options_CVC, num_devices_LM] of float: SC_CVC_lat;
array[num_options_CVC, num_servers, dim_server_res] of int: SC_CVC_serv;

array[adj_x, adj_y] of float: target;
array[num_servers, dim_server_res] of int: server_resources;

var num_options_SE: x_se;
var num_options_VPP: x_vpp;
var num_options_AR: x_ar;
var num_options_LM: x_lm;
var num_options_CVC: x_cvc;

constraint forall(i in adj_x, j in adj_y)(SC_SE_br[x_se, i, j]  + SC_VPP_br[x_vpp, i, j] + SC_AR_br[x_ar, i, j] + SC_LM_br[x_lm, i, j] + SC_CVC_br[x_cvc, i, j] <= target[i, j]);
constraint forall(i in num_devices_SE)(SC_SE_lat[x_se, i] <= QoS_SE[2]);
constraint forall(i in num_devices_VPP)(SC_VPP_lat[x_vpp,i] <= QoS_VPP[2]);
constraint forall(i in num_devices_AR) (SC_AR_lat[x_ar, i] <= QoS_AR[2]);
constraint forall(i in num_devices_LM) (SC_LM_lat[x_lm, i] <= QoS_LM[2]);
constraint forall(i in num_devices_CVC) (SC_CVC_lat[x_cvc, i] <= QoS_CVC[2]);
constraint forall(k in num_servers, j in dim_server_res)(SC_VPP_serv[x_vpp, k, j] + SC_SE_serv[x_se, k , j] + SC_AR_serv[x_ar, k, j] + SC_LM_serv[x_lm, k, j] + SC_CVC_serv[x_cvc, k, j] <= server_resources[k, j]);


%var float: obj_lat = sum(j in num_devices_SE)(SC_SE_lat[x_se, j]) + sum(j in num_devices_VPP)(SC_VPP_lat[x_vpp,j]) + sum(j in num_devices_AR)(SC_AR_lat[x_ar,j]);
%var float: obj_br = sum(i in adj_x, j in adj_y)(target[i,j] - (SC_SE_br[x_se, i, j]  + SC_VPP_br[x_vpp, i, j] + SC_AR_br[x_ar, i, j]));
%var float: obj = 1/obj_lat + obj_br;
solve satisfy;
%solve minimize(obj_lat);

%output["QoS is \(QoS_SE[1])"];
%output ["the following indexes were chosen x_se = \(x_se), x_vpp = \(x_vpp),"];