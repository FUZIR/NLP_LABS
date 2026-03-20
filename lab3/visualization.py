import matplotlib.pyplot as plt
import numpy as np

experiments = ['Text vs Itself', 'Part 1 vs Part 2', 'Phrase vs Text', 'Synonyms']

tfidf_en = [1.0000, 0.0254, 0.2242, 0.3361]
bert_en = [1.0000, 0.4035, 0.6138, 0.7557]

tfidf_uk = [1.0000, 0.0000, 0.1745, 0.3361]
bert_uk = [1.0000, 0.7029, 0.2198, 0.6888]

def plot_results(tfidf_scores, bert_scores, language, color1, color2):
    x = np.arange(len(experiments))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, tfidf_scores, width, label='TF-IDF (Лексичний збіг)', color=color1)
    rects2 = ax.bar(x + width/2, bert_scores, width, label='BERT (Семантичний зміст)', color=color2)

    ax.set_ylabel('Косинусна схожість', fontsize=12)
    ax.set_title(f'Порівняння методів векторизації ({language})', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(experiments, fontsize=11)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    ax.bar_label(rects1, padding=3, fmt='%.4f')
    ax.bar_label(rects2, padding=3, fmt='%.4f')

    fig.tight_layout()
    plt.savefig(f'vectorization_comparison_{language.lower()}.png')
    plt.show()

plot_results(tfidf_en, bert_en, 'English', '#1f77b4', '#ff7f0e')
plot_results(tfidf_uk, bert_uk, 'Ukrainian', '#2ca02c', '#d62728')