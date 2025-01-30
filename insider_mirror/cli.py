"""Command-line interface entry point."""

from .cli.app import InsiderMirrorCLI

def main():
    """Entry point for the CLI"""
    cli = InsiderMirrorCLI()
    cli.execute()

if __name__ == "__main__":
    main()