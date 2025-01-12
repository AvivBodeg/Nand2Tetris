import sys, os
from CompilationEngine import CompilationEngine


def main():
    if len(sys.argv) != 2:
        print("Usage: JackAnalyzer  <path/to/dir | file.jack>")
        exit(1)

    user_input = sys.argv[1]
    # Single file:
    if os.path.isfile(user_input) and user_input.endswith('.jack'):
        output = os.path.join(user_input[:-4] + "vm")
        if os.path.exists(output):
            os.remove(output)
        compiler = CompilationEngine(user_input, output)
        compiler.compile_class()
        print("Done compiling")
        exit(0)

    # Dir
    if os.path.isdir(user_input):
        path = user_input.rstrip('/').rstrip('\\')
        for file in os.listdir(user_input):
            if file.endswith('.jack'):
                print(f"Processing {file}")
                file_path = os.path.join(path, file)
                output = os.path.join(path, file[:-4] + "vm")
                if os.path.exists(output):
                    os.remove(output)
                compiler = CompilationEngine(file_path, output)
                compiler.compile_class()
        print("Done compiling")
        exit(0)

    else:
        print("Expected <path/to/dir | file.jack>; Gotten " + user_input)
        exit(2)


if __name__ == "__main__":
    main()
