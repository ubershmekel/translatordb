import md_gen

from google.cloud import translate_v2

import os

script_dir = os.path.dirname(__file__)

examples = [
    "He is washing the car now.",
    "Right now, he's washing the car.",
    "At this moment, he's cleaning the car.",
    "Currently, he's washing the car.",
    "He's in the process of washing the car.",
    "At present, he's cleaning the car.",
]

def translate_text(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    print("Text: {}".format(result["input"]))
    print("Translation: {}".format(result["translatedText"]))
    print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result

# translate_text("es", "Hello world")

from google.cloud import translate
client = translate.TranslationServiceClient()
print(client)

def fix_gcp_translate(text: str) -> str:
    # Not sure why this happens,
    # but we got it for:
    # "If it rains tomorrow, I will stay home." en->fr
    # "Je resterai à la maison s&#39;il pleut demain.""
    # Also - "עד מחר, הדו&quot;ח יושלם."
    return text.replace('&#39;', "'").replace('&quot;', '"')

def translate(lines, lang_code):
    result = client.translate_text(parent="projects/ubershmekel", contents=lines, source_language_code="en", target_language_code=lang_code)
    return [fix_gcp_translate(trans.translated_text) for trans in result.translations]
    # print(result)
    # import pdb; pdb.set_trace()
    # return result

# print(translate(examples, "he"))

out_dir = script_dir + '/out'
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)

def main():
    lang_to_examples = {
        "eng": examples,
    }
    for c3, c2 in md_gen.lang_code_3to2.items():
        if c3 == "eng":
            continue
        lang_to_examples[c3] = translate(examples, c2)
        print(lang_to_examples[c3])
    md_text = md_gen.generate_md(lang_to_examples)
    md_filename = md_gen.to_md_name(examples[0])
        
    with open(f'{out_dir}/{md_filename}', 'w', encoding='utf8') as fout:
        fout.write(md_text)

main()