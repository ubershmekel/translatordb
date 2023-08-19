"""
links.csv - 356 MB
sentences.csv - 618 MB
sentences_base.csv - 158 MB but I don't understand what this file is

I guess I'll load sentences and links to memory, then start working
I wonder if that'll work

"""


# https://downloads.tatoeba.org/exports/links.tar.bz2
# 812375	128575
# 812375	268964


import json
from collections import Counter
from typing import List
import os

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

# https://en.wikipedia.org/wiki/List_of_most_commonly_learned_second_languages_in_the_United_States#Colleges_and_universities
# The order of output_langs determines the order in the md files.
# It starts with English, then it's alphabetical
# Removed "ara" because it's not as well translated on tatoeba
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

output_langs_set = set(output_langs)
eng_ids = set()
# langs_counter: Counter({'eng': 1812813, 'rus': 1003593, 'ita': 855218, 'deu': 620770, 'fra': 556854,
# 'por': 419678, 'spa': 396372, 'jpn': 237407, 'heb': 200759, 'ara': 57894, 'ell': 37832, 'kor': 11588})
langs_counter = Counter()

def load_sentences():
    id_to_lang_sentence = {}
    for line in open(script_dir + '/sentences.csv', encoding='utf8'):
        parts = [part.strip() for part in line.split('\t') if part.strip()]
        if len(parts) != 3:
            continue
        sid, lng, sentence = parts
        sid = int(sid)
        if lng not in output_langs_set:
            continue
        id_to_lang_sentence[sid] = (lng, sentence)
        langs_counter[lng] += 1
        if lng == "eng":
            eng_ids.add(sid)
    print(f"langs_counter: {langs_counter}")
    return id_to_lang_sentence

print("loading sentences")
id_to_lang_sentence = load_sentences()

def load_links():
    links = {}
    for line in open(script_dir + '/links.csv', encoding='utf8'):
        parts = [part.strip() for part in line.split('\t') if part.strip()]
        if len(parts) != 2:
            continue
        a, b = int(parts[0]), int(parts[1])
        if a in id_to_lang_sentence and b in id_to_lang_sentence:
            if a not in links:
                links[a] = []
            if b not in links:
                links[b] = []
            links[a].append(b)
            links[b].append(a)
    return links

print("loading links")
links = load_links()


def to_md_name(name: str) -> str:
    return "".join(x for x in name.lower() if x.isalnum()) + ".md"

# def generate_md(eng_id):

def values_len(di: dict) -> int:
    return sum(len(val) for val in di.values())

def gather_links(starting_sid: str, seen: set):
    # seen.add(sid)
    to_explore = [starting_sid]
    while to_explore:
        next_sid = to_explore.pop()
        seen.add(next_sid)
        for sublink in links[next_sid]:
            if sublink not in seen:
                to_explore.append(sublink)
        # if sublink not in seen:
        #     gather_links(sublink, seen)
    return seen

def dedupe_sentences(sentences: List[str]):
    deduped = {}
    for sent in sentences:
        deduped[to_md_name(sent)] = sent
    return list(deduped.values())

# md_names = []
# len eng_ids 1,812,813
print(f"len eng_ids {len(eng_ids)}")

def generate_examples(sid):
    lang, sentence = id_to_lang_sentence[sid]
    # if len(sentence) > 50:
    #     # longer sentences have many more variations
    #     return

    lang_to_examples = {}
    lang_to_examples[lang] = set([sentence])
    all_links = set()
    if sid not in links:
        # no translations of this sentence
        return
    for linked_sid in links[sid]:
        linked_lang, linked_sentence = id_to_lang_sentence[linked_sid]
        if linked_lang not in lang_to_examples:
            lang_to_examples[linked_lang] = set()
        lang_to_examples[linked_lang].add(linked_sentence)
        all_links.add(linked_sid)
        for sublink in links[linked_sid]:
            all_links.add(sublink)
    
    # print(f"sid: {sid}, sentence: {sentence}")
    # print(f"examples here: {values_len(lang_to_examples)}")
    # print(f"all_links len: {len(all_links)}")
    # Recursively traversing the graph gets us into very wrong translation territory
    # because of sentences with similar but not precisely equivalent meaning.
    # all_links2 = gather_links(sid, set())
    # print(f"all_links2 len: {len(all_links2)}")

    for linked_sid in all_links:
        linked_lang, linked_sentence = id_to_lang_sentence[linked_sid]
        if linked_lang not in lang_to_examples:
            lang_to_examples[linked_lang] = set()
        lang_to_examples[linked_lang].add(linked_sentence)

    return lang_to_examples

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

def generate_all_examples():
    for i, sid in enumerate(sorted(eng_ids)):
        lang_to_examples = generate_examples(sid)
        if not lang_to_examples:
            continue
        
        yield lang_to_examples

def write_md_files():
    print("write_md_files")
    for lang_to_examples in generate_all_examples():
        if len(lang_to_examples) < 12:
            # not enough translations
            continue
        sentence = sorted(dedupe_sentences(lang_to_examples["eng"]))[0]
        if len(sentence) > 60:
            # skip the long ones
            continue
        md_filename = to_md_name(sentence)
        md_text = generate_md(lang_to_examples)
        
        with open(script_dir + f'/../a2/{md_filename}', 'w', encoding='utf8') as fout:
            fout.write(md_text)



def analyze_links():
    #   "dan": {
    #     "name": "Danish",
    #     "code2": "da"
    #   },
    codes3 = json.load(open(script_dir + '/language-codes.json', encoding='utf8'))
    count = Counter()
    # takes about a minute to run.
    for line in open(script_dir + '/links.csv'):
        parts = [part.strip() for part in line.split('\t') if part.strip()]
        if len(parts) != 2:
            continue
        a, b = parts
        count[a] += 1
        count[b] += 1

    print(count.most_common(50)) 
    # [('10519298', 1388), ('373320', 768), ('1434', 670), ('8315175', 654), ('70623', 624), ('373330', 556), ('408293', 540), ('16492', 534), ('8328540', 514), ('370703', 504), ('416367', 502), ('30341', 486), ('138919', 474), ('349064', 460), ('1437', 456), ('2055348', 440), ('374827', 436), ('378270', 434), ('356200', 434), ('516745', 432), ('403981', 430), ('373216', 416), ('413731', 400), ('436243', 388), ('477086', 384), ('370708', 376), ('2046775', 370), ('448645', 368), ('2175', 364), ('36088', 362), ('1622', 360), ('7872529', 360), ('1329', 358), ('2168', 358), ('328604', 358), ('1399479', 354), ('36419', 352), ('329713', 352), ('462430', 352), ('361350', 344), ('428402', 340), ('1876041', 334), ('1564', 330), ('376611', 330), ('16164', 320), ('2412739', 320), ('433491', 318), ('382287', 316), ('477061', 308), ('379451', 308)]


