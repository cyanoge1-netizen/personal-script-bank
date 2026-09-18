# Personal-Scriptbank

এই রিপোজিটরিটিতে আমার ব্যক্তিগত ক্রস-প্ল্যাটফর্ম অটোমেশন স্ক্রিপ্ট এবং প্রোডাক্টিভিটি টুলগুলো সুশৃঙ্খল ক্যাটাগরিভিত্তিক ফোল্ডারে সংরক্ষিত আছে। সিএসই (CSE) শিক্ষার্থী হিসেবে ল্যাব অ্যাসাইনমেন্ট, প্রশ্নপত্র সংরক্ষণ এবং ফাইল অটোমেশন সহজ করার লক্ষ্যে এই প্রজেক্টটি তৈরি।

---

## 🚀 সমর্থিত প্ল্যাটফর্ম (Cross-Platform Support)
- 📱 **Android (Termux / Proot)**
- 🐧 **Linux (Ubuntu, Debian, Fedora, Arch)**
- 🍎 **macOS**
- 🪟 **Windows (PowerShell / CMD / WSL)**

---

## 📂 ক্যাটাগরি এবং স্ক্রিপ্ট ইনডেক্স (Directory Structure)

```
personal-script-bank/
├── academic_tools/          # সিলেট ইঞ্জিনিয়ারিং কলেজের শিক্ষা ও ল্যাব সম্পর্কিত টুলস
│   ├── download_questions.py# এসইসি টার্ম ফাইনাল ও অ্যাডমিশন টেস্ট প্রশ্ন ডাউনলোডার
│   ├── fast_create.py       # মাল্টি-কোর C/C++ স্কেলিটন ফাইল জেনারেটর
│   └── README.md            # বিস্তারিত গাইড ও ব্যবহারবিধি
│
├── backup_utilities/        # মিডিয়া ও সিস্টেম ব্যাকআপ ইউটিলিটিজ
│   ├── media_backup.py      # ক্রস-প্ল্যাটফর্ম Zip64 ও MD5 ইনটিগ্রিটি ব্যাকআপ টুল
│   └── README.md            # বিস্তারিত গাইড ও ব্যবহারবিধি
│
├── .gitignore               # পাইথন ও এনভায়রনমেন্ট ইগনোর রুলস
└── README.md                # রিপোজিটরি মাস্টার ইনডেক্স
```

---

## 🛠️ মাস্টার ইনডেক্স টেবিল (Master Table)

| বিভাগ (Category) | স্ক্রিপ্ট | ভাষা | সংক্ষিপ্ত বিবরণ |
| :--- | :--- | :--- | :--- |
| [**Academic Tools**](academic_tools/) | [`download_questions.py`](academic_tools/download_questions.py) | Python 3 | এসইসির CSE, EEE, CE ও ভর্তি পরীক্ষার ৪১টি প্রশ্নপত্র স্বয়ংক্রিয় ডাউনলোড |
| [**Academic Tools**](academic_tools/) | [`fast_create.py`](academic_tools/fast_create.py) | Python 3 | ল্যাব ক্লাসের জন্য দ্রুত সমান্তরালে C/C++ স্কেলিটন ফাইল তৈরি |
| [**Backup Utilities**](backup_utilities/) | [`media_backup.py`](backup_utilities/media_backup.py) | Python 3 | ছবি/ভিডিও স্বয়ংক্রিয় ব্যাকআপ, চাঙ্কড MD5 ভেরিফিকেশন ও সেফ ক্লিনার |

---

## 💻 দ্রুত ব্যবহারের নির্দেশিকা (Quick Start)

### ১. প্রশ্নপত্র ডাউনলোড (SEC Question Downloader)
```bash
cd academic_tools

# ইন্টারঅ্যাক্টিভ ভিজ্যুয়াল মেনু
python3 download_questions.py

# সরাসরি সিএসই (CSE) প্রশ্ন ডাউনলোড
python3 download_questions.py cse
```

### ২. ল্যাব ফাইল তৈরি (C/C++ File Generator)
```bash
cd academic_tools

# ১০টি C স্কেলিটন ফাইল তৈরি
python3 fast_create.py lab_task 10 -d ./my_lab
```

### ৩. মিডিয়া ব্যাকআপ (Media Archiver)
```bash
cd backup_utilities

# ব্যাকআপ নেওয়া ও ইনটিগ্রিটি যাচাই
python3 media_backup.py -s ~/Pictures -o ~/Backups
```

---

## 🎯 লক্ষ্য
কোডিং ও কম্পিউটিং এনভায়রনমেন্টকে আরও সুশৃঙ্খল করা এবং সিস্টেম অটোমেশনের মাধ্যমে সময় বাঁচিয়ে একাডেমিক প্রোডাক্টিভিটি বৃদ্ধি করা।

## 👤 অবদানকারী (Author)
**Suleman Ahmed Shuvo**  
কম্পিউটার সায়েন্স অ্যান্ড ইঞ্জিনিয়ারিং (CSE), ব্যাচ: ১৯  
সিলেট ইঞ্জিনিয়ারিং কলেজ (SEC)।
