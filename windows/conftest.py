import sys
import os

# Ensure the windows/ directory is on sys.path so `import input_handler` works
# regardless of which directory pytest is invoked from.
sys.path.insert(0, os.path.dirname(__file__))
