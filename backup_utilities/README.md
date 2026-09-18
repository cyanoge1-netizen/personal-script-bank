# Backup Utilities (ব্যাকআপ ইউটিলিটিজ)

সিস্টেম ও মিডিয়া ফাইল সংরক্ষণ, কম্প্রেসড আর্কাইভিং এবং ডেটা ইনটিগ্রিটি নিশ্চিতকরণের ক্রস-প্ল্যাটফর্ম টুলস।

---

## 📂 স্ক্রিপ্ট তালিকা (Index Table)

| স্ক্রিপ্ট | ভাষা | উদ্দেশ্য | ব্যবহারের উদাহরণ |
| :--- | :--- | :--- | :--- |
| [`media_backup.py`](media_backup.py) | Python 3 | ছবি ও ভিডিও স্বয়ংক্রিয়ভাবে স্ক্যান করে Zip64 আর্কাইভে ব্যাকআপ ও RAM-safe MD5 হ্যাশ ভেরিফিকেশন | `python3 media_backup.py -s ~/Pictures` |

---

### ১. `media_backup.py` বিস্তারিত

- **বৈশিষ্ট্য:**
  - সম্পূর্ণ ক্রস-প্ল্যাটফর্ম (Android/Termux, Windows, Linux, macOS)।
  - বড় ফাইলের জন্য ৬৪-বিট জিপ সাপোর্ট (`allowZip64=True`)।
  - RAM-Safe চাঙ্কড MD5 হ্যাশিং—কম মেমরিতেও ওওএম (OOM) ক্র্যাশ ছাড়া ইনটিগ্রিটি চেক।
  - নিরাপদ প্রিভিউ মোড (`--dry-run`) এবং ব্যবহারকারীর নিশ্চিতকরণ সাপেক্ষে সোর্স ক্লিনিং (`--clean`)।
- **ব্যবহার:**
  ```bash
  # স্বয়ংক্রিয় ডিফল্ট পাথ অনুযায়ী স্ক্যান ও আর্কাইভ
  python3 media_backup.py

  # নির্দিষ্ট ডিরেক্টরি প্রিভিউ
  python3 media_backup.py -s /path/to/media --dry-run

  # কাস্টম সোর্স ও আউটপুট ডিরেক্টরি
  python3 media_backup.py -s ~/Pictures -o ~/Backups

  # অডিও ফাইল অন্তর্ভুক্ত করতে
  python3 media_backup.py -s ~/Media --include-audio

  # সফল ভেরিফিকেশনের পর সোর্স ফাইল ডিলিট করতে
  python3 media_backup.py -s /path/to/media --clean
  ```
