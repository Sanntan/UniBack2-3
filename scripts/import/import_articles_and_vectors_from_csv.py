import sys
from pathlib import Path
from tqdm import tqdm

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from database.config import SessionLocal
from database.models import Article, ArticleVector
from sqlalchemy.exc import SQLAlchemyError

# Путь к файлу
CSV_PATH = "TestData/articles_with_embeddings_cleaned.csv"

def parse_vector_string(vector_str):
    vector_str = vector_str.strip().replace("[", "").replace("]", "")
    return [float(x.strip()) for x in vector_str.split(",") if x.strip()]

def import_articles_and_vectors_from_raw():
    db = SessionLocal()
    articles = []
    vectors = []
    START_ID = 1001

    try:
        with open(CSV_PATH, encoding="utf-8") as f:
            lines = f.readlines()

        print(f"Найдено {len(lines)-1} строк для загрузки.")  # -1 чтобы исключить заголовок

        for idx, line in tqdm(enumerate(lines[1:]), total=len(lines)-1, desc="Импорт"):
            parts = line.strip().split("|", 4)  # максимум 5 частей

            if len(parts) != 5:
                print(f"⚠️ Пропущена строка {idx + 2}: неправильное количество полей ({len(parts)})")
                continue

            title, authors, abstract, pdf_link, vector_raw = parts

            if not title.strip() or not vector_raw.strip():
                print(f"⚠️ Пропуск пустой записи на строке {idx + 2}")
                continue

            article_id = START_ID + idx

            article = Article(
                article_id=article_id,
                title=title.strip(),
                authors=authors.strip(),
                content=abstract.strip(),
                article_url=pdf_link.strip()
            )
            articles.append(article)

            vector_list = parse_vector_string(vector_raw)

            vector = ArticleVector(
                article_id=article_id,
                vector_data=vector_list
            )
            vectors.append(vector)

        if articles and vectors:
            db.bulk_save_objects(articles)
            db.bulk_save_objects(vectors)
            db.commit()
            print(f"\n✅ Успешно импортировано {len(articles)} статей и {len(vectors)} векторов.")
        else:
            print("⚠️ Нет данных для вставки.")

    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Ошибка при добавлении в базу: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_articles_and_vectors_from_raw()
