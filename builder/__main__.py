from builder.bootstrap.bootstrap import bootstrap
from builder.cli.app import app

def main() -> None:
    bootstrap()
    app()

if __name__ == "__main__":
    main()
