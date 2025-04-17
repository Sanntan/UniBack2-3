import os
import csv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from typing import List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/pdf',
}


def download_pdf(url: str, save_path: str, index: int) -> bool:
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=15)
        content_type = response.headers.get("Content-Type", "")

        if "application/pdf" not in content_type:
            print(f"[!] Not a PDF ({index}): {url}")
            return False

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"[!] Failed ({index}): {url} — {e}")
        return False


def process_csv(csv_path: str, download_dir: str, max_files: int = None, max_workers: int = 10):
    os.makedirs(download_dir, exist_ok=True)

    urls = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        for row in reader:
            url = row.get("PDF")
            if url:
                urls.append(url.strip())

    if max_files:
        urls = urls[:max_files]

    print(f"[i] Preparing to download {len(urls)} file(s)...")

    def task(index_url):
        index, url = index_url
        filename = f"{index + 1}.pdf"  # Нумерация с 1
        save_path = os.path.join(download_dir, filename)
        success = download_pdf(url, save_path, index + 1)
        sleep(0.1)
        return success

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(task, (idx, url)) for idx, url in enumerate(urls)]
        completed = 0
        for future in as_completed(futures):
            if future.result():
                completed += 1

    print(f"\n[✓] Finished. {completed} file(s) successfully downloaded.")


def main():
    # Здесь задаем переменные
    csv_path = r"E:\PyCharm\additional\articles_3694.csv"
    download_dir = r"E:\PyCharm\additional\downloads"
    max_files = None  # Поставь None, чтобы скачать все
    max_workers = 50  # Количество параллельных потоков

    process_csv(csv_path, download_dir, max_files, max_workers)


if __name__ == "__main__":
    main()
