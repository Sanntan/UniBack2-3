# scripts/import_articles_from_csv.py

import sys
from pathlib import Path
import pandas as pd

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

from database.config import SessionLocal
from database.models import Article
from sqlalchemy.exc import SQLAlchemyError

# Путь к файлу CSV
CSV_PATH = "TestData/articles_and_authors.csv"


def import_articles():
    try:
        df = pd.read_csv(CSV_PATH, sep="|")
    except Exception as e:
        print(f"Ошибка при чтении CSV: {e}")
        return

    db = SessionLocal()
    count = 0

    try:
        for _, row in df.iterrows():
            title = str(row.get("Title", "")).strip()
            authors = str(row.get("Authors", "")).strip()
            pdf_link = str(row.get("PDF", "")).strip()
            abstract = str(row.get("Abstract", "")).strip()

            if not title:
                continue  # Пропускаем записи без заголовка

            article = Article(
                title=title,
                authors=authors,
                content=abstract,
                article_url=pdf_link
            )

            db.add(article)
            count += 1

        db.commit()
        print(f"✅ Импортировано {count} статей.")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Ошибка при добавлении в базу: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import_articles()
