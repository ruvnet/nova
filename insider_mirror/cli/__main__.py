"""Entry point for the CLI when run as a module."""

from .app import InsiderMirrorCLI

def main():
    """Main entry point"""
    cli = InsiderMirrorCLI()
    cli.execute()

if __name__ == "__main__":
    main()