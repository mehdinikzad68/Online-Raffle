# Online Raffle (سیستم جامع قرعه‌کشی و تحلیل آماری مسابقات)

An interactive, visual raffle draw and quiz analytics application written in Python. This tool processes quiz participant data from Excel files, evaluates scores, generates insightful statistical visualizations, exports comprehensive Excel reports, and features an engaging full-screen animated live raffle draw with sound effects.

یک نرم‌افزار تعاملی و گرافیکی جهت تحلیل نتایج آزمون‌ها/مسابقات و برگزاری زنده مراسم قرعه‌کشی برندگان با افکت‌های بصری و صوتی.

---

## 🌟 Features (ویژگی‌ها)

- 📊 **Automated Quiz Evaluation & Scoring:** Automatically compares participant answers with answer keys and computes total scores.
- 🎯 **Qualification Filtering:** Filters eligible candidates based on qualification score thresholds (e.g., score >= 2).
- 📈 **Statistical Dashboard & Visual Charts:**
  - Displays participant breakdown by score (0, 1, 2, 3 correct answers).
  - Generates charts (pie chart for score distribution, bar chart for qualification status) via Matplotlib & Seaborn.
- 📑 **Advanced Multi-Sheet Excel Reports:**
  - `Dashboard`: Summary of key statistics.
  - `Full_Results`: Complete participant list with calculated scores.
  - `Qualified_List`: List of qualified candidates ready for the draw.
- 🎲 **Interactive Live Draw & Winner Animation Panel:**
  - Live draw panel powered by Tkinter.
  - Full-screen winner reveal animation with dynamic text shuffle and zoom-in effects.
  - Background audio playback using Pygame (`draw_sound.mp3`).
  - Validation to prevent duplicate winners.
  - Export final winners list to Excel (`Winners_List.xlsx`).

---

## 📁 Project Structure (ساختار پروژه)

```text
Online-Raffle/
├── Amar-ghorekeshi.py       # Main Python application with English GUI / Persian data fields
├── Amar-ghorekeshi.py.txt   # Alternative Persian GUI reference script
├── requirements.txt         # Project dependencies
├── .gitignore               # Git ignore rules
└── README.md                # Documentation
```

---

## 🚀 Getting Started (راهنمای راه‌اندازی و اجرا)

### 1. Prerequisites (پیش‌نیازها)
Make sure Python 3.8+ is installed on your system.

### 2. Installation (نصب وابستگی‌ها)
Clone the repository and install the required dependencies:

```bash
git clone https://github.com/mehdinikzad68/Online-Raffle.git
cd Online-Raffle
pip install -r requirements.txt
```

### 3. Audio Asset (Optional)
If you wish to have sound effects during the live winner shuffle, place an MP3 sound file named `draw_sound.mp3` in the root directory alongside `Amar-ghorekeshi.py`.

### 4. Running the Application (اجرای برنامه)

Run the script using:

```bash
python Amar-ghorekeshi.py
```

1. A file picker dialog will prompt you to select the participants Excel file (`.xlsx` or `.xls`).
2. The console interactive menu will display options:
   - `1`: Display Overall Statistics
   - `2`: Display & Save List of Qualified Participants
   - `3`: Export Advanced Excel Report
   - `4`: Display Graphical Charts
   - `5`: Start Live Draw Process
   - `0`: Exit Program

---

## 📋 Input File Format (فرمت فایل ورودی)

The Excel file should contain columns such as:
- `نام و نام خانوادگی` (Full Name)
- `شماره تماس` (Phone Number)
- `ایمیل` (Email)
- `سوال 1`, `سوال 2`, `سوال 3` (Quiz questions to score)

*(Note: Correct answer options and column names can be customized inside `load_and_analyze_data` in `Amar-ghorekeshi.py`)*.

---

## 🛠️ Built With (فناوری‌های مورد استفاده)

- [Python](https://www.python.org/)
- [Pandas](https://pandas.pydata.org/) & [OpenPyXL](https://openpyxl.readthedocs.io/) - Data manipulation and multi-sheet Excel generation
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI and interactive live draw animations
- [Matplotlib](https://matplotlib.org/) & [Seaborn](https://seaborn.pydata.org/) - Statistical charts and visualizations
- [Pygame](https://www.pygame.org/) - Audio playback for raffle excitement

---

## 📄 License

This project is licensed under the MIT License.
