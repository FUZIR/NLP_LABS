import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# --- Завантаження та очищення даних ---

FILES = {
    'Allo':    ['../lab5/allo_computers.csv', '../lab5/allo_fridges.csv', '../lab5/allo_tvs.csv'],
    'Comfy':   ['../lab5/comfy_computers.csv', '../lab5/comfy_fridges.csv', '../lab5/comfy_tvs.csv'],
    'Rozetka': ['../lab5/rozetka_computers.csv', '../lab5/rozetka_fridges.csv', '../lab5/rozetka_tvs.csv'],
}

dfs = []
for platform, file_list in FILES.items():
    for file in file_list:
        try:
            df = pd.read_csv(file)
            df['platform'] = platform
            dfs.append(df)
        except Exception as e:
            print(f"Помилка при читанні {file}: {e}")

df_all = pd.concat(dfs, ignore_index=True)


def clean_price(price_val):
    if pd.isna(price_val):
        return None
    price_str = str(price_val).strip()
    if price_str == "Немає в наявності":
        return None
    price_str = price_str.replace(' ', '').replace('\xa0', '')
    numbers = re.findall(r'\d+', price_str)
    if numbers:
        return min([int(n) for n in numbers])
    return None


df_all['price_clean'] = df_all['price'].apply(clean_price)
df_clean = df_all.dropna(subset=['price_clean']).copy()

# --- Статистика ---

stats = df_clean.groupby(['category', 'platform'])['price_clean'].agg(
    count='count',
    min_price='min',
    avg_price='mean',
    max_price='max',
    median_price='median'
).round(2)

print("=== Статистика за категоріями та платформами ===")
print(stats.to_string())
print()

# --- Візуалізація ---

plt.figure(figsize=(10, 6))
sns.barplot(data=df_clean, x='category', y='price_clean', hue='platform',
            estimator='mean', errorbar=None)
plt.title('Порівняння середніх цін між платформами', fontsize=14)
plt.xlabel('Категорія', fontsize=12)
plt.ylabel('Середня ціна (грн)', fontsize=12)
plt.legend(title='Платформа')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('price_comparison.png')
plt.close()
print("Графік збережено: price_comparison.png")

# --- Підготовка зведеної таблиці для Groq ---

stats_reset = stats.reset_index()
stats_text_lines = []
for _, row in stats_reset.iterrows():
    stats_text_lines.append(
        f"  {row['category']} / {row['platform']}: "
        f"кількість={int(row['count'])}, "
        f"мін={row['min_price']:.0f} грн, "
        f"середня={row['avg_price']:.0f} грн, "
        f"медіана={row['median_price']:.0f} грн, "
        f"макс={row['max_price']:.0f} грн"
    )
stats_summary = "\n".join(stats_text_lines)

# Топ-3 найдешевших товарів по кожній категорії
cheapest_lines = []
for category in df_clean['category'].unique():
    sub = df_clean[df_clean['category'] == category].nsmallest(3, 'price_clean')
    for _, row in sub.iterrows():
        cheapest_lines.append(
            f"  [{category}] {row['platform']}: {row['title'][:60]} — {row['price_clean']:.0f} грн"
        )
cheapest_summary = "\n".join(cheapest_lines)

# --- Groq AI аналіз ---

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

prompt = f"""Ти — аналітик електронної комерції. Проведи детальний порівняльний аналіз пропозицій між трьома українськими торговими платформами (Allo, Comfy, Rozetka) на основі зібраних даних.

=== СТАТИСТИКА ЦІН ===
{stats_summary}

=== ТОП-3 НАЙДЕШЕВШИХ ТОВАРИ ПО КАТЕГОРІЯХ ===
{cheapest_summary}

Твоє завдання:
1. Порівняй середні та медіанні ціни між платформами для кожної категорії. Яка платформа пропонує найнижчі ціни?
2. Проаналізуй розкид цін (різниця між мін та макс). Де асортимент різноманітніший?
3. Визнач, на якій платформі найбільше товарів у кожній категорії (за кількістю).
4. Дай рекомендації покупцю: де краще купувати комп'ютерну техніку, холодильники та телевізори?
5. Загальний висновок: яка платформа найвигідніша для покупок в цілому?

Відповідай українською мовою, структуровано, з чіткими висновками для кожного пункту.
"""

print("AI-аналіз (Groq / Llama)\n")

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "Ти досвідчений аналітик ринку електронної комерції. Надаєш чіткі, структуровані аналітичні звіти українською мовою."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    max_tokens=2048,
)

analysis = chat_completion.choices[0].message.content
print(analysis)

# Зберегти звіт у файл
with open("ai_analysis_report.txt", "w", encoding="utf-8") as f:
    f.write("ПОРІВНЯЛЬНИЙ АНАЛІЗ ПЛАТФОРМ (AI звіт)\n\n")
    f.write("--- Статистика ---\n")
    f.write(stats_summary + "\n\n")
    f.write("--- AI висновки (Groq / Llama-3.3-70b) ---\n")
    f.write(analysis + "\n")

print("\nЗвіт збережено: ai_analysis_report.txt")
