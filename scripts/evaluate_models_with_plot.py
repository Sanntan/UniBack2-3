import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import tensorflow_hub as hub
from tqdm import tqdm

# =============================
# Настройки
# =============================

TOP_K = 10
SCIDOCS_PATH = "scidocs_sample.csv"
USE_MODEL_URL = "https://tfhub.dev/google/universal-sentence-encoder/4"

# =============================
# Метрики
# =============================

def precision_at_k(recommended, relevant, k):
    recommended_at_k = recommended[:k]
    return len(set(recommended_at_k) & set(relevant)) / k

def recall_at_k(recommended, relevant, k):
    recommended_at_k = recommended[:k]
    if not relevant:
        return 0.0
    return len(set(recommended_at_k) & set(relevant)) / len(relevant)

def ndcg_at_k(recommended, relevant, k):
    dcg = 0.0
    for i, item in enumerate(recommended[:k]):
        if item in relevant:
            dcg += 1 / np.log2(i + 2)
    idcg = sum(1 / np.log2(i + 2) for i in range(min(len(relevant), k)))
    return dcg / idcg if idcg > 0 else 0.0

# =============================
# Загрузка данных
# =============================

def load_data(path):
    df = pd.read_csv(path)
    texts = df["text"].tolist()
    labels = df["label"].tolist()
    label_to_indices = {}
    for idx, label in enumerate(labels):
        label_to_indices.setdefault(label, []).append(idx)
    return texts, labels, label_to_indices

# =============================
# Эмбеддинг моделей
# =============================

def embed_tfidf(texts):
    vectorizer = TfidfVectorizer(max_features=10000)
    embeddings = vectorizer.fit_transform(texts)
    return embeddings.toarray()

def embed_use(texts):
    model = hub.load(USE_MODEL_URL)
    embeddings = model(texts)
    return embeddings.numpy()

def embed_bert(texts):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    return embeddings

# =============================
# Оценка модели
# =============================

def evaluate_model(embeddings, labels, label_to_indices):
    sims = cosine_similarity(embeddings)
    precisions, recalls, ndcgs = [], [], []

    for idx in tqdm(range(len(embeddings)), desc="Evaluating"):
        indices = np.argsort(-sims[idx])
        indices = [i for i in indices if i != idx]

        recommended = indices
        relevant = [i for i in label_to_indices[labels[idx]] if i != idx]

        precisions.append(precision_at_k(recommended, relevant, TOP_K))
        recalls.append(recall_at_k(recommended, relevant, TOP_K))
        ndcgs.append(ndcg_at_k(recommended, relevant, TOP_K))

    return np.mean(precisions), np.mean(recalls), np.mean(ndcgs)

# =============================
# Построение графиков
# =============================

def plot_metrics(results):
    models = list(results.keys())
    precisions = [v['precision'] for v in results.values()]
    recalls = [v['recall'] for v in results.values()]
    ndcgs = [v['ndcg'] for v in results.values()]

    x = np.arange(len(models))

    plt.figure(figsize=(10, 6))

    plt.bar(x - 0.2, precisions, width=0.2, label='Precision@10')
    plt.bar(x, recalls, width=0.2, label='Recall@10')
    plt.bar(x + 0.2, ndcgs, width=0.2, label='NDCG@10')

    plt.xticks(x, models)
    plt.ylabel("Score")
    plt.title("Сравнение моделей на SciDocs Benchmark")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# =============================
# Основной запуск
# =============================

if __name__ == "__main__":
    texts, labels, label_to_indices = load_data(SCIDOCS_PATH)

    results = {}

    # TF-IDF
    print("\n[TF-IDF] Эмбеддинг...")
    tfidf_embeds = embed_tfidf(texts)
    print("[TF-IDF] Оценка...")
    p, r, ndcg = evaluate_model(tfidf_embeds, labels, label_to_indices)
    results["TF-IDF"] = {"precision": p, "recall": r, "ndcg": ndcg}

    # USE
    print("\n[USE] Эмбеддинг...")
    use_embeds = embed_use(texts)
    print("[USE] Оценка...")
    p, r, ndcg = evaluate_model(use_embeds, labels, label_to_indices)
    results["USE"] = {"precision": p, "recall": r, "ndcg": ndcg}

    # BERT
    print("\n[BERT] Эмбеддинг...")
    bert_embeds = embed_bert(texts)
    print("[BERT] Оценка...")
    p, r, ndcg = evaluate_model(bert_embeds, labels, label_to_indices)
    results["BERT"] = {"precision": p, "recall": r, "ndcg": ndcg}

    # Вывод результатов
    print("\n==== Результаты @10 ====")
    for model, scores in results.items():
        print(f"{model}: Precision={scores['precision']:.4f}, Recall={scores['recall']:.4f}, NDCG={scores['ndcg']:.4f}")

    # Рисуем графики
    plot_metrics(results)
