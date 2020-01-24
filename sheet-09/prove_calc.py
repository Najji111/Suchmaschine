#!/usr/bin/python3

import numpy as np





print("A")
a = np.matrix('13 5 5 0 13; 9 15 15 0 9; 0 0 0 20 0')
print(a)
aat = a.dot(np.transpose(a))
print("A*A^T")
print(aat)

s, u = np.linalg.eig(aat)
print("\neigenvalues")
s[1] = 400
s[2] = 900
s = np.diag(s)
print(s)
print("eigenvectros")
print(u)
u = np.matrix('4 0 -3; -3 0 -4; 0 1 0')
print(u)

print("\nEigenvalue ", s[0])
print(aat.dot(u[:,0]))
print("Eigenvalue ", s[1])
print(aat.dot(u[:,1]))
print("Eigenvalue ", s[2])
print(aat.dot(u[:, 2]))

print("\ninverse eigenvalue mateix")
s_i = np.linalg.inv(s)
print(s_i)
print("transpose eigenvector mateix")
u_t = np.transpose(u)
print(u_t)
print("svd")
v = s_i.dot(u_t.dot(a))
print(v) 
print("svd test")
print(s.dot(v))
a_n = u.dot(s.dot(v))
a_n[0:2,:] /= 25
print(a_n)

