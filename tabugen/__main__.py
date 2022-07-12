"""
The main entry point. Invoke as `tabugen' or `python -m tabugen'.
"""


def main():
    try:
        from tabugen.cli import main
        main()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()
