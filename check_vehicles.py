import requests
import json

# Get all vehicles
response = requests.get('http://172.31.3.209:8000/vehicles-with-details')
vehicles = response.json()

print(f"Total vehicles: {len(vehicles)}")
print("\nAll vehicles:")
for v in vehicles:
    brand = v['brands']['brand']
    model = v['models']['model']
    year = v['model_year']
    plates = [p['plate'] for p in v['plates']] if v['plates'] else []
    colors = [c['color'] for c in v['colors']] if v['colors'] else []

    print(f"  ID: {v['id']}")
    print(f"  {brand} {model} {year}")
    print(f"  Plates: {', '.join(plates) if plates else 'None'}")
    print(f"  Colors: {', '.join(colors) if colors else 'None'}")
    print()
