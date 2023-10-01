import pandas as pd
import matplotlib.pyplot as plt

sentiments = pd.read_csv('Sentiments.csv')

plt.figure(figsize=(10, 6))
plt.hist(sentiments['sentiment score'], bins=30, edgecolor='k', alpha=0.7)
plt.title('Distribution of Sentiment Scores')
plt.xlabel('Sentiment Score')
plt.ylabel('Frequency')
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.show()

stats = sentiments['sentiment score'].describe()

skewness = sentiments['sentiment score'].skew()

print(stats)
print("Skewness:", skewness)