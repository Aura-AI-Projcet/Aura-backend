"""
Test Runner Script

Provides a convenient way to run tests with proper environment setup.
"""
import os
import subprocess
import sys
from pathlib import Path


def setup_test_environment() -> None:
    """Setup test environment variables"""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["TESTING"] = "true"


def run_tests(test_path: str = "", verbose: bool = False) -> int:
    """Run pytest with proper configuration"""
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)

    # Setup test environment
    setup_test_environment()

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")

    # Add coverage reporting
    cmd.extend(
        [
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html",
        ]
    )

    # Run tests
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run tests")
    parser.add_argument("path", nargs="?", default="", help="Specific test path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()
    exit_code = run_tests(args.path, args.verbose)
    sys.exit(exit_code)
