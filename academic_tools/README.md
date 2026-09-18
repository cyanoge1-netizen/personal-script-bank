# Academic Tools (একাডেমিক টুলস)

সিলেট ইঞ্জিনিয়ারিং কলেজ (SEC)-এর একাডেমিক ও ল্যাবরেটরি কার্যক্রম দ্রুত এবং নির্ভুলভাবে সম্পন্ন করার জন্য তৈরি করা অটোমেশন স্ক্রিপ্টসমূহ।

---

## 📂 স্ক্রিপ্ট তালিকা (Index Table)

| স্ক্রিপ্ট | ভাষা | উদ্দেশ্য | ব্যবহারের উদাহরণ |
| :--- | :--- | :--- | :--- |
| [`download_questions.py`](download_questions.py) | Python 3 | SEC-এর ৪১টি অফিসিয়াল টার্ম ফাইনাল ও অ্যাডমিশন টেস্ট প্রশ্নপত্র ডাউনলোড ও ডিপার্টমেন্ট-সেমিস্টার অনুযায়ী সাজানো | `python3 download_questions.py cse` |
| [`fast_create.py`](fast_create.py) | Python 3 | মাল্টি-প্রসেসিং ব্যবহার করে সি/সি++ ল্যাব অ্যাসাইনমেন্টের কঙ্কাল (skeleton) কোড দ্রুত তৈরি | `python3 fast_create.py lab 10 -d ./lab_01` |

---

### ১. `download_questions.py` বিস্তারিত

- **বৈশিষ্ট্য:**
  - সিএসই, ট্রিপল-ই, সিভিল এবং আন্ডারগ্র্যাজুয়েট ভর্তি পরীক্ষার প্রশ্নপত্রের পূর্ণাঙ্গ ডাটাবেজ।
  - ক্রস-প্ল্যাটফর্ম টার্মিনাল UI (Windows, Linux, macOS, Android/Termux)।
  - মাল্টি-থ্রেডেড ডাউনলোড (`concurrent.futures`), ক্যাশিং ও `%PDF` বাইনারি সিগনেচার যাচাই।
- **ব্যবহার:**
  ```bash
  # ইন্টারঅ্যাক্টিভ ভিজ্যুয়াল মেনু
  python3 download_questions.py

  # নির্দিষ্ট ডিপার্টমেন্টের প্রশ্ন ডাউনলোড
  python3 download_questions.py cse
  python3 download_questions.py eee
  python3 download_questions.py civil
  python3 download_questions.py all

  # কাস্টম ফোল্ডারে ডাউনলোড
  python3 download_questions.py all -o ~/MyArchive

  # ডাউনলোড না করে শুধু প্রিভিউ দেখতে
  python3 download_questions.py --dry-run cse

  # প্রশ্ন তালিকার মেটাডাটা JSON ফাইলে এক্সপোর্ট
  python3 download_questions.py --export-json questions.json
  ```

---

### ২. `fast_create.py` বিস্তারিত

- **বৈশিষ্ট্য:**
  - মাল্টি-কোর প্রসেসিং (`ProcessPoolExecutor`) দিয়ে দ্রুত সমান্তরালে ফাইল তৈরি।
  - সি/সি++ কোডের আদর্শ টেমপ্লেট ইনজেকশন।
- **ব্যবহার:**
  ```bash
  python3 fast_create.py task 10 -d ./assignment_1
  ```
