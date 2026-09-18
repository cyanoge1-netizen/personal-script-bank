#!/usr/bin/env python3
"""
Fast C/C++ File Skeleton Generator (Cross-Platform)
Supports: Android (Termux), Linux, macOS, and Windows.
"""

import os
import argparse
import concurrent.futures
from pathlib import Path


def get_default_dir() -> Path:
    """Return platform-appropriate default directory."""
    if Path("/storage/emulated/0").exists():
        return Path("/storage/emulated/0/B")
    return Path.cwd() / "output"


def get_skeleton() -> str:
    """Returns standard ANSI C / C++ boilerplate."""
    return (
        "#include <stdio.h>\n\n"
        "int main(void) {\n"
        "    // Start your logic here\n"
        "    return 0;\n"
        "}\n"
    )


def write_file(task_tuple):
    """Write template content to a single file."""
    file_path, content = task_tuple
    file_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Fast C/C++ file skeleton generator with parallel processing.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("filename", help="Base name of the files (e.g. 'lab_task')")
    parser.add_argument("count", type=int, help="Number of files to create")
    parser.add_argument(
        "-d", "--dir",
        type=Path,
        default=get_default_dir(),
        help="Target directory path"
    )
    parser.add_argument(
        "-e", "--ext",
        default=".c",
        help="File extension (.c, .cxx, .cpp)"
    )

    args = parser.parse_args()

    target_dir = args.dir.expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    ext = args.ext if args.ext.startswith('.') else f".{args.ext}"
    skeleton = get_skeleton()
    tasks = [(target_dir / f"{args.filename}{i}{ext}", skeleton) for i in range(1, args.count + 1)]

    print(f"🚀 Generating {args.count} files in: {target_dir}")

    # Graceful fallback if tqdm is not installed
    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        has_tqdm = False

    with concurrent.futures.ProcessPoolExecutor() as executor:
        if has_tqdm:
            list(tqdm(executor.map(write_file, tasks), total=len(tasks), unit="file"))
        else:
            list(executor.map(write_file, tasks))

    print(f"✨ Successfully generated {args.count} skeleton files in {target_dir}!")


if __name__ == "__main__":
    main()
