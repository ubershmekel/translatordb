

import json

# From https://raw.githubusercontent.com/flyingcircusio/pycountry/main/src/pycountry/databases/iso639-3.json
raw_iso6393 = json.load(open('tools/iso639-3.json', encoding='utf8'))

out = {}
for row in raw_iso6393["639-3"]:
    # {
    #   "alpha_3": "jpa",
    #   "inverted_name": "Aramaic, Jewish Palestinian",
    #   "name": "Jewish Palestinian Aramaic",
    #   "scope": "I",
    #   "type": "H"
    # },
    # {
    #   "alpha_2": "ja",
    #   "alpha_3": "jpn",
    #   "name": "Japanese",
    #   "scope": "I",
    #   "type": "L"
    # },
    if "alpha_2" in row:
        code3 = row["alpha_3"]
        name = row["name"]
        code2 = row["alpha_2"]
        out[code3] = {
            "name": name,
            "code2": code2,
        }


print(f'len({len(raw_iso6393["639-3"])})')
print(f"len({len(out)})")

json.dump(out, open('tools/language-codes.json', 'w', encoding='utf8'), indent=2)
