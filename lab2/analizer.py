import os
import re
import nltk
import pandas as pd
import spacy
from collections import Counter
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.util import ngrams
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, SnowballStemmer

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

# завантаження моделей
nlp_uk = spacy.load("uk_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")

stop_words = set(stopwords.words('english')) | set(stopwords.words('russian')) | {
    "це","та","що","як","в","на","до","з","у","за","не","який","яка","яке","також",
    "про","від","але","його","її","їх","ми","ви","вони","вона","він","було"
}

porter = PorterStemmer()
snowball = SnowballStemmer("english")

def save_step(filename, data):
    with open(f"./nlp_steps/{filename}", "w", encoding="utf-8") as f:
        if isinstance(data, list):
            f.write("\n".join(map(str, data)))
        else:
            f.write(str(data))

def process_text(text: str):
    # 1.3 Нормалізація
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"\s+", " ", text)
    save_step("step_1_normalized.txt", text)

    # 1.4 Токенізація трьома типами
    word_tokens = word_tokenize(text)
    sent_tokens = sent_tokenize(text)
    bigrams = list(ngrams(word_tokens, 2))

    save_step("step_2_tokens_words.txt", word_tokens)
    save_step("step_3_tokens_sentences.txt", sent_tokens)
    save_step("step_4_bigrams.txt", bigrams)

    # 1.6 Лематизація
    doc = nlp_uk(" ".join(word_tokens))

    lemmas = []
    for token in doc:
        lemma = token.lemma_.lower().strip()
        if (
            len(lemma) > 2
            and lemma not in stop_words
            and token.pos_ in ["NOUN", "PROPN", "ADJ"]
        ):
            lemmas.append(lemma)

    # fallback
    if len(lemmas) < 5:
        doc = nlp_en(" ".join(word_tokens))
        lemmas = [
            token.lemma_.lower().strip()
            for token in doc
            if len(token.lemma_) > 2
        ]

    save_step("step_5_lemmas.txt", lemmas)

    # стоп фільтр
    stop_lemmas = stop_words | {
        "бути","мати","могти","який","цей","той","свій",
        "так","ще","вже","дуже","сам","самий","один",
        "день","час","рік","людина","також"
    }

    filtered_lemmas = [l for l in lemmas if l not in stop_lemmas]

    # 1.7 Стемінг
    porter_stems = [porter.stem(w) for w in filtered_lemmas]
    snowball_stems = [snowball.stem(w) for w in filtered_lemmas]

    save_step("step_6_stems_porter.txt", porter_stems)
    save_step("step_7_stems_snowball.txt", snowball_stems)

    # 1.8 Топ 10
    freq = Counter(filtered_lemmas)
    top10 = freq.most_common(10)

    save_step("step_8_top10.txt", top10)

    return {
        "normalized": text,
        "tokens_words": word_tokens,
        "tokens_sentences": sent_tokens,
        "tokens_bigrams": bigrams,
        "lemmas": filtered_lemmas,
        "porter_stems": porter_stems,
        "snowball_stems": snowball_stems,
        "top10": top10
    }

def analyze_news():
    os.makedirs("nlp_steps", exist_ok=True)
    df = pd.read_csv("../news.csv")
    all_text = " ".join(df["text"].astype(str).tolist())
    result = process_text(all_text)
    print(result)
    print("\n--- TOP 10 WORDS ---")
    for word, count in result["top10"]:
        print(f"{word} : {count}")

if __name__ == "__main__":
    analyze_news()