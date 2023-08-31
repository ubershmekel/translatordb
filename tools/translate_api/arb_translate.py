import os
import json

import api_task
import md_gen

arb_en = r'C:\dev\2023\youarethetranslator\yout\lib\src\localization\app_en.arb'
arb_dir = os.path.dirname(arb_en)

def main():
    en_data = json.load(open(arb_en, encoding='utf8'))
    en_number_key_line = []
    for key, line in en_data.items():
        if key.startswith('@'):
            continue
        if type(line) != str:
            print(f"Skipping {key} because it's not a string")
            continue
        en_number_key_line.append((len(en_number_key_line), key, line))

    en_lines = [i[2] for i in en_number_key_line]
    print(f"enlines: {en_lines}")
    for c3, c2 in md_gen.lang_code_3to2.items():
        print(f"Translating {c3}...")
        if c3 == "eng":
            continue
        translated_lines = api_task.translate(en_lines, c2)
        fname = f'{arb_dir}/app_{c2}.arb'
        new_data = en_data.copy()
        for i, key, line in en_number_key_line:
            new_data[key] = translated_lines[i]
        open(fname, 'w', encoding='utf8').write(json.dumps(new_data, indent=2, ensure_ascii=False))

main()