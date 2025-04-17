import pdfplumber
import re
from pathlib import Path

def extract_text_from_pdf(pdf_path: str) -> str:
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except Exception as e:
        print(f"❌ Ошибка при обработке файла {pdf_path.name}: {e}")
        return ""
    return full_text

def clear_text(text: str) -> str:
    # --- 1. Поиск и обработка 'keyword(s)' / 'key word(s)'
    pattern_keywords = re.compile(r".*?key\s?word[s]?.*?\r?\n", re.IGNORECASE | re.DOTALL)
    text_after_keywords = pattern_keywords.sub("", text, count=1)
    if text_after_keywords != text:
        pattern_until_cyrillic = re.compile(r"^[^а-яА-Я]+", re.DOTALL)
        text = pattern_until_cyrillic.sub("", text_after_keywords)
    else:
        # --- 2. Поиск 'введение' и удаление до него (оставляя строку)
        match_intro = re.search(r"введение", text, re.IGNORECASE)
        if match_intro:
            text = text[match_intro.start():]
        else:
            # --- 3. Поиск 'ключевые слова' и удаление до и включая строку
            pattern_keywords_ru = re.compile(r".*?ключевые\s+слова.*?\r?\n", re.IGNORECASE | re.DOTALL)
            text_after_kw_ru = pattern_keywords_ru.sub("", text, count=1)
            if text_after_kw_ru != text:
                text = text_after_kw_ru

    # --- 4. Удаление конца по последнему вхождению списка литературы
    end_patterns = [
        r"список\s+литературы",
        r"библиографический\s+список",
        r"список\s+источников"
    ]
    combined_pattern = re.compile("|".join(end_patterns), re.IGNORECASE)

    matches = list(combined_pattern.finditer(text))
    if matches:
        last_match = matches[-1]
        start_of_line = text.rfind('\n', 0, last_match.start())
        if start_of_line == -1:
            start_of_line = 0
        text = text[:start_of_line].rstrip()

    return text

def main():
    pdf_dir = Path("PDFs")
    if not pdf_dir.exists():
        print("❌ Папка 'PDFs' не найдена.")
        return

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print("❌ В папке 'PDFs' нет PDF-файлов.")
        return

    for pdf_path in pdf_files:
        print(f"\n📄 Обработка файла: {pdf_path.name}")
        try:
            text = extract_text_from_pdf(str(pdf_path))
            if not text.strip():
                print("⚠️ Пустой текст после извлечения.")
                continue

            cleared_text = clear_text(text)
            print("✅ Предобработка завершена. Пример вывода:")
            print("-" * 40)
            print(cleared_text[:50])
            print("-" * 40)

        except Exception as e:
            print(f"❌ Ошибка при обработке {pdf_path.name}: {e}")

if __name__ == "__main__":
    main()
