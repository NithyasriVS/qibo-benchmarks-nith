import qibo
from qibo import Circuit, gates
import qibotn

computation_settings = {
    "MPI_enabled": False,
    "MPS_enabled": {
        "qr_method": False,
        "svd_method": {
            "partition": "UV",
            "abs_cutoff": 1e-12,
        },
    },
    "NCCL_enabled": False,
    "expectation_enabled": False,
}

qibo.set_backend(
    backend="qibotn", platform="quimb", runcard=computation_settings
)  # cuQuantum
# qibo.set_backend(backend="qibotn", platform="QuimbBackend", runcard=computation_settings) #quimb


# Construct the circuit
c = Circuit(2)
# Add some gates
c.add(gates.H(0))
c.add(gates.H(1))

# Execute the circuit and obtain the final state
result = c()

print(result.state())