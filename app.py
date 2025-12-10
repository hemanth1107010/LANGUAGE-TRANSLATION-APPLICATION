import sys
import os
import fitz        # PyMuPDF for PDF reading
import pytesseract
from PIL import Image
import docx
from deep_translator import GoogleTranslator
from indic_transliteration.sanscript import transliterate, DEVANAGARI, TAMIL

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QTextEdit, QFileDialog, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt


# ----------------------- FILE READING HELPERS -----------------------

def read_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_docx(path):
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def read_pdf(path):
    text = ""
    pdf = fitz.open(path)
    for page in pdf:
        text += page.get_text()
    return text


def read_image(path):
    img = Image.open(path)
    return pytesseract.image_to_string(img)


# ----------------------- MAIN APP -----------------------

class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("English → Tamil Translator")
        self.setGeometry(200, 200, 700, 500)

        layout = QVBoxLayout()

        self.label = QLabel("Select Translation Engine:")
        layout.addWidget(self.label)

        self.engine_selector = QComboBox()
        self.engine_selector.addItems([
            "deep_translator",
            "tamil_script_convert"
        ])
        layout.addWidget(self.engine_selector)

        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Enter or upload English text...")
        layout.addWidget(self.input_box)

        self.upload_btn = QPushButton("Upload File")
        self.upload_btn.clicked.connect(self.open_file)
        layout.addWidget(self.upload_btn)

        self.translate_btn = QPushButton("Translate")
        self.translate_btn.clicked.connect(self.translate_text)
        layout.addWidget(self.translate_btn)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        layout.addWidget(self.output_box)

        self.setLayout(layout)

    # ------------------ File Upload Logic ------------------
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose File",
            "",
            "All Supported (*.txt *.docx *.pdf *.png *.jpg *.jpeg);;"
            "Text Files (*.txt);;Word Files (*.docx);;PDF Files (*.pdf);;Images (*.png *.jpg *.jpeg)"
        )

        if not file_path:
            return

        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext == ".txt":
                text = read_txt(file_path)
            elif ext == ".docx":
                text = read_docx(file_path)
            elif ext == ".pdf":
                text = read_pdf(file_path)
            elif ext in [".png", ".jpg", ".jpeg"]:
                text = read_image(file_path)
            else:
                QMessageBox.warning(self, "Unsupported", "This file type is not supported.")
                return

            self.input_box.setPlainText(text)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file:\n{str(e)}")

    # ------------------ Translation Logic ------------------
    def translate_text(self):
        english_text = self.input_box.toPlainText().strip()
        engine = self.engine_selector.currentText()

        if not english_text:
            QMessageBox.warning(self, "Empty", "Please enter or upload text.")
            return

        try:
            if engine == "deep_translator":
                translated = GoogleTranslator(source="en", target="ta").translate(english_text)

            elif engine == "tamil_script_convert":
                # Convert English → Devanagari → Tamil script
                dev = transliterate(english_text, "iast", DEVANAGARI)
                translated = transliterate(dev, DEVANAGARI, TAMIL)

            else:
                translated = "Invalid translation engine selected."

            self.output_box.setPlainText(translated)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Translation failed:\n{str(e)}")


# ----------------------- RUN APP -----------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    translator = TranslatorApp()
    translator.show()
    sys.exit(app.exec())
