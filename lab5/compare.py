import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns

files = {
    'Allo': ['allo_computers.csv', 'allo_fridges.csv', 'allo_tvs.csv'],
    'Comfy': ['comfy_computers.csv', 'comfy_fridges.csv', 'comfy_tvs.csv'],
    'Rozetka': ['rozetka_computers.csv', 'rozetka_fridges.csv', 'rozetka_tvs.csv']
}

dfs = []

for platform, file_list in files.items():
    for file in file_list:
        try:
            df = pd.read_csv(file)
            df['platform'] = platform
            dfs.append(df)
        except Exception as e:
            print(f"Помилка при читанні файлу {file}: {e}")

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
df_all_clean = df_all.dropna(subset=['price_clean']).copy()

stats = df_all_clean.groupby(['category', 'platform'])['price_clean'].agg(
    Кількість='count',
    Мін_ціна='min',
    Сер_ціна='mean',
    Макс_ціна='max',
    Медіана='median'
).round(2)

print("--- Статистика за категоріями та платформами ---")
print(stats.to_string())

df_all_clean.to_csv('all_platforms_cleaned_data.csv', index=False, encoding='utf-8')
stats.to_csv('comparative_analysis_stats.csv', encoding='utf-8')
print("\nФайли 'all_platforms_cleaned_data.csv' та 'comparative_analysis_stats.csv' успішно збережено!")

plt.figure(figsize=(10, 6))
sns.barplot(data=df_all_clean, x='category', y='price_clean', hue='platform', estimator='mean', errorbar=None)
plt.title('Порівняння середніх цін за категоріями між платформами', fontsize=14)
plt.xlabel('Категорія', fontsize=12)
plt.ylabel('Середня ціна (грн)', fontsize=12)
plt.legend(title='Платформа')
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('average_prices_comparison.png')
plt.show()