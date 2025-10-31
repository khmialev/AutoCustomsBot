import json

import requests

headers = {
    "sec-ch-ua-full-version-list": '"Chromium";v="142.0.7444.60", "Google Chrome";v="142.0.7444.60", "Not_A Brand";v="99.0.0.0"',
    "sec-ch-ua-platform": '"macOS"',
    "Referer": "https://bid.cars/ru/search/results?search-type=filters&status=All&type=Automobile&make=All&model=All&year-from=1900&year-to=2026&auction-type=All",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-model": '""',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-arch": '"arm"',
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-full-version": '"142.0.7444.60"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "sec-ch-ua-platform-version": '"15.7.1"',
}

response = requests.get(
    "https://bid.cars/app/search/toolbar-type/automobile", headers=headers
)
data = response.json()
result = {}

for item in data:
    make = item.get("make")
    model = item.get("model")
    generations = item.get("generations", [])

    if not make or not model or not generations:
        continue

    for gen in generations:
        if not isinstance(gen, dict):
            continue

        name = gen.get("name")
        min_year = gen.get("min_year")
        max_year = gen.get("max_year")

        if min_year and max_year:
            years = f"{min_year}–{max_year}"
        elif min_year:
            years = str(min_year)
        else:
            years = None

        result.setdefault(make, {}).setdefault(model, []).append(
            {"name": name, "years": years}
        )

with open("../cars_structured.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
