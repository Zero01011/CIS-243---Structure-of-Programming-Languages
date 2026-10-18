## --- start AI code ----

import subprocess
import sys
from pathlib import Path

# Settings: adjust these to match the project layout.
TEST_ROOT = Path(__file__).parent                          # folder containing this script
INTERPRETER = TEST_ROOT.parent.parent / "src" / "nario.py"  # program that runs each test
TEST_FOLDERS = ["valid", "errors"]                         # subfolders to run, in order
FILE_PATTERN = "*.nario"                                   # which files count as tests

for folder in TEST_FOLDERS:
    # Sort so the tests run in a predictable order.
    for test_file in sorted((TEST_ROOT / folder).glob(FILE_PATTERN)):
        # Flush the header so it prints before the program's output.
        print(f"\n=== {folder}/{test_file.name} ===", flush=True)

        # Run with the current Python executable and merge stderr into stdout
        # so errors appear directly under their header.
        subprocess.run([sys.executable, str(INTERPRETER), str(test_file)], stderr=subprocess.STDOUT)

## --- end AI code ----