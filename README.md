# 🗂️ Dump Extractor

**Dump Extractor** is a GUI-based Python application that extracts and cleans questions from exam preparation PDFs (aka "dumps"). It detects questions based on specific patterns like `QUESTION NO:` or `NO.`, extracts the corresponding answer, and generates a clean, easy-to-review PDF file.

## 📌 Features

-   ✅ Extracts questions and answers from PDF files
-   ✅ Supports both `QUESTION NO:` and `NO.` styles
-   ✅ Automatically removes explanations and irrelevant text
-   ✅ Line breaks and formatting are cleaned for improved readability
-   ✅ Choose whether to:
    -   Omit answers
    -   Display answers normally
    -   Display answers in **light gray** for semi-transparent review mode
-   ✅ Clean PDF output with readable formatting
-   ✅ Simple step-by-step user interface
-   ✅ System pop-up with completion status and automatic app exit

## 🖥️ How to Use

1. **Launch the application**
2. **Click "Next"** on the welcome screen
3. **Choose your PDF file** (containing the dump questions)
4. **Select an output folder** (or use the default executable directory)
5. **Choose whether to display answers**
    - You can choose "Normal" or "Semi-transparent" if answers are shown
6. **Click "Extract"**
7. A result popup will display the status and file location
8. The app automatically exits when you close the popup

## 📦 Installation

### 1. Run from Python (for developers)

```bash
git clone https://github.com/yourusername/dump-extractor.git
cd dump-extractor
```

**Dependencies:**

-   `PyPDF2`
-   `fpdf`
-   `tkinter` (built-in for most Python distributions)

Install with:

```bash
pip install PyPDF2 fpdf
```

### 2. Build Executable (.exe)

Use `pyinstaller` to build a standalone executable from `new_updated/` directory:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "C:/Windows/Fonts/malgun.ttf;." DumpExtractor.py
```

> Make sure the font path is correct for your system.  
> Output will be in the `dist/` folder.

## 📁 Output Format

The output PDF will contain:

-   Questions labeled as `NO. X`
-   Clean multiple-choice options
-   (Optional) Answer section shown in normal or light gray font
-   No explanation or extra commentary

## ❓ FAQ

**Q: What if my PDF uses `NO.` instead of `QUESTION NO:`?**  
A: It supports both automatically.

**Q: Will it work on macOS or Linux?**  
A: The app was built for Windows GUI (using the `malgun.ttf` font), but the core logic is cross-platform if adapted.

**Q: Can I batch-process multiple PDFs?**  
A: Not yet, but support for batch processing may be added in a future version.

## 🙌 Credits

Developed by [sehyeon.eom](https://github.com/muring).

Feel free to contribute or submit issues on GitHub!
