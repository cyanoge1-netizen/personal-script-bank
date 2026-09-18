# Personal-Scriptbank

এই রিপোজিটরিটিতে আমার ব্যক্তিগত ক্রস-প্ল্যাটফর্ম অটোমেশন স্ক্রিপ্ট এবং টুলগুলো সংরক্ষিত আছে। সিএসই (CSE) শিক্ষার্থী হিসেবে দৈনন্দিন ল্যাব ওয়ার্ক, মিডিয়া ব্যাকআপ এবং সামগ্রিক প্রোডাক্টিভিটি বাড়ানোর লক্ষ্যে এই স্ক্রিপ্টগুলো তৈরি করা হয়েছে।

## 🚀 সমর্থিত প্ল্যাটফর্ম (Cross-Platform Support)
- **Android (Termux)**
- **Linux (Ubuntu, Debian, Fedora, Arch)**
- **macOS**
- **Windows**

---

## 📂 বিষয়বস্তু (Contents)
1. **Cross-Platform Media Backup Utility (`media_backup.py`):**
   - ডিভাইস থেকে ছবি এবং ভিডিও ফাইল স্বয়ংক্রিয়ভাবে স্ক্যান করে 64-বিট স্ট্রিমিং জিপ আর্কাইভে ব্যাকআপ তৈরি করে।
   - RAM-Safe চাঙ্কড MD5 হ্যাশিংয়ের মাধ্যমে ফাইল ও জিপ ফাইলের শতভাগ ডেটা ইনটিগ্রিটি নিশ্চিত করে।
   - প্ল্যাটফর্ম-ভিত্তিক ইন্টেলিজেন্ট পাথ ডিটেকশন ও সিস্টেম ফোল্ডার এক্সক্লুশন (যেমন Android, Windows, Mac, Linux সিস্টেম ডিরেক্টরি)।
   - নিরাপদ প্রিভিউ (`--dry-run`) এবং যাচাইকৃত ব্যাকআপের পর সোর্স ফাইল ক্লিনিং অপশন (`--clean`)।

2. **Fast C/C++ Generator (`fast_create.py`):**
   - মাল্টি-প্রসেসিং (`concurrent.futures`) ব্যবহার করে নিমিষেই ল্যাব অ্যাসাইনমেন্টের জন্য প্রয়োজনীয় C/C++ কঙ্কাল (skeleton template) ফাইল তৈরি করে।

---

## 🛠️ টেকনিক্যাল স্পেসিফিকেশন
- **Language:** Python 3 (3.7+)
- **Dependencies:** 
  - Standard Library: `argparse`, `pathlib`, `zipfile`, `hashlib`, `platform`, `concurrent.futures` (জিরো এক্সটার্নাল ডিপেন্ডেন্সি দিয়েও চলে)
  - Optional: `tqdm` (টার্মিনালে প্রগ্রেস বার ভিজ্যুয়ালাইজেশনের জন্য)

---

## 💻 ব্যবহারের নিয়ম (Usage)

### ১. মিডিয়া ব্যাকআপ ইউটিলিটি (`media_backup.py`)

**স্বয়ংক্রিয় মোড (ডিফল্ট পাথ অনুযায়ী):**
```bash
python3 media_backup.py
```

**প্রিভিউ মোড (ফাইল না মুছে বা আর্কাইভ না করে শুধু স্ক্যান রিপোর্ট দেখতে):**
```bash
python3 media_backup.py -s /path/to/source --dry-run
```

**কাস্টম সোর্স ও আউটপুট ডিরেক্টরি নির্ধারণ:**
```bash
python3 media_backup.py -s ~/Pictures -o ~/Backups
```

**অডিও ফাইল অন্তর্ভুক্ত করতে:**
```bash
python3 media_backup.py -s ~/Media --include-audio
```

**আর্কাইভ ভেরিফিকেশন সফল হলে সোর্স ফাইল মুছে ফেলার জন্য (নিরাপদ ক্লিনিং):**
```bash
python3 media_backup.py -s /path/to/media --clean
```

---

### ২. ফাস্ট C/C++ ফাইল জেনারেটর (`fast_create.py`)

**ল্যাব টাস্কের জন্য ১০টি C ফাইল তৈরি করতে:**
```bash
python3 fast_create.py lab_task 10 -d ./my_lab
```

**C++ এক্সটেনশন দিয়ে ফাইল তৈরি করতে:**
```bash
python3 fast_create.py assignment 5 -d ./cpp_tasks -e .cpp
```

---

## 🎯 লক্ষ্য
কোডিং ও কম্পিউটিং এনভায়রনমেন্টকে আরও সুশৃঙ্খল করা এবং সিস্টেম অটোমেশনের মাধ্যমে সময় বাঁচিয়ে প্রোডাক্টিভিটি ত্বরান্বিত করা।

## 👤 অবদানকারী (Author)
**Suleman Ahmed Shuvo**  
সিএসই, সিলেট ইঞ্জিনিয়ারিং কলেজ (SEC)।
