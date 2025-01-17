# -*- coding: utf-8 -*-
"""CrosssellingV2.0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EbPrDVD_OxohiHY778L452yvBIUrSC8a
"""

# -*- coding: utf-8 -*-
"""Cross-Selling Analysis Notebook

Generated within a cloud-based interactive development environment.

Notebook available at:
    https://colab.research.google.com/drive/1hsY6H57_M-Vt343ZCzlg6FTQFuBS4Ss_
"""

import numpy as np
import pandas as pd

# Import libraries for creating visualizations
import matplotlib.pyplot as plt
import seaborn as sns
# Allows inline plotting for notebooks
import altair as alt
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

# Libraries for Apriori algorithm
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

# Code to access Google Drive in a Google Colaboratory environment
from google.colab import drive
drive.mount('/content/drive')  # Mounting Google Drive
# Load data from a specific path in Google Drive
sales_data = pd.read_csv('/content/drive/My Drive/food_orders_crosssell_V2.0.csv')

sales_data.head()

# Create DataFrame focusing on necessary columns only
sales_data = pd.DataFrame(sales_data, columns=['Member_number', 'Date', 'itemDescription'], index=None)

sales_data.head()

# Convert the 'Date' column to datetime format
sales_data['Date'] = pd.to_datetime(sales_data['Date'])

# Extract components from the 'Date' and create new columns
sales_data['year'] = sales_data['Date'].apply(lambda x: x.year)
sales_data['month'] = sales_data['Date'].apply(lambda x: x.month)
sales_data['day'] = sales_data['Date'].apply(lambda x: x.day)
sales_data['weekday'] = sales_data['Date'].apply(lambda x: x.weekday())

# Configure the aesthetic style of plots
plt.figure(figsize=(15, 8))
plt.style.use('seaborn-white')

# Visualize the top 10 fast moving products
plt.subplot(1, 2, 1)
ax = sns.countplot(y="itemDescription", hue="year", data=sales_data, palette="pastel",
                   order=sales_data.itemDescription.value_counts().iloc[:10].index)
ax.set_xticklabels(ax.get_xticklabels(), fontsize=11, rotation=40, ha="right")
ax.set_title('Top 10 Fast Moving Products', fontsize=22)
ax.set_xlabel('Total Number of Items Purchased', fontsize=20)
ax.set_ylabel('Top 10 Items', fontsize=20)
plt.tight_layout()

# Visualize the bottom 10 fast moving products
plt.subplot(1, 2, 2)
ax = sns.countplot(y="itemDescription", hue="year", data=sales_data, palette="pastel",
                   order=sales_data.itemDescription.value_counts().iloc[-10:].index)
ax.set_xticklabels(ax.get_xticklabels(), fontsize=11, rotation=40, ha="right")
ax.set_title('Bottom 10 Fast Moving Products', fontsize=22)
ax.set_xlabel('Total Number of Items Purchased', fontsize=20)
ax.set_ylabel('Bottom 10 Items', fontsize=20)
plt.tight_layout()

import altair as alt
# Preparing data with quantity purchased
pur = sales_data.copy()
pur['qty_purchased'] = sales_data['Member_number'].map(sales_data['Member_number'].value_counts())

# Identify top customers based on quantity purchased
best_cust = pur[['Member_number', 'qty_purchased', 'year']].sort_values(by='Member_number', ascending=False).head(500)
best_cust.Member_number = best_cust.Member_number.astype('category')
best_cust.year = best_cust.year.astype('category')

# Visualization of top customers
alt.Chart(best_cust).mark_bar(color="darkgreen").encode(
    x='qty_purchased',
    y=alt.Y('Member_number', sort='-x'),
    color='year',
    tooltip=['Member_number', 'qty_purchased']
).properties(height=400, width=600, title="Top Customers")

# Creating a sparse matrix for Apriori analysis
basket = (pur.groupby(['Member_number', 'itemDescription'])['qty_purchased']
          .sum().unstack().reset_index().fillna(0)
          .set_index('Member_number'))

# Encoding the quantity purchased into binary format for analysis
def encode(x):
    return 0 if x <= 0 else 1  # Simplified conditional return

basket_sets = basket.applymap(encode)
basket_sets.head()

# Conducting Apriori algorithm to find frequent item sets with high support
frequent_itemsets = apriori(basket_sets, min_support=0.01, use_colnames=True)

# Generating association rules based on lift
as_rule_model = association_rules(frequent_itemsets, metric="lift", min_threshold=0.7)
as_rule_model.head()

# Filter rules by lift and confidence thresholds
as_rule_data=as_rule_model[(as_rule_model['lift'] >= 0.8) & (as_rule_model['confidence'] >= 0.76)]

as_rule_data.count()

# Plotting relationships between different metrics
plt.figure(figsize=(10, 10))
plt.subplot(2, 2, 1)
sns.scatterplot(x="support", y="confidence", data=as_rule_data)
plt.subplot(2, 2, 2)
sns.scatterplot(x="support", y="lift", data=as_rule_data)
plt.subplot(2, 2, 3)
sns.scatterplot(x="confidence", y="lift", data=as_rule_data)
plt.subplot(2, 2, 4)
sns.scatterplot(x="antecedent support", y="consequent support", data=as_rule_data)

# Analysis of rules with more than one item on the left-hand side
as_rule_data['lhs items'] = as_rule_data['antecedents'].apply(lambda x: len(x))
top_rules = as_rule_data[as_rule_data['lhs items'] > 1].sort_values('lift', ascending=False).head()

# Reformatting sets for clearer visualization
as_rule_data['antecedents_'] = as_rule_data['antecedents'].apply(lambda a: ','.join(list(a)))
as_rule_data['consequents_'] = as_rule_data['consequents'].apply(lambda a: ','.join(list(a)))
pivot = as_rule_data[as_rule_data['lhs items'] > 1].pivot(index='antecedents_', columns='consequents_', values='lift')

# Display a heatmap of lift values
sns.heatmap(pivot, annot=True)
plt.yticks(rotation=0)
plt.xticks(rotation=90)
plt.show()