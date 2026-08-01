import os
import sys
import pathlib

# Get the repository root directory
repository_root = pathlib.Path(__file__).parent

# Get the list of Python files in the repository
python_files = [file for file in repository_root.rglob("*.py")]

# Get the first Python file in the repository
first_python_file = python_files[0]

# Read the first five lines of the first Python file
with open(first_python_file, "r") as file:
    first_five_lines = [line.strip() for line in file.readlines()[:5]]

# Print the name of the first Python file and its first five lines
print(f"First Python file: {first_python_file.name}")
print(first_five_lines)