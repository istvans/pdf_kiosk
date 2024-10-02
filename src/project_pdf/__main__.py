"""The main entry point of this script."""
import sys

from project_pdf import project


def main() -> int:
    project()
    return 0


if __name__ == "__main__":
    sys.exit(main())
