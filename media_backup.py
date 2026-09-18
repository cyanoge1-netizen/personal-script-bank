#!/usr/bin/env python3
"""
Media Backup & Archive Utility (Cross-Platform)
Supports: Android (Termux), Linux, macOS, and Windows.

Scans, archives, MD5 verifies, and optionally cleans media files with RAM-safe chunking
and 64-bit zip support.
"""

import os
import sys
import platform
import argparse
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

# --- Supported Extensions ---
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif',
    '.heic', '.heif', '.raw', '.dng', '.svg', '.ico', '.cr2', '.nef', '.arw'
}

VIDEO_EXTENSIONS = {
    '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm',
    '.m4v', '.3gp', '.mpeg', '.mpg', '.ts', '.vob', '.m2ts', '.mts'
}

AUDIO_EXTENSIONS = {
    '.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.opus', '.wma'
}


def is_android() -> bool:
    """Detect if running under an Android environment (e.g., Termux or proot)."""
    return (
        'ANDROID_ROOT' in os.environ
        or 'ANDROID_DATA' in os.environ
        or 'com.termux' in os.environ.get('PREFIX', '')
        or Path('/storage/emulated/0').exists()
    )


def detect_system_defaults():
    """Detect OS-specific default directories and exclude patterns."""
    current_os = platform.system()
    home = Path.home()

    # Base common exclusions across all operating systems
    banned_dirs = {'.git', '.svn', '.hg', '.cache', 'node_modules', '__pycache__', '.recycle'}
    exclude_paths = set()

    if is_android():
        source_dir = Path('/storage/emulated/0') if Path('/storage/emulated/0').exists() else home
        banned_dirs.update({'Android', '.thumbnail', '.thumbnails', 'lost+found'})
        # Common user exclude paths on Android if they exist
        for candidate in [
            Path('/storage/emulated/0/Download/Intro_cs'),
            Path('/storage/emulated/0/ELA MODS Movie')
        ]:
            if candidate.exists():
                exclude_paths.add(candidate.resolve())
    elif current_os == 'Windows':
        source_dir = home / 'Pictures' if (home / 'Pictures').exists() else home
        banned_dirs.update({'$RECYCLE.BIN', 'System Volume Information', 'AppData', 'Thumbs.db'})
    elif current_os == 'Darwin':  # macOS
        source_dir = home / 'Pictures' if (home / 'Pictures').exists() else home
        banned_dirs.update({
            'Library', '.Trash', '.Spotlight-V100', '.fseventsd',
            '.DocumentRevisions-V100', '.TemporaryItems'
        })
    else:  # Linux / BSD / Unix
        source_dir = home / 'Pictures' if (home / 'Pictures').exists() else Path.cwd()
        banned_dirs.update({'.local', '.Trash', 'lost+found'})

    return source_dir, banned_dirs, exclude_paths


def calculate_md5(file_path: Path, chunk_size: int = 262144) -> str | None:
    """Calculate MD5 hash of an on-disk file in RAM-safe chunks (default 256KB)."""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


def calculate_zip_md5(zip_obj: zipfile.ZipFile, rel_posix_path: str, chunk_size: int = 262144) -> str | None:
    """Calculate MD5 hash directly from a streamed zip entry without full RAM buffering."""
    hasher = hashlib.md5()
    try:
        with zip_obj.open(rel_posix_path) as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


def human_size(num_bytes: int) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def parse_arguments():
    default_source, default_banned, default_excludes = detect_system_defaults()

    parser = argparse.ArgumentParser(
        description="Cross-Platform Media Backup & Integrity Verification Utility",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-s', '--source',
        type=Path,
        default=default_source,
        help="Source directory to scan for media"
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help="Destination zip file path or target directory (default: <source>/all_media_archive_<timestamp>.zip)"
    )
    parser.add_argument(
        '-e', '--exclude',
        action='append',
        default=[],
        help="Additional path or directory to exclude (can be specified multiple times)"
    )
    parser.add_argument(
        '--include-audio',
        action='store_true',
        help="Include audio formats (.mp3, .wav, .flac, .aac, .m4a, etc.)"
    )
    parser.add_argument(
        '--custom-ext',
        type=str,
        default=None,
        help="Comma-separated custom extensions to include (e.g., .jpg,.mp4,.png)"
    )
    parser.add_argument(
        '--clean', '--delete-source',
        dest='clean',
        action='store_true',
        help="Permanently delete verified source files and empty directories after backup"
    )
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help="Bypass interactive confirmation before cleaning source files"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Scan and report matching files without creating the zip or deleting files"
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=256,
        help="Hashing chunk size in KB (default: 256)"
    )

    return parser.parse_args(), default_banned, default_excludes


def main():
    args, banned_dir_names, system_excludes = parse_arguments()

    source_dir = args.source.expanduser().resolve()
    if not source_dir.exists() or not source_dir.is_dir():
        print(f"❌ Error: Source directory does not exist or is not a directory: {source_dir}")
        sys.exit(1)

    # Determine Valid Extensions
    if args.custom_ext:
        valid_extensions = {ext.strip().lower() if ext.strip().startswith('.') else f".{ext.strip().lower()}"
                            for ext in args.custom_ext.split(',') if ext.strip()}
    else:
        valid_extensions = IMAGE_EXTENSIONS.union(VIDEO_EXTENSIONS)
        if args.include_audio:
            valid_extensions = valid_extensions.union(AUDIO_EXTENSIONS)

    # Combine Excludes
    exclude_paths = set(system_excludes)
    for exc in args.exclude:
        exc_p = Path(exc).expanduser().resolve()
        exclude_paths.add(exc_p)

    # Determine Output Zip Path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output:
        out_path = args.output.expanduser().resolve()
        if out_path.is_dir() or args.output.name.endswith(('/', '\\')):
            out_path.mkdir(parents=True, exist_ok=True)
            output_zip = out_path / f"all_media_archive_{timestamp}.zip"
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            output_zip = out_path if str(out_path).endswith('.zip') else out_path.with_suffix('.zip')
    else:
        output_zip = source_dir / f"all_media_archive_{timestamp}.zip"

    chunk_bytes = max(32, args.chunk_size) * 1024

    print("=" * 60)
    print(" 📦 Media Backup & Integrity Utility")
    print(f" • Platform       : {platform.system()} ({'Android/Termux' if is_android() else platform.release()})")
    print(f" • Source Dir     : {source_dir}")
    print(f" • Archive Output : {output_zip}")
    print(f" • Extensions ({len(valid_extensions)}) : {', '.join(sorted(valid_extensions)[:8])} ...")
    print(f" • Mode           : {'DRY RUN (Preview Only)' if args.dry_run else ('Archive + Clean' if args.clean else 'Archive Only')}")
    print("=" * 60 + "\n")

    # Optional progress bar via tqdm if available
    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        has_tqdm = False

    # --- Step 1: Scan Source Files ---
    print(f"🔍 Scanning files in: {source_dir}")
    matching_files = []
    total_bytes = 0

    try:
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)

            # In-place directory filtering
            dirs[:] = [
                d for d in dirs
                if (root_path / d).resolve() not in exclude_paths
                and d not in banned_dir_names
                and not d.startswith('.')
            ]

            # Avoid archiving within an existing archive directory
            if "all_media_archive_" in root:
                continue

            for file in files:
                ext = Path(file).suffix.lower()
                if ext in valid_extensions:
                    full_path = root_path / file
                    if full_path.resolve() == output_zip:
                        continue
                    try:
                        file_size = full_path.stat().st_size
                        matching_files.append((full_path, file_size))
                        total_bytes += file_size
                    except (OSError, PermissionError):
                        continue

    except PermissionError as pe:
        print(f"\n❌ Permission Denied while scanning: {pe}")
        if is_android():
            print("👉 Tip for Android/Termux: Run 'termux-setup-storage' and grant storage permissions.")
        else:
            print("👉 Tip: Check read permissions or run with appropriate user privileges.")
        sys.exit(1)

    print(f"Found {len(matching_files)} media files ({human_size(total_bytes)}).\n")

    if not matching_files:
        print("ℹ️ No media files found matching the criteria. Exiting.")
        return

    if args.dry_run:
        print("--- Dry-run file summary (first 10 files) ---")
        for fpath, fsize in matching_files[:10]:
            print(f"  • {fpath.relative_to(source_dir)} ({human_size(fsize)})")
        if len(matching_files) > 10:
            print(f"  ... and {len(matching_files) - 10} more files.")
        print("\n✨ Dry run complete. No archive created, no files modified.")
        return

    # --- Step 2: Archive & Hash Source Files ---
    source_file_registry = {}  # rel_posix_path -> (full_path, orig_md5, orig_size)
    media_count = 0

    print(f"🗜️  Creating archive: {output_zip.name}")
    try:
        # allowZip64=True is critical for cross-platform support when total archive exceeds 4GB
        with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as media_zip:
            iterator = tqdm(matching_files, desc="Archiving & Hashing", unit="file") if has_tqdm else matching_files

            for item in iterator:
                full_path, orig_size = item
                rel_path = full_path.relative_to(source_dir).as_posix()  # Standard POSIX zip path

                orig_md5 = calculate_md5(full_path, chunk_size=chunk_bytes)
                if orig_md5 is not None:
                    try:
                        media_zip.write(full_path, arcname=rel_path)
                        source_file_registry[rel_path] = (full_path, orig_md5, orig_size)
                        media_count += 1
                        if not has_tqdm:
                            print(f"[{media_count}/{len(matching_files)}] Archived & Hashed: {rel_path}")
                    except Exception as e:
                        print(f"⚠️ Skipped write for {rel_path}: {e}")

    except PermissionError:
        print(f"\n❌ Permission denied writing archive: {output_zip}")
        if is_android():
            print("👉 Run: termux-setup-storage")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during archiving: {e}")
        if output_zip.exists():
            output_zip.unlink(missing_ok=True)
        sys.exit(1)

    print(f"\n✅ Archive written with {media_count} files ({human_size(output_zip.stat().st_size)}).")

    # --- Step 3: Streamed RAM-Safe Integrity Verification ---
    print("\n🔐 Starting Streamed RAM-Safe Integrity Check...")
    integrity_passed = True
    verified_count = 0

    try:
        with zipfile.ZipFile(output_zip, 'r') as media_zip:
            iterator = tqdm(source_file_registry.items(), desc="Verifying Checksums", unit="file") if has_tqdm else source_file_registry.items()

            for rel_posix, (full_path, orig_md5, orig_size) in iterator:
                try:
                    zip_md5 = calculate_zip_md5(media_zip, rel_posix, chunk_size=chunk_bytes)
                    zip_size = media_zip.getinfo(rel_posix).file_size

                    if zip_md5 != orig_md5 or zip_size != orig_size:
                        print(f"\n❌ CORRUPTION DETECTED: {rel_posix} checksum or size mismatch!")
                        integrity_passed = False
                        break
                    else:
                        verified_count += 1
                        if not has_tqdm and verified_count % 50 == 0:
                            print(f" Verified {verified_count}/{media_count} files...")
                except Exception as e:
                    print(f"\n❌ Error verifying {rel_posix}: {e}")
                    integrity_passed = False
                    break

    except Exception as e:
        print(f"\n❌ Verification halted due to error: {e}")
        integrity_passed = False

    print("\n" + "=" * 55)
    print(f" Integrity Check Result : {'PASSED ✓' if integrity_passed else 'FAILED ✗'}")
    print(f" Verified               : {verified_count}/{media_count} files")
    print(f" Final Archive Location : {output_zip}")
    print("=" * 55)

    # --- Step 4: Optional Cleaner Mechanism ---
    if not integrity_passed:
        print("\n⚠️ WARNING: Integrity verification failed! Source files are left untouched.")
        return

    if args.clean and media_count > 0:
        if not args.yes:
            prompt = input(f"\n⚠️  Are you sure you want to permanently delete {media_count} source files from {source_dir}? [y/N]: ")
            if prompt.strip().lower() not in ('y', 'yes'):
                print("🛑 Cleanup aborted by user. All source files are preserved.")
                return

        print("\n🧹 Proceeding to clean verified source files...")
        deleted_count = 0
        for rel_posix, (full_path, _, _) in source_file_registry.items():
            try:
                full_path.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ Could not delete {full_path}: {e}")

        # Bottom-up empty directory removal
        print("🧹 Cleaning up empty directories...")
        for root, dirs, files in os.walk(source_dir, topdown=False):
            dir_path = Path(root)
            if dir_path in exclude_paths or any(b in dir_path.parts for b in banned_dir_names):
                continue
            if dir_path == source_dir:
                continue
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
            except Exception:
                pass

        print(f"\n🎉 Clean complete! Deleted {deleted_count} source files and empty directories.")
        print(f"Your safe archive is located at:\n{output_zip}")
    else:
        if not args.clean:
            print("\n💡 Note: Source files were preserved. To remove source files after archiving, use '--clean'.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Process interrupted by user. Exiting cleanly.")
        sys.exit(130)
