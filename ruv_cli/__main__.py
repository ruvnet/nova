from ruv_cli.cli import main

if __name__ == "__main__":
    main()
else:
    # When imported as a module, provide the main function
    __all__ = ['main']