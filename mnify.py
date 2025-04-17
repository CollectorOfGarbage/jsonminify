import json
import sys

def round_coord(coord, precision):
    return [round(c, precision) for c in coord]

def remove_consecutive_duplicates(ring, precision):
    cleaned = []
    prev = None
    removed = 0
    for coord in ring:
        rounded = round_coord(coord, precision)
        if rounded != prev:
            cleaned.append(rounded)
            prev = rounded
        else:
            removed += 1
    return cleaned, removed

def clean_geometry(geometry, precision):
    total_removed = 0

    if geometry["type"] == "Polygon":
        new_coords = []
        for ring in geometry["coordinates"]:
            cleaned, removed = remove_consecutive_duplicates(ring, precision)
            new_coords.append(cleaned)
            total_removed += removed
        geometry["coordinates"] = new_coords

    elif geometry["type"] == "MultiPolygon":
        new_coords = []
        for polygon in geometry["coordinates"]:
            new_polygon = []
            for ring in polygon:
                cleaned, removed = remove_consecutive_duplicates(ring, precision)
                new_polygon.append(cleaned)
                total_removed += removed
            new_coords.append(new_polygon)
        geometry["coordinates"] = new_coords

    return total_removed

def main(input_file, output_file, precision):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data["type"] != "FeatureCollection":
        print("❌ Only FeatureCollection is supported.")
        return

    cleaned_count = 0
    total_removed = 0

    for i, feature in enumerate(data["features"]):
        geom = feature.get("geometry")
        if geom and geom["type"] in ["Polygon", "MultiPolygon"]:
            removed = clean_geometry(geom, precision)
            if removed > 0:
                print(f"🔁 Feature {i}: {removed} consecutive duplicates removed")
            total_removed += removed
            cleaned_count += 1

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))

    print(f"\n✅ Cleaned {cleaned_count} geometries.")
    print(f"🧹 Total consecutive duplicates removed: {total_removed}")
    print(f"📁 Output saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python mnify.py input.geojson output.geojson precision")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    try:
        precision = int(sys.argv[3])
    except ValueError:
        print("Precision must be an integer.")
        sys.exit(1)

    main(input_path, output_path, precision)
