from flask import Flask, render_template, request
from deep_translator import GoogleTranslator
from indic_transliteration.sanscript import transliterate, DEVANAGARI, TAMIL

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    translated_text = ""

    if request.method == "POST":
        english_text = request.form.get("english_text", "").strip()
        engine = request.form.get("engine")

        if english_text:
            try:
                if engine == "deep_translator":
                    translated_text = GoogleTranslator(source="en", target="ta").translate(english_text)

                elif engine == "tamil_script_convert":
                    translated_text = transliterate(english_text, DEVANAGARI, TAMIL)

                else:
                    translated_text = "Invalid engine or engine not supported in Python 3.13!"

            except Exception as e:
                translated_text = f"Error: {str(e)}"

    return render_template("index.html", translated_text=translated_text)

if __name__ == "__main__":
    app.run(debug=True)
