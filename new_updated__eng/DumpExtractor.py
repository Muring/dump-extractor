# Complete code with an extended regular expression to identify question blocks that start with 'QUESTION NO:' or 'NO.

import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader
from fpdf import FPDF

font_path_regular = "C:\\Windows\\Fonts\\arial.ttf"      # Regular
font_path_bold = "C:\\Windows\\Fonts\\arialbd.ttf"       # Bold

# Register phrases such as headers or footers you want to remove.
unwanted_phrases = [
    "IT Certification Guaranteed, The Easy Way!",
]

class PDFWithHiddenAnswers(FPDF):
    def __init__(self, title="", show_answer=True, answer_transparent=False):
        super().__init__()
        self.title_text = title
        self.show_answer = show_answer
        self.answer_transparent = answer_transparent
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("ArialCustom", "", font_path_regular, uni=True)
        self.add_font("ArialCustom", "B", font_path_bold, uni=True)
        self.set_font("ArialCustom", size=12)
        self.set_text_color(0, 0, 0)
        self._add_title()

    def _add_title(self):
        if self.title_text:
            self.set_font("ArialCustom", style="B", size=20)
            self.cell(0, 15, self.title_text, ln=True, align="C")
            self.ln(10)
            self.set_font("ArialCustom", size=12)

    def add_question_text(self, question_text):
        lines = question_text.strip().split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Question number
            if re.match(r'NO[:\.] \d+', stripped, re.IGNORECASE):
                self.set_font("ArialCustom", style="B", size=13)
                self.multi_cell(0, 8, stripped)
                self.set_font("ArialCustom", size=12)

            # Answer choices
            elif re.match(r'^[A-E]\.', stripped):
                self.ln(2)
                self.multi_cell(0, 6, stripped)

            # Answer
            elif stripped.startswith("Answer:"):
                self.ln(6)
                if self.show_answer:
                    if self.answer_transparent:
                        self.set_text_color(240, 240, 240)
                    self.multi_cell(0, 8, stripped)
                    self.set_text_color(0, 0, 0)
                self.ln(8)

            # Question content
            else:
                self.multi_cell(0, 8, stripped)

def normalize_question_number(text):
    # QUESTION NO: 1 or NO. 1 → NO: 1
    return re.sub(r'(?:QUESTION\s+)?NO[:\.]\s*(\d+)', r'NO. \1', text, flags=re.IGNORECASE)

def extract_questions_with_answer(pdf_path, output_dir):
    import re
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_txt = os.path.join(output_dir, f"{base_name}_cleaned.txt")

    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()

    # Delete unwanted phrases
    for phrase in unwanted_phrases:
        full_text = full_text.replace(phrase, "")
    
    # Delete page lines
    full_text = re.sub(r'^\s*\d+\s*$', '', full_text, flags=re.MULTILINE)

    # Extract questions (Starts with QUESTION NO or NO. and ends with Answer)
    questions_with_answers = re.findall(
        r"((?:QUESTION\s+NO|NO)[:\.]\s*\d+.*?^Answer:.*?$)",
        full_text,
        re.DOTALL | re.MULTILINE
    )

    def clean_line_breaks(text):
        lines = text.split('\n')
        cleaned_lines = []

        for i, line in enumerate(lines):
            line = line.strip()
            if re.match(r'^NO[:\.] \d+', line):  # Question numbers must always appear on a separate line.
                cleaned_lines.append(line)
            elif re.match(r'^[A-E]\.', line) or line.startswith('Answer:'):  # Keep in seperate lines for answer choices
                cleaned_lines.append('\n' + line)
            else:
                # Maintain a line break before the question text if it's directly preceded by a question number; 
                # Otherwise, place it on the same line as the preceding content.
                if cleaned_lines and re.match(r'^NO[:\.] \d+', cleaned_lines[-1]):
                    cleaned_lines.append(line)
                else:
                    cleaned_lines.append(' ' + line if cleaned_lines else line)

        return '\n'.join(cleaned_lines).strip()

    def normalize_question_number(text):
        return re.sub(r'(?:QUESTION\s+)?NO[:\.]\s*(\d+)', r'NO. \1', text, flags=re.IGNORECASE)

    cleaned = [
        normalize_question_number(
            clean_line_breaks(re.sub(r'\n+', '\n', q))
        ).strip()
        for q in questions_with_answers
    ]

    if not cleaned:
        raise ValueError("We couldn’t extract the questions. The PDF format might not match the expected layout.")

    with open(output_txt, "w", encoding="utf-8") as f:
        for q in cleaned:
            f.write(q + "\n\n")

    return base_name, len(cleaned), output_txt

def txt_to_pdf_unicode(base_name, output_dir, show_answer=True, answer_transparent=False, title=""):
    txt_path = os.path.join(output_dir, f"{base_name}_cleaned.txt")
    pdf_path = os.path.join(output_dir, f"{base_name}_cleaned.pdf")

    pdf = PDFWithHiddenAnswers(title=title, show_answer=show_answer, answer_transparent=answer_transparent)

    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        questions = content.split('\n\n')
        for q in questions:
            pdf.add_question_text(q)

    pdf.output(pdf_path)
    return pdf_path

class DumpExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dump Extractor")
        self.file_path = ""
        self.output_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))

        self.button_style = {
            "relief": "solid",
            "bd": 1,
            "highlightthickness": 1,
            "highlightbackground": "#f0f0f0",
            "highlightcolor": "blue"
        }

        self.intro_frame()

    def intro_frame(self):
        self.clear_window()
        self.content_frame = tk.Frame(self.root, padx=20, pady=20, bg="white")
        self.content_frame.pack(fill="both", expand=True)

        tk.Label(self.content_frame, text="Welcome to Dump Extractor", font=("Arial", 16, "bold"), pady=10, bg="white").pack()
        tk.Label(
            self.content_frame,
            text="This application extracts only the questions and answers from a dump PDF and converts them into a new PDF.\n"
                 "You can choose whether to display the answers, how they are displayed, and where the file is saved.\n\n"
                 "Click 'Next' to proceed.",
            wraplength=550, justify="left", bg="white"
        ).pack(pady=10)

        self.bottom_frame([("Next", self.options_frame)])

    def options_frame(self):
        self.clear_window()
        self.content_frame = tk.Frame(self.root, padx=20, pady=20)
        self.content_frame.pack(fill="both", expand=True)

        section = tk.LabelFrame(self.content_frame, text="Set file path", padx=10, pady=10)
        section.pack(fill="x", pady=10)

        tk.Label(section, text="PDF file path").pack(anchor="w")
        file_frame = tk.Frame(section)
        file_frame.pack(fill="x", pady=5)
        self.file_entry = tk.Entry(file_frame, highlightthickness=1, highlightbackground="lightgray", highlightcolor="blue", insertbackground="blue")
        self.file_entry.pack(side="left", fill="x", expand=True, ipadx=1, ipady=1)
        tk.Button(file_frame, text="찾기", command=self.select_file, **self.button_style).pack(side="left", padx=5)

        tk.Label(section, text="Save file path").pack(anchor="w", pady=(10, 0))
        out_frame = tk.Frame(section)
        out_frame.pack(fill="x", pady=5)
        self.output_entry = tk.Entry(out_frame, highlightthickness=1, highlightbackground="lightgray", highlightcolor="blue", insertbackground="blue")
        self.output_entry.insert(0, self.output_dir)
        self.output_entry.pack(side="left", fill="x", expand=True, ipadx=1, ipady=1)
        tk.Button(out_frame, text="Search", command=self.select_output_dir, **self.button_style).pack(side="left", padx=5)

        section2 = tk.LabelFrame(self.content_frame, text="Answer display setting", padx=10, pady=10)
        section2.pack(fill="x", pady=10)

        self.answer_var = tk.BooleanVar(value=False)
        self.answer_check = tk.Checkbutton(section2, text="Show Answer", variable=self.answer_var, command=self.toggle_transparency_options)
        self.answer_check.pack(anchor="w")

        self.transparent_var = tk.StringVar(value="transparent")
        self.radio_transparent = tk.Radiobutton(section2, text="Semi-transparent", variable=self.transparent_var, value="transparent", state="disabled")
        self.radio_opaque = tk.Radiobutton(section2, text="Opaque", variable=self.transparent_var, value="opaque", state="disabled")
        self.radio_transparent.pack(anchor="w", padx=20)
        self.radio_opaque.pack(anchor="w", padx=20)

        self.bottom_frame([
            ("Cancel", self.confirm_exit),
            ("Extract", self.run_extraction),
            ("Previous", self.intro_frame)
        ])

    def toggle_transparency_options(self):
        state = "normal" if self.answer_var.get() else "disabled"
        self.radio_opaque.configure(state=state)
        self.radio_transparent.configure(state=state)

    def bottom_frame(self, buttons):
        sep = ttk.Separator(self.root, orient="horizontal")
        sep.pack(fill="x")
        frame = tk.Frame(self.root, pady=10)
        frame.pack(fill="x")
        for idx, (text, cmd) in enumerate(buttons):
            tk.Button(frame, text=text, command=cmd, width=10, **self.button_style).pack(side="right", padx=(5 if idx != 0 else 20))

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.file_path = path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, path)

    def select_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir = path
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def run_extraction(self):
        self.file_path = self.file_entry.get()
        self.output_dir = self.output_entry.get()

        if not self.file_path:
            messagebox.showwarning("Warning", "You must select PDF file first.")
            return
        try:
            base, count, _ = extract_questions_with_answer(self.file_path, self.output_dir)
            title = os.path.basename(self.file_path)
            pdf_path = txt_to_pdf_unicode(
                base,
                output_dir=self.output_dir,
                show_answer=self.answer_var.get(),
                answer_transparent=(self.transparent_var.get() == "transparent"),
                title=title
            )
            message = f"Extraction complete!\nTotal extracted questions: {count}개\nPDF location: {pdf_path}"
            messagebox.showinfo("Extraction result", message)
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def confirm_exit(self):
        if messagebox.askyesno("Exit Confirmation", "Do you really want to close the application?"):
            self.root.destroy()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("640x460")
    
    # Position in the center of the screen
    window_width = 640
    window_height = 460
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    app = DumpExtractorApp(root)
    root.mainloop()
