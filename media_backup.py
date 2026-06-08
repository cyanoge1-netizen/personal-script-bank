#!/usr/bin/env python3
import os
import zipfile
import hashlib
from datetime import datetime

SOURCE_DIR = "/storage/emulated/0"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_ZIP = f"{SOURCE_DIR}/all_media_archive_{TIMESTAMP}.zip"

EXCLUDE_PATHS = {
    "/storage/emulated/0/Download/Intro_cs",
    "/storage/emulated/0/ELA MODS Movie"
}

BANNED_DIR_NAMES = {'Android', '.thumbnail', '.thumbnails', 'lost+found', '.git'}

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif', '.heic', '.heif', '.raw', '.dng', '.svg', '.ico'}
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpeg', '.mpg', '.ts', '.vob'}
VALID_EXTENSIONS = IMAGE_EXTENSIONS.union(VIDEO_EXTENSIONS)

source_file_registry = {}

def calculate_md5(file_path):
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def calculate_zip_md5(zip_obj, rel_path):
    """ জিপ ফাইলের ভেতর থেকে ব্লকিং মেকানিজমে MD5 বের করার ফিক্সড লজিক (র‍্যাম সেফ) """
    hasher = hashlib.md5()
    try:
        with zip_obj.open(rel_path) as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

print(f"Scanning and archiving media from: {SOURCE_DIR}")
print(f"Archive Destination: {OUTPUT_ZIP}\n")

media_count = 0
try:
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as media_zip:
        for root, dirs, files in os.walk(SOURCE_DIR):
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in EXCLUDE_PATHS and d not in BANNED_DIR_NAMES and not d.startswith('.')]
            
            if "all_media_archive_" in root:
                continue

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in VALID_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, SOURCE_DIR)
                    
                    orig_md5 = calculate_md5(full_path)
                    orig_size = os.path.getsize(full_path)
                    
                    if orig_md5:
                        try:
                            media_zip.write(full_path, rel_path)
                            source_file_registry[rel_path] = (full_path, orig_md5, orig_size)
                            media_count += 1
                            print(f"[{media_count}] Archived & Hashed: {rel_path}")
                        except Exception as e:
                            print(f"Skipped (Write Error): {rel_path} -> {e}")

    print(f"\nArchive created with {media_count} files. Starting RAM-Safe Integrity Check...")

    # --- স্টেপ ২: জিপ ভেরিফিকেশন (ফিক্সড - ওওএম ক্র্যাশ হবে না) ---
    integrity_passed = True
    verified_count = 0
    
    with zipfile.ZipFile(OUTPUT_ZIP, 'r') as media_zip:
        for rel_path, (full_path, orig_md5, orig_size) in source_file_registry.items():
            try:
                zip_md5 = calculate_zip_md5(media_zip, rel_path)
                zip_size = media_zip.getinfo(rel_path).file_size
                
                if zip_md5 != orig_md5 or zip_size != orig_size:
                    print(f"❌ CORRUPTION DETECTED: {rel_path} Mismatch!")
                    integrity_passed = False
                    break
                else:
                    verified_count += 1
            except Exception as e:
                print(f"❌ Error verifying {rel_path}: {e}")
                integrity_passed = False
                break

    print("\n" + "="*50)
    print(f"Integrity Check Result: {'PASSED ✓' if integrity_passed else 'FAILED ✗'}")
    print(f"Verified {verified_count}/{media_count} files successfully.")
    print("="*50)

    # --- স্টেপ ৩: ক্লিনার মেকানিজম (ফাইল + খালি ফোল্ডার ক্লিনিং) ---
    if integrity_passed and media_count > 0:
        print("\nSafe to proceed. Cleaning source media files...")
        deleted_count = 0
        for rel_path, (full_path, _, _) in source_file_registry.items():
            try:
                os.remove(full_path)
                deleted_count += 1
                print(f"[{deleted_count}] Deleted: {rel_path}")
            except Exception as e:
                print(f"Could not delete {rel_path}: {e}")
        
        # এক্সট্রা ফিচার: ফাঁকা ফোল্ডারগুলো ক্লিন করা (Bottom-up cleaning)
        print("\nCleaning up empty directories...")
        for root, dirs, files in os.walk(SOURCE_DIR, topdown=False):
            if root in EXCLUDE_PATHS or any(b_dir in root for b_dir in BANNED_DIR_NAMES):
                continue
            try:
                if not os.listdir(root):  # ফোল্ডারটি যদি এখন ফাঁকা হয়
                    os.rmdir(root)
            except Exception:
                pass
                
        print(f"\nAll clean, Shuvo! Successfully deleted {deleted_count} source files and empty folders.")
        print(f"Your safe archive is here: {OUTPUT_ZIP}")
    else:
        print("\n⚠️ WARNING: Integrity check failed or no files found!")
        print("Source files are left untouched.")

except PermissionError:
    print("\nPermission Denied! Run: termux-setup-storage")
except Exception as e:
    print(f"\nAn error occurred: {e}")
