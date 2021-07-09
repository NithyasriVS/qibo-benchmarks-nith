"""
Generic benchmark script that runs circuits defined in `benchmark_models.py`.

The type of the circuit is selected using the ``--type`` flag.
"""
import argparse
import os
import time
import json
import numpy as np
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3" # disable Tensorflow warnings


parser = argparse.ArgumentParser()
parser.add_argument("--nqubits", default=20, type=int)
parser.add_argument("--type", default="qft", type=str)
parser.add_argument("--backend", default="qibojit", type=str)
parser.add_argument("--precision", default="double", type=str)
parser.add_argument("--nreps", default=1, type=int)
parser.add_argument("--nshots", default=None, type=int)

parser.add_argument("--memory", default=None, type=int)
parser.add_argument("--threading", default=None, type=str)

parser.add_argument("--transfer", action="store_true")
parser.add_argument("--nlayers", default=None, type=int)
parser.add_argument("--gate-type", default=None, type=str)

parser.add_argument("--filename", default=None, type=str)

# params
_PARAM_NAMES = {"theta", "phi"}
parser.add_argument("--theta", default=None, type=float)
parser.add_argument("--phi", default=None, type=float)
args = vars(parser.parse_args())


threading = args.pop("threading")
if args.get("backend") == "qibojit" and threading is not None:
    select_numba_threading(threading)

memory = args.pop("memory")
if args.get("backend") in {"qibotf", "tensorflow"}:
    limit_gpu_memory(memory)

import qibo
import circuits


def main(nqubits, type, backend="custom", precision="double", threadsafe=False,
         nreps=1, nshots=None, transfer=False, nlayers=None,
         gate_type=None, params={}, filename=None):
    """Runs benchmarks for different circuit types.

    Args:
        nqubits (int): Number of qubits in the circuit.
        type (str): Type of Circuit to use.
            See ``benchmark_models.py`` for available types.
        nreps (int): Number of repetitions of circuit execution.
            Dry run is not included. Default is 1.
        nshots (int): Number of measurement shots.
            Logs the time required to sample frequencies (no samples).
            If ``None`` no measurements are performed.
        transfer (bool): If ``True`` it transfers the array from GPU to CPU.
            Makes execution and dry run times similar
            (otherwise execution is much faster).
        nlayers (int): Number of layers for supremacy-like or gate circuits.
            If a different circuit is used ``nlayers`` is ignored.
        gate_type (str): Type of gate for gate circuits.
            If a different circuit is used ``gate_type`` is ignored.
        params (dict): Gate parameter for gate circuits.
            If a non-parametrized circuit is used then ``params`` is ignored.
        filename (str): Name of file to write logs.
            If ``None`` logs will not be saved.
    """
    qibo.set_backend(backend)
    qibo.set_precision(precision)

    if filename is not None:
        if os.path.isfile(filename):
            with open(filename, "r") as file:
                logs = json.load(file)
            print("Extending existing logs from {}.".format(filename))
        else:
            print("Creating new logs in {}.".format(filename))
            logs = []
    else:
        logs = []

    # Create log dict
    logs.append({
        "nqubits": nqubits, "circuit_type": type, "threading": "",
        "backend": qibo.get_backend(), "precision": qibo.get_precision(),
        "nshots": nshots, "transfer": transfer
        })

    params = {k: v for k, v in params.items() if v is not None}
    kwargs = {"nqubits": nqubits, "circuit_type": type}
    if params: kwargs["params"] = params
    if nlayers is not None: kwargs["nlayers"] = nlayers
    if gate_type is not None: kwargs["gate_type"] = gate_type
    logs[-1].update(kwargs)

    start_time = time.time()
    circuit = qibo.models.Circuit(nqubits)
    circuit.add()
    if nshots is not None:
        # add measurement gates
        circuit.add(qibo.gates.M(*range(nqubits)))
    logs[-1]["creation_time"] = time.time() - start_time

    if compile:
        start_time = time.time()
        circuit.compile()
        # Try executing here so that compile time is not included
        # in the simulation time
        result = circuit(nshots=nshots)
        logs[-1]["compile_time"] = time.time() - start_time

    start_time = time.time()
    result = circuit(nshots=nshots)
    if transfer:
        result = result.numpy()
    logs[-1]["dry_run_time"] = time.time() - start_time

    simulation_time = []
    for _ in range(nreps):
        start_time = time.time()
        result = circuit(nshots=nshots)
        if transfer:
            result = result.numpy()
        simulation_time.append(time.time() - start_time)
    logs[-1]["dtype"] = str(result.dtype)
    logs[-1]["simulation_time"] = np.mean(simulation_time)
    logs[-1]["simulation_time_std"] = np.std(simulation_time)


    if nshots is not None:
        start_time = time.time()
        freqs = result.frequencies()
        logs[-1]["measurement_time"] = time.time() - start_time

    if logs[-1]["backend"] == "qibojit" and qibo.K.op.get_backend() == "numba":
        from numba import threading_layer
        logs[-1]["threading"] = threading_layer()

    print()
    for k, v in logs[-1].items():
        print("{}: {}".format(k, v))
    print()

    if filename is not None:
        with open(filename, "w") as file:
            json.dump(logs, file)


if __name__ == "__main__":
    args["params"] = {k: args.pop(k) for k in _PARAM_NAMES}
    main(**args)
