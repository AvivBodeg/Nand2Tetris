import sys, os
from CompilationEngine import CompilationEngine


def main():
    if len(sys.argv) != 2:
        print("Usage: JackAnalyzer  <path/to/dir | file.jack>")
        exit(1)

    userInput = sys.argv[1]
    # Single file:
    if os.path.isfile(userInput) and userInput.endswith('.jack'):

        output = os.path.join(userInput[:-4] + "xml")
        if os.path.exists(output):
            os.remove(output)
        compiler = CompilationEngine(userInput, output)
        compiler.compileClass()
        print("Done compiling")
        exit(0)

    # Dir
    if os.path.isdir(userInput):
        path = userInput.rstrip('/').rstrip('\\')
        for file in os.listdir(userInput):
            if file.endswith('.jack'):
                print(f"Processing {file}")
                filePath = os.path.join(path, file)
                output = os.path.join(path, file[:-4] + "xml")
                if os.path.exists(output):
                    os.remove(output)
                compiler = CompilationEngine(filePath, output)
                compiler.compileClass()
        print("Done compiling")
        exit(0)

    else:
        print("Expected <path/to/dir | file.jack>; Gotten " + userInput)
        exit(2)


if __name__ == "__main__":
    main()
