import json

try:
    with open('Dictionary/definition.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(data)
except FileNotFoundError:
    print("File not found")
except json.JSONDecodeError:
    print("Error decoding JSON")