import json
import urllib.request
from datetime import datetime, timezone, timedelta
from django.shortcuts import render

BMKG_URL = "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json"


def _parse_depth_km(kedalaman_str):
    try:
        return float(kedalaman_str.lower().replace("km", "").strip())
    except (ValueError, AttributeError):
        return 0.0


def _depth_category(depth_km):
    if depth_km < 70:
        return "dangkal", "#d63031", "Dangkal"
    if depth_km <= 300:
        return "menengah", "#e67e22", "Menengah"
    return "dalam", "#27ae60", "Dalam"


def gempaterkini(request):
    gempa_list = []
    error_msg = None

    try:
        req = urllib.request.Request(
            BMKG_URL,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw_data = json.loads(resp.read().decode("utf-8"))

        items = raw_data.get("Infogempa", {}).get("gempa", [])[:15]
        for idx, item in enumerate(items, start=1):
            coords_str = item.get("Coordinates", "0,0")
            lat_str, lon_str = coords_str.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            mag = float(item.get("Magnitude", "0"))
            depth_km = _parse_depth_km(item.get("Kedalaman", "0 km"))
            cat, color, label = _depth_category(depth_km)

            gempa_list.append({
                "no": idx,
                "tanggal": item.get("Tanggal", ""),
                "jam": item.get("Jam", ""),
                "magnitude": item.get("Magnitude", ""),
                "mag_num": mag,
                "kedalaman": item.get("Kedalaman", ""),
                "depth_km": depth_km,
                "category": cat,
                "color": color,
                "depth_label": label,
                "wilayah": item.get("Wilayah", ""),
                "lintang": item.get("Lintang", ""),
                "bujur": item.get("Bujur", ""),
                "potensi": item.get("Potensi", ""),
                "lat": lat,
                "lon": lon,
            })
    except Exception as exc:
        error_msg = f"Gagal memuat data BMKG: {exc}"

    wib_now = datetime.now(timezone(timedelta(hours=7))).strftime("%H.%M.%S")
    return render(
        request,
        "gempabumi/gempaterkini.html",
        {
            "gempa_list": gempa_list,
            "gempa_json": json.dumps(gempa_list),
            "updated_at": wib_now,
            "error_msg": error_msg,
        },
    )
