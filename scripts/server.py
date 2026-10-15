"""Run the shared Snowballer browser: python server.py [--port 8000]."""
import sys

sys.dont_write_bytecode = True

from snowballer import main


if __name__ == "__main__":
    sys.argv.insert(1, "serve")
    main()
