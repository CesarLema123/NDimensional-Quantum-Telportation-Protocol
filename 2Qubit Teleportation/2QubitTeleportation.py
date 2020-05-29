"""
NYU Tandon PH-GY 5553 Course Project Code
written by Cesar Lema (cl4393)
"""
import numpy as np
import matplotlib.pyplot as plt

from qiskit import *
from qiskit.visualization import plot_histogram
from qiskit.tools.monitor import job_monitor
import time

"""
This file implements teleportation of an arbitrary two qubit state
"""

def maxSuperposition(n,provider):
    qRegister = QuantumRegister(n,name = "bit%i_maxSuper_q"%(n))
    circuit = QuantumCircuit(qRegister)   # Hold n qubits and classical bits
    
    for i in range(n):
        circuit.h([i])
    print("Max Superposition circuit")
    print(circuit.draw(output="text"))
    return qRegister, circuit
    
def singleState(n, m, provider):
    qRegister = QuantumRegister(n,name = "bit%i_single%iState_q"%(n,m))
    circuit = QuantumCircuit(qRegister)
    binary = format(m,"b")
    for i in range(n - len(binary) ):
        binary = "0"+binary
    
    for qindex in range(n):
        if int(binary[qindex]):
            circuit.x([qindex])
    print("Single state circuit")
    print(circuit.draw(output="text"))
    return qRegister, circuit
    
def BellsState(ind = "0"):
    qRegister = QuantumRegister(2,name = "bellsState%s_q"%(ind))
    circuit = QuantumCircuit(qRegister)
    circuit.h([0])
    circuit.cx([0],[1])
    print("Bells state circuit %s"%(ind))
    print(circuit.draw(output="text"))
    return qRegister, circuit

def executeAndPlot(cir, backend):
    print(cir.draw(output="text"))
    job = execute(cir, backend = backend,shots = 1024)
    job_monitor(job)
    results = job.result()
    plot_histogram(results.get_counts(cir))                # histogram of results from simulation
    plt.show()
    plt.close()

"""
def intermediateTeleStep(initialQBits = None):
    return
"""
#------------------------------------------------------------------
#                        Initializing System
#------------------------------------------------------------------
qr = QuantumRegister(3)                               #
cr = ClassicalRegister(2)

circuit = QuantumCircuit(qr,cr)

provider = IBMQ.load_account()
leastBusyBackend = qiskit.providers.ibmq.least_busy(provider.backends() ).name()
#backend = provider.get_backend(leastBusyBackend)
backend = Aer.get_backend("qasm_simulator")

#------------------------------------------------------------------
#                         Building Circuit
#------------------------------------------------------------------

initStateQbits, initStateCircuit = maxSuperposition(2,provider)
#initStateQbits, initStateCircuit = singleState(2,3,provider)
bStateQbits1, bState1Circuit = BellsState(ind = "1")
bStateQbits2, bState2Circuit = BellsState(ind = "2")


# Initialization
cBit1 = ClassicalRegister(1,name = "c1_iter1")
cBit2 = ClassicalRegister(1,name = "c2_iter1")
cBit3 = ClassicalRegister(1,name = "c1_iter2")
cBit4 = ClassicalRegister(1,name = "c2_iter2")
resultCB = ClassicalRegister(2, name = "results")

currCir = initStateCircuit
currCir = initStateCircuit.combine(bState1Circuit)
currCir = currCir.combine(bState2Circuit)
currCir.add_register(cBit1,cBit2,cBit3,cBit4)
currCir.add_register(resultCB)

# First Iteration
currCir.barrier()
currCir.cx([0],[2])
currCir.h([0])

currCir.measure([0],[1])
currCir.measure([2],[0])

currCir.barrier()
currCir.z([3]).c_if(cBit2, 1)
currCir.x([3]).c_if(cBit1, 1)
#currCir.measure([1],[5])               # testing intermediate state after first iter
#currCir.measure([3],[4])               # testing intermediate state after first iter
#executeAndPlot(currCir, backend)

# Second Iteration
currCir.barrier()
currCir.cx([1],[4])
currCir.h([1])

currCir.measure([1],[3])
currCir.measure([4],[2])

currCir.barrier()
currCir.z([5]).c_if(cBit4, 1)
currCir.x([5]).c_if(cBit3, 1)

# Measure teleported state
currCir.barrier()
currCir.measure([3],[5])            # Final state of teleported bits
currCir.measure([5],[4])            # Final states of teleported bits

#------------------------------------------------------------------
#                       Visualization/Ouput
#------------------------------------------------------------------
executeAndPlot(currCir, backend)            # Custom function to display circuit, execute job, print results

