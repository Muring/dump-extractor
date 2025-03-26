import os
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
from tkinter import Tk, filedialog, messagebox

font_path = "C:\\Windows\\Fonts\\malgun.ttf"  # 맑은 고딕

class PDFWithAnswerHint(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("Custom", "", font_path, uni=True)
        self.set_font("Custom", size=12)
        self.set_text_color(0, 0, 0)

    def add_question_text(self, question_text):
        lines = question_text.strip().split('\n')
        for line in lines:
            stripped = line.strip()
            if re.match(r'NO\.\d+', stripped, re.IGNORECASE):
                self.set_font("Custom", size=13)
                self.multi_cell(0, 10, stripped)
                self.set_font("Custom", size=12)
            elif stripped.startswith("Answer:"):
                self.set_text_color(240, 240, 240)
                self.multi_cell(0, 10, stripped)
                self.set_text_color(0, 0, 0)
            else:
                self.multi_cell(0, 10, stripped)
        self.ln(5)

def extract_and_clean_questions(pdf_path):
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = f"{base_name}_cleaned.txt"
    output_path = os.path.join(os.getcwd(), output_filename)

    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()

    questions = re.findall(r"(NO\.\d+.*?Answer:.*?)(?:Explanation:|\nNO\.|\Z)", full_text, re.DOTALL)

    def clean_line_breaks(text):
        return re.sub(r'(?<!\n)(?<![A-D]\.)\n(?![A-D]\.|Answer:)', ' ', text)

    cleaned = [clean_line_breaks(re.sub(r'\n+', '\n', q)).strip() for q in questions]

    with open(output_path, "w", encoding="utf-8") as f:
        for q in cleaned:
            f.write(q + "\n\n")

    return base_name

def txt_to_pdf(base_name):
    txt_path = os.path.join(os.getcwd(), f"{base_name}_cleaned.txt")
    pdf_path = os.path.join(os.getcwd(), f"{base_name}_cleaned.pdf")

    pdf = PDFWithAnswerHint()

    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        questions = content.split('\n\n')
        for q in questions:
            pdf.add_question_text(q)

    pdf.output(pdf_path)
    return pdf_path

# 전체 실행
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Tk 창 숨기기

    try:
        file_path = filedialog.askopenfilename(
            title="PDF 파일을 선택하세요",
            filetypes=[("PDF files", "*.pdf")]
        )

        if file_path:
            base = extract_and_clean_questions(file_path)
            pdf_result = txt_to_pdf(base)
            messagebox.showinfo("완료", f"✅ 변환 완료!\n\n📄 생성 파일:\n{pdf_result}")
        else:
            messagebox.showwarning("취소됨", "❗ 파일이 선택되지 않았습니다.")
    except Exception as e:
        messagebox.showerror("오류 발생", f"🚫 오류가 발생했습니다:\n{str(e)}")
