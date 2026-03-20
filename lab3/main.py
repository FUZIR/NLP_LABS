import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

nlp_en = spacy.load("en_core_web_sm")
nlp_uk = spacy.load("uk_core_news_sm")

bert_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

text_en = ("Significant progress has been made in automated problem-solving using societies of agents powered by large "
           "language models (LLMs). In finance, efforts have largely focused on single-agent systems handling "
           "specific tasks or multi-agent frameworks independently gathering data. However, the multi-agent systems' "
           "potential to replicate real-world trading firms' collaborative dynamics remains underexplored. "
           "TradingAgents proposes a novel stock trading framework inspired by trading firms, featuring LLM-powered "
           "agents in specialized roles such as fundamental analysts, sentiment analysts, technical analysts, "
           "and traders with varied risk profiles. The framework includes Bull and Bear researcher agents assessing "
           "market conditions, a risk management team monitoring exposure, and traders synthesizing insights from "
           "debates and historical data to make informed decisions. By simulating a dynamic, collaborative trading "
           "environment, this framework aims to improve trading performance. Detailed architecture and extensive "
           "experiments reveal its superiority over baseline models, with notable improvements in cumulative returns, "
           "Sharpe ratio, and maximum drawdown, highlighting the potential of multi-agent LLM frameworks in financial "
           "trading.")
text_uk = ("Двадцять років. Що таке двадцять років? Дивлячись, що ви маєте на увазі. Якщо вік двадцятирічної людини — "
           "то це вічність. Вічність позаду і ніякого уявлення про час, та простір попереду. Так. Вічність позаду. Це "
           "ціле дитинство, з міксом із ранкових сліз по дорозі в садочок, свят у вічних костюмах зайчика, застуд, "
           "ігор на будівлях і гаражах, морозива, поїздок до бабусь, завжди здертих колін, якихось котів, "
           "щенят і т.д. і т.п.")

experiments_en = {
    "text_vs_itself": (text_en, text_en),

    "part1_vs_part2": (
        "Significant progress has been made in automated problem-solving using societies of agents powered by large language models (LLMs).",
        "In finance, efforts have largely focused on single-agent systems handling specific tasks or multi-agent frameworks independently gathering data."
    ),

    "phrase_vs_text": ("multi-agent LLM frameworks", text_en),

    "synonyms": ("Machine learning is great.", "Deep learning is awesome.")
}

experiments_uk = {
    "text_vs_itself": (text_uk, text_uk),

    "part1_vs_part2": (
        "Двадцять років. Що таке двадцять років? Дивлячись, що ви маєте на увазі.",
        "Якщо вік двадцятирічної людини — то це вічність."
    ),

    "phrase_vs_text": ("мікс із ранкових сліз по дорозі в садочок", text_uk),

    "synonyms": ("Машинне навчання це чудово.", "Глибоке навчання це круто.")
}


def analyze_pos(text, lang='en'):
    nlp = nlp_en if lang == 'en' else nlp_uk
    doc = nlp(text)
    print(f"\n--- POS Tagging ({lang.upper()}) ---")
    for token in doc:
        # Виводимо слово, його лему та частину мови (POS)
        print(f"{token.text:15} | Lemma: {token.lemma_:15} | POS: {token.pos_}")


def compare_tfidf(text1, text2):
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return sim
    except ValueError:
        return 0.0


def compare_bert(text1, text2):
    emb1 = bert_model.encode([text1])
    emb2 = bert_model.encode([text2])
    sim = cosine_similarity(emb1, emb2)[0][0]
    return sim


def run_comparisons(experiments, lang_label):
    print(f"\n=== Дослідження векторних уявлень ({lang_label}) ===")
    print(f"{'Експеримент':<20} | {'Метод 1 (TF-IDF)':<18} | {'Метод 2 (BERT)':<18}")
    print("-" * 65)

    for exp_name, (t1, t2) in experiments.items():
        sim_tfidf = compare_tfidf(t1, t2)
        sim_bert = compare_bert(t1, t2)
        print(f"{exp_name:<20} | {sim_tfidf:>16.4f} | {sim_bert:>16.4f}")


if __name__ == "__main__":
    analyze_pos(experiments_en["part1_vs_part2"][0], 'en')
    analyze_pos(experiments_uk["part1_vs_part2"][0], 'uk')

    run_comparisons(experiments_en, "Англійська")
    run_comparisons(experiments_uk, "Українська")