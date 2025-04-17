import sys
from pathlib import Path
import pandas as pd

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from database.config import SessionLocal
from database.models import Article, ArticleVector
from sqlalchemy.exc import SQLAlchemyError

# Путь к CSV-файлу
CSV_PATH = "TestData/articles_with_vectors.csv"

def parse_vector_string(vector_str):
    vector_str = vector_str.strip().replace("[", "").replace("]", "")
    return [float(x.strip()) for x in vector_str.split(",") if x.strip()]

def import_articles_and_vectors():
    try:
        df = pd.read_csv(CSV_PATH, sep="|")
    except Exception as e:
        print(f"Ошибка при чтении CSV: {e}")
        return

    db = SessionLocal()
    articles = []
    vectors = []

    START_ID = 1001  # начальный ID для новых записей

    try:
        for idx, row in df.iterrows():
            title = str(row.get("Title", "")).strip()
            authors = str(row.get("Authors", "")).strip()
            abstract = str(row.get("Abstract", "")).strip()
            pdf_link = str(row.get("PDF", "")).strip()
            vector_raw = str(row.get("Vector", "")).strip()

            if not title or not vector_raw:
                print(f"⚠️ Пропуск записи на строке {idx + 2}: нет Title или Vector")
                continue

            article_id = START_ID + idx

            article = Article(
                article_id=article_id,
                title=title,
                authors=authors,
                content=abstract,
                article_url=pdf_link
            )
            articles.append(article)

            vector_list = parse_vector_string(vector_raw)

            vector = ArticleVector(
                article_id=article_id,
                vector_data=vector_list
            )
            vectors.append(vector)

        # bulk сохранение
        if articles and vectors:
            db.bulk_save_objects(articles)
            db.bulk_save_objects(vectors)
            db.commit()
            print(f"✅ Успешно импортировано {len(articles)} статей и {len(vectors)} векторов.")
        else:
            print("⚠️ Нет данных для вставки.")

    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Ошибка при добавлении в базу: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_articles_and_vectors()
