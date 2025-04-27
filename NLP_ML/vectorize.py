import pdfplumber
import re
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import numpy as np
import os
import csv
import faiss
import torch


def extract_text_from_pdf(pdf_path: str) -> str:

    full_text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
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
            # иначе ничего не найдено, текст остаётся как есть

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
            # если нет переноса — от начала текста
            start_of_line = 0
        text = text[:start_of_line].rstrip()

    return text


def text_to_paragraphs(text: str):
    text = text.replace('', '')
    text = re.sub(r'-\s*\n\s*', '', text)
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)

    parts = re.split(r'(?<=\.)\s*\n+', text)
    cleaned_paragraphs = []

    for p in parts:
        p = re.sub(r'(?m)^\s*.{1,4}\s*$\n?', '', p)
        p = re.sub(r'(?m)^\s*(Рис\.|Источник:).*\n?', '', p)
        p = re.sub(r'\s*\n\s*', ' ', p).strip()
        if p:
            cleaned_paragraphs.append(p)

    merged = []
    for para in cleaned_paragraphs:
        if merged and para and para[0].islower():
            merged[-1] += ' ' + para
        else:
            merged.append(para)

    return merged


def split_sentences(paragraphs):
    sentences = []

    # Часто встречающиеся аббревиатуры, которые не считаются концом предложения
    abbreviations = [
        r'т\.д\.', r'т\.п\.', r'и\.д\.', r'и\.т\.д\.', r'и\.т\.п\.', r'и\.др\.',
        r'т\.е\.', r'т\.н\.', r'напр\.', r'г\.', r'ул\.', r'д\.',
        r'e\.g\.', r'i\.e\.', r'U\.S\.', r'Mr\.', r'Mrs\.', r'Dr\.'
    ]
    abbrev_pattern = '|'.join(abbreviations)

    for paragraph in paragraphs:
        # Защита аббревиатур временной меткой
        safe_text = re.sub(f'({abbrev_pattern})', lambda m: m.group(1).replace('.', '§'), paragraph)

        # Разбивка по .!? + пробел + заглавная буква
        split_parts = re.split(r'(?<=[.!?])\s+(?=[А-ЯA-Z])', safe_text)

        # Восстанавливаем точки в аббревиатурах и чистим
        for part in split_parts:
            restored = part.replace('§', '.').strip()
            if restored:
                sentences.append(restored)

    return sentences


def group_sentences_by_char_limit(sentences, limit=600):
    grouped = []
    current_group = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        if current_length + sentence_length <= limit:
            current_group.append(sentence)
            current_length += sentence_length
        else:
            if current_group:
                grouped.append(' '.join(current_group))
            current_group = [sentence]
            current_length = sentence_length

    if current_group:
        grouped.append(' '.join(current_group))

    return grouped


def vectorize_paragraphs(paragraphs, model, tokenizer, max_tokens=512, batch_size=64):
    device = model.device
    filtered_paragraphs = []

    for i, paragraph in enumerate(paragraphs):
        tokens = tokenizer.encode(paragraph, add_special_tokens=True)
        token_len = len(tokens)

        if token_len <= max_tokens:
            filtered_paragraphs.append(paragraph)
        else:
            print(f"⚠️ Абзац {i + 1} содержит {token_len} токенов и будет усечён до 512.")
            truncated = tokenizer.decode(tokens[:max_tokens], skip_special_tokens=True)
            filtered_paragraphs.append(truncated)

    if not filtered_paragraphs:
        return np.zeros(model.get_sentence_embedding_dimension())

    embeddings = model.encode(
        filtered_paragraphs,
        show_progress_bar=True,
        convert_to_numpy=True,
        device=device,
        batch_size=batch_size
    )

    doc_embedding = np.mean(embeddings, axis=0)
    return doc_embedding



def find_most_similar(embeddings_list, filenames, top_k=5, max_outputs=5):

    embeddings_np = np.stack(embeddings_list).astype("float32")
    index = faiss.IndexFlatL2(embeddings_np.shape[1])
    index.add(embeddings_np)

    def print_results(base_idx, distances, indices):
        print(f"\n🔍 Похожие на файл: {filenames[base_idx]}")
        printed = 0
        for i, dist in zip(indices, distances):
            if i == base_idx:
                continue  # Пропускаем сам себя
            printed += 1
            print(f"{printed}. {filenames[i]} — расстояние: {dist:.4f}")
            if printed >= top_k:
                break

    for i in range(min(len(embeddings_list), max_outputs)):
        distances, indices = index.search(embeddings_np[i:i+1], top_k + 1)
        print_results(i, distances[0], indices[0])



def export_articles_to_txt(text, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for paragraph in text:
            f.write(paragraph.strip() + '\n\n')


def export_embeddings_to_csv(embeddings_list, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['embedding'])
        for emb in embeddings_list:
            writer.writerow([', '.join(map(str, emb))])


def main(max_files=None):
    pdf_folder = "downloads/pdfs"
    output_csv = "all_embeddings.csv"

    embeddings_list = []
    filenames = []

    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"\n🧠 Загрузка модели на {device.upper()}...")
    model = SentenceTransformer(model_name)
    model.to(torch.device(device))
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    pdf_files = [
        f for f in os.listdir(pdf_folder)
        if f.lower().endswith('.pdf') and os.path.splitext(f)[0].isdigit()
    ]
    pdf_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

    if max_files is not None:
        pdf_files = pdf_files[:max_files]

    for filename in pdf_files:
        file_path = os.path.join(pdf_folder, filename)
        print(f"\n📄 Обработка файла: {filename}")

        text = extract_text_from_pdf(file_path)
        if not text.strip():
            print(f"⚠️ Пропущен файл (нет текста): {filename}")
            continue

        cleared_text = clear_text(text)
        paragraphs = text_to_paragraphs(cleared_text)
        sentences = split_sentences(paragraphs)
        grouped = group_sentences_by_char_limit(sentences)
        doc_embedding = vectorize_paragraphs(grouped, model, tokenizer)

        embeddings_list.append(doc_embedding)
        filenames.append(filename)

    if embeddings_list:
        export_embeddings_to_csv(embeddings_list, output_csv)
        print(f"\n✅ Все эмбеддинги сохранены в {output_csv}")

        # Выводим наиболее похожие документы
        find_most_similar(embeddings_list, filenames, top_k=5)
    else:
        print("❌ Не удалось получить ни одного эмбеддинга.")



if __name__ == "__main__":
    main(max_files = 1000)
