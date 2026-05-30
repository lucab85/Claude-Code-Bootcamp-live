#!/usr/bin/env python3
"""Greet command-line tool."""

import argparse
import sys


def hello(name: str, upper: bool) -> None:
    greeting = f"Hello, {name}!"
    if upper:
        greeting = greeting.upper()
    print(greeting)


def main() -> int:
    parser = argparse.ArgumentParser(prog="greet", description="Greet tool")
    parser.add_argument("--upper", action="store_true", help="Uppercase the greeting")
    subparsers = parser.add_subparsers(dest="command", required=True)

    hello_parser = subparsers.add_parser("hello", help="Greet someone")
    hello_parser.add_argument("name", help="Name to greet")

    args = parser.parse_args()

    if args.command == "hello":
        hello(args.name, args.upper)

    return 0


if __name__ == "__main__":
    sys.exit(main())
