Test cases:
    1. python src/nario.py
        - should enter repl mode
    2. python src/nario.py test/lab1/test_program.nario
        - should print all token types, tokens, and values
    3. python src/nario.py 123.nario 456.nario
        - should give you an error and tell you how to run correctly
    4. python src/nario.py non_existent_file.nario
        - should give a no such file or directory error