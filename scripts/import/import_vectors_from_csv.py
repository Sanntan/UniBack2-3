import sys
from pathlib import Path
import pandas as pd

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from database.config import SessionLocal
from database.models import ArticleVector
from sqlalchemy.exc import SQLAlchemyError

# Путь к файлу CSV
CSV_PATH = "TestData/all_embeddings.csv"

def parse_vector_string(vector_str):
    # Убираем возможные скобки и пробелы
    vector_str = vector_str.strip().replace("[", "").replace("]", "")
    # Разбиваем по запятым и преобразуем в список float
    return [float(x.strip()) for x in vector_str.split(",")]

def import_vectors_bulk():
    try:
        df = pd.read_csv(CSV_PATH, skiprows=1, header=None)
    except Exception as e:
        print(f"Ошибка при чтении CSV: {e}")
        return

    db = SessionLocal()
    article_vectors = []

    try:
        for idx, row in df.iterrows():
            vector_raw = str(row.values[0])
            vector_list = parse_vector_string(vector_raw)

            article_vectors.append(ArticleVector(
                article_id=idx + 1,
                vector_data=vector_list
            ))

        if article_vectors:
            db.bulk_save_objects(article_vectors)
            db.commit()
            print(f"✅ Успешно импортировано {len(article_vectors)} векторов в базу.")
        else:
            print("⚠️ Нет векторов для вставки.")

    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Ошибка при добавлении в базу: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_vectors_bulk()
