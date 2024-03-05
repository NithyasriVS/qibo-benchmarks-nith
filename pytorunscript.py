import plots.libraries
import subprocess

# List of libraries
libraries = ['qibo', 'qiskit']

# Loop through the libraries
for library in libraries:
    # Construct the command to run
    command = ['python', 'compare.py', '--precision', 'double', '--filename', 'file.dat', '--library', library]
    # Execute the command
    subprocess.run(command)

