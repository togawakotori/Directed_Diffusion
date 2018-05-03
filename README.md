# Directed Diffusion

To minimize the energy consumption in Wireless Sensor Network (WSN), routing protocols are proposed to decrease the communication cost. In [1], a scheme including routing protocol and data aggregation is proposed. In this project, we plan to realize and improve the routing protocol by using Raspberry Pis and testify its effectiveness. 

# Introduction to Directed Diffusion

In [1], the authors propose a data dissemination paradigm, Directed Diffusion.
The queries from sink are disseminated by broadcasting or geographic routing.
The sensing data are returned along reverse path. The relay nodes would
aggregate the sensing data from different nodes.
Some significant features are implemented in the paradigm: Loops in the
network are removed in the routing protocol; To promise the robustness of
network, the network will adapt to a changed topology; The cases of multisources
or multi-sinks are also considered.

# Plan

Our plan can be divided into several phases (Estimated duration of each phase
is attached in the parentheses):

- We should first read the paper carefully. (2 days)

- Then, we should realize the basic function, the routing protocol, by using
Raspberry Pis. (3 days)

- Next, data aggregation should be implemented. The comparison of energy
consumption between two versions should be done. (7 days)

- Finally, we should make the protocol robust against to the changing topology.
(7 days)

- If possible, we can try to improve the protocol. (3 days)

# References

[1] C. Intanagonwiwat, R. Govindan, D. Estrin, J. S. Heidemann, and F. Silva,
“Directed diffusion for wireless sensor networking,” IEEE/ACM Trans.
Netw., vol. 11, no. 1, pp. 2–16, 2003.
