"""Command-line interface for OTPKit."""

from __future__ import annotations

import argparse
import sys

from . import OTP, generate_secret


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="otpkit", description="Generate and verify one-time passwords.")
    subparsers = parser.add_subparsers(dest="command")

    generate_parser = subparsers.add_parser("generate", help="Generate a new OTP.")
    generate_parser.add_argument("--length", type=int, default=6)

    verify_parser = subparsers.add_parser("verify", help="Verify an OTP value.")
    verify_parser.add_argument("code")

    subparsers.add_parser("secret", help="Generate a new secret.")
    subparsers.add_parser("version", help="Show package version.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        try:
            otp = OTP(length=args.length)
            code = otp.generate()
            print(f"OTP: {code}")
            return 0
        except Exception as exc:  # pragma: no cover - CLI safety
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    if args.command == "verify":
        otp = OTP()
        if otp.verify(args.code):
            print("Verified")
            return 0
        print("Invalid")
        return 1

    if args.command == "secret":
        print(generate_secret())
        return 0

    if args.command == "version":
        from . import __version__

        print(__version__)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
