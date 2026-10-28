"""CLI entry point that preserves a single ORM module identity in subprocesses."""
from .inference_queue import main

if __name__ == "__main__":
    main()
