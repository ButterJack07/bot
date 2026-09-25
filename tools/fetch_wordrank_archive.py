import html
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUTPUT = BASE / "data" / "wordrank_archive_1_100.txt"


def fetch(issue):
    url = f"https://wordrank.net/zh/daily/{issue}"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        text = html.unescape(response.read().decode("utf-8", errors="ignore"))
    text = re.sub(
        r"已揭晓答案.*?<span[^>]*>答案</span>.*?<span[^>]*>([\u4e00-\u9fff]{2,})</span>",
        r"已揭晓答案 答案 \1",
        text,
        flags=re.S,
    )
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    patterns = (
        r"已揭晓答案\s+答案\s+([\u4e00-\u9fff]{2,})",
        r"答案分隔线\s+前方是答案\s+答案\s+([\u4e00-\u9fff]{2,})",
        r"正确答案\s*(?:是|为)\s*[：:]\s*([\u4e00-\u9fff]{2,})",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match and match.group(1) not in {"是", "为", "有多近", "多少接近"}:
            return match.group(1), url
    return None, url


def main():
    rows = []
    failures = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {pool.submit(fetch, issue): issue for issue in range(1, 101)}
        for future in as_completed(futures):
            issue = futures[future]
            try:
                answer, url = future.result()
                if answer:
                    rows.append((issue, f"第{issue}期\t{answer}\t{url}"))
                    print(f"{issue}: {answer}")
                else:
                    failures.append(issue)
                    print(f"{issue}: NOT FOUND")
            except Exception as error:
                failures.append(issue)
                print(f"{issue}: ERROR {error}")
    rows.sort()
    rows = [row for _, row in rows]
    OUTPUT.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"saved={OUTPUT} found={len(rows)} missing={len(failures)}")
    if failures:
        print("missing=" + ",".join(map(str, failures)))


if __name__ == "__main__":
    main()
