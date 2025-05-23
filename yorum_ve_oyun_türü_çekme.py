import requests
import csv
import time
from datetime import datetime, timezone

# === Ayarlanabilir sabitler ===
MAX_REVIEWS = 10000
SLEEP_TIME = 1.2
APP_ID = 2138710

def get_game_details(app_id):
    """Steam'den oyun bilgilerini çeker: isim, tür, çıkış tarihi."""
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Oyun bilgisi alınamadı: {e}")
        return {}

    entry = data.get(str(app_id), {})
    if not entry.get("success"):
        print("Oyun bilgisi alınamadı: Veri eksik")
        return {}

    game_data = entry.get("data", {})
    return {
        "name": game_data.get("name", "Bilinmiyor"),
        "genres": [g["description"] for g in game_data.get("genres", [])],
        "release_date": game_data.get("release_date", {}).get("date", "Bilinmiyor")
    }

def get_reviews(app_id, max_reviews=MAX_REVIEWS):
    """Steam'den yorumları çeker (tüm dillerde)."""
    all_reviews = []
    cursor = "*"
    total = 0

    while total < max_reviews:
        try:
            response = requests.get(
                f"https://store.steampowered.com/appreviews/{app_id}",
                params={
                    "json": 1,
                    "filter": "recent",
                    "language": "all",
                    "day_range": 9223372036854775807,
                    "cursor": cursor,
                    "num_per_page": 100
                }
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Yorum verisi alınamadı: {e}")
            break

        reviews = data.get("reviews", [])
        if not reviews:
            print("Yorum kalmadı veya Steam limiti geldi.")
            break

        cursor = data.get("cursor", cursor)

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
        time.sleep(SLEEP_TIME)

    return all_reviews[:max_reviews]

def save_to_csv(reviews, game_info, filename="steam_reviews.csv"):
    """Yorumları ve oyun bilgilerini CSV dosyasına kaydeder."""
    if not reviews:
        print("Kaydedilecek yorum bulunamadı.")
        return

    with open(filename, "w", encoding="utf-8", newline="") as f:
        # Oyun bilgisi açıklaması
        f.write("# GAME INFORMATION\n")
        f.write(f"# Name: {game_info['name']}\n")
        f.write(f"# Genres: {', '.join(game_info['genres'])}\n")
        f.write(f"# Release Date: {game_info['release_date']}\n")
        f.write("#\n# REVIEWS\n")

        # CSV Yorumlar
        writer = csv.DictWriter(f, fieldnames=reviews[0].keys())
        writer.writeheader()
        writer.writerows(reviews)

    print(f"{len(reviews)} yorum başarıyla kaydedildi: {filename}")

# === Ana akış ===

if __name__ == "__main__":
    game_info = get_game_details(APP_ID)
    if not game_info:
        exit("Oyun bilgileri alınamadı, çıkılıyor.")

    print(f"Oyun: {game_info['name']}")
    print(f"Türler: {', '.join(game_info['genres'])}")
    print(f"Çıkış: {game_info['release_date']}")

    reviews = get_reviews(APP_ID)
    save_to_csv(reviews, game_info, filename="Sifu_yorumlar.csv")
