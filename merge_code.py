import os


def merge_python_files(source_dir, output_file):
    # Collect all Python files in the source directory
    python_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    with open(output_file, "w") as outfile:
        outfile.write("# Merged Python Source Code\n\n")

        for py_file in python_files:
            with open(py_file, "r") as infile:
                outfile.write(f"# File: {py_file}\n")
                content = infile.read()

                # Remove the `if __name__ == "__main__":` block
                content = "\n".join(
                    line for line in content.splitlines()
                    if not line.strip().startswith("if __name__")
                )
                outfile.write(content + "\n\n")
        print(f"Merged {len(python_files)} files into {output_file}")


# Example usage
source_directory = "src/"  # Replace with your project's root directory
output_file = "merged_project.py"
merge_python_files(source_directory, output_file)
