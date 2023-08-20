from typing import List

output_langs = (
    "eng",
    "ara",
    "deu",
    "ell",
    "fra",
    "heb",
    "ita",
    "jpn",
    "kor",
    "por",
    "rus",
    "spa",
)

def generate_md(lang_to_examples):
    md_lines = []
    for lang in output_langs:
        if lang not in lang_to_examples:
            # we only want to use complete entries
            # print(f"missing lang {lang}")
            # return
            continue
        md_lines.append(f"# lang:{lang}")
        for sentence in sorted(dedupe_sentences(lang_to_examples[lang])):
            md_lines.append(sentence)
    
    md_text = '\n\n'.join(md_lines)
    return md_text

def to_md_name(name: str) -> str:
    return "".join(x for x in name.lower() if x.isalnum()) + ".md"


def dedupe_sentences(sentences: List[str]):
    deduped = {}
    for sent in sentences:
        deduped[to_md_name(sent)] = sent
    return list(deduped.values())