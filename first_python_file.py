import os
import sys
import pathlib

# Get the repository root directory
repository_root = pathlib.Path(__file__).parent

# Get the list of Python files in the repository
python_files = [file for file in repository_root.rglob("*.py")]

# Get the first Python file in the repository
first_python_file = python_files[0]

# Print the name of the first Python file
print(f"First Python file: {first_python_file.name}")