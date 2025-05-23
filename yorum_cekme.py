import requests
import csv
import time
from datetime import datetime, timezone

def get_reviews(app_id, max_reviews=10000):
    all_reviews = []
    cursor = "*"
    total = 0

    while total < max_reviews:
        url = f"https://store.steampowered.com/appreviews/{app_id}"
        params = {
            "json": 1,
            "filter": "recent",
            "language": "all",
            "day_range": 9223372036854775807,
            "cursor": cursor,
            "num_per_page": 100
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("Hata:", response.status_code)
            break

        data = response.json()
        reviews = data.get("reviews", [])
        cursor = data.get("cursor", cursor)

        if not reviews:
            print("Yorum kalmadı veya limit geldi.")
            break

        for review in reviews:
            author = review.get("author", {})
            all_reviews.append({
                "review_text": review.get("review", ""),
                "voted_up": review.get("voted_up", False),
                "playtime_forever_minutes": author.get("playtime_forever", 0),
                "playtime_at_review_minutes": author.get("playtime_at_review", 0),
                "timestamp_created": datetime.fromtimestamp(
                    review.get("timestamp_created", 0), tz=timezone.utc
                ).isoformat(),
                "review_url": f"https://steamcommunity.com/profiles/{author.get('steamid', '')}/recommended/{app_id}/"
            })

        total += len(reviews)
        print(f"Toplam çekilen yorum: {total}")
        time.sleep(1.2)  # Steam rate-limit

    return all_reviews[:max_reviews]

def save_to_csv(reviews, filename="Loop_hero_yorumlar.csv"):
    if not reviews:
        print("Yorum bulunamadı.")
        return

    keys = reviews[0].keys()
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(reviews)

    print(f"{len(reviews)} yorum kaydedildi: {filename}")

# oyun App ID
app_id = 1282730

# Yorumları çek
reviews = get_reviews(app_id, max_reviews=10000)

# Kaydet
save_to_csv(reviews)
