import pdfplumber
import os
import re
from pathlib import Path
from datetime import datetime
import sys
from typing import List, Optional

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from database.config import get_db
from database.models import Article
from sqlalchemy.orm import Session


def get_project_root() -> Path:
    """Возвращает абсолютный путь к корню проекта"""
    return Path(__file__).parent.parent


def extract_article_data_from_pdf(file_path: str) -> dict:
    """
    Извлекает метаданные статьи из PDF файла.

    Args:
        file_path: Путь к PDF файлу

    Returns:
        Словарь с данными статьи: {'title', 'authors', 'content'}
    """
    pattern_fio = r"[А-ЯЁ]\.[А-ЯЁ]\.\s?[А-ЯЁ][а-яё]+"
    pattern_title = r"[А-ЯЁA-Z][А-ЯЁA-Z0-9\s,.-:;!?()]+"

    with pdfplumber.open(file_path) as pdf:
        # Извлекаем текст со всех страниц
        full_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"

        # Очищаем текст
        lines = full_text.split("\n")
        lines = [line.strip() for line in lines if line.strip()]
        text_cleaned = " ".join(lines)
        text_cleaned = re.sub(r"\s+", " ", text_cleaned)

        # Поиск авторов
        authors_match = re.findall(pattern_fio, text_cleaned)
        authors = ", ".join(authors_match) if authors_match else ""

        # Удалим авторов из текста, чтобы не мешали заголовку
        text_wo_authors = text_cleaned
        for match in authors_match:
            text_wo_authors = text_wo_authors.replace(match, "")

        # Поиск названия — берём первую длинную капс-строку
        title_match = re.findall(pattern_title, text_wo_authors)
        title = ""
        for m in title_match:
            if len(m.replace(" ", "")) > 20:  # простая эвристика для заголовков
                title = m
                break

        return {
            'title': title,
            'authors': authors,
            'content': full_text,
            'article_url': f"file://{str(Path(file_path).absolute())}"  # Добавляем ссылку на файл
        }


def process_pdfs_to_db(pdf_folder: Path, db: Session, batch_size: int = 10) -> None:
    """
    Обрабатывает все PDF в папке и сохраняет их в базу данных.

    Args:
        pdf_folder: Путь к папке с PDF файлами (Path объект)
        db: Сессия SQLAlchemy
        batch_size: Размер батча для групповой вставки
    """
    processed_files = 0
    skipped_files = 0
    batch = []

    for filename in os.listdir(pdf_folder):
        if not filename.endswith(".pdf"):
            continue

        file_path = pdf_folder / filename
        print(f"Обработка файла: {filename}")

        try:
            article_data = extract_article_data_from_pdf(file_path)

            if not article_data['title']:
                print(f"Не удалось извлечь заголовок из файла {filename}, пропускаем")
                skipped_files += 1
                continue

            # Проверяем, существует ли уже статья с таким заголовком
            existing_article = db.query(Article).filter(
                Article.title == article_data['title']
            ).first()

            if existing_article:
                print(f"Статья с заголовком '{article_data['title']}' уже существует, пропускаем")
                skipped_files += 1
                continue

            # Создаем объект статьи для добавления в базу
            new_article = Article(
                title=article_data['title'],
                authors=article_data['authors'],
                content=article_data['content'],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            batch.append(new_article)
            processed_files += 1

            # Если набрали батч, сохраняем
            if len(batch) >= batch_size:
                db.bulk_save_objects(batch)
                db.commit()
                batch = []
                print(f"Сохранено {batch_size} статей в базу данных")

        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {str(e)}")
            skipped_files += 1

    # Сохраняем оставшиеся статьи в батче
    if batch:
        db.bulk_save_objects(batch)
        db.commit()
        print(f"Сохранено {len(batch)} статей в базу данных")

    print(f"\nОбработка завершена. Обработано файлов: {processed_files}, пропущено: {skipped_files}")


if __name__ == "__main__":
    # Определяем путь к папке TestData в корне проекта
    pdf_folder = get_project_root() / "TestData"

    if not pdf_folder.exists():
        print(f"Папка {pdf_folder} не существует! Создайте папку TestData в корне проекта.")
        exit(1)

    if not any(file.endswith('.pdf') for file in os.listdir(pdf_folder)):
        print(f"В папке {pdf_folder} не найдено PDF файлов!")
        exit(1)

    # Подключаемся к базе данных
    db = next(get_db())

    try:
        print(f"Начата обработка PDF из папки: {pdf_folder}")
        process_pdfs_to_db(pdf_folder, db)
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
    finally:
        db.close()