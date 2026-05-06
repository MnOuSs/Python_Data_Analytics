import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters


# Import data (Make sure to parse dates. Consider setting index column to 'date'.)
df = pd.read_csv('fcc-forum-pageviews.csv', parse_dates=['date'], index_col='date')

# Clean data
df = df[(df['value'] >= df['value'].quantile(0.025)) & (df['value'] <= df['value'].quantile(0.975))]

def draw_line_plot():
  # Draw line plot
  fig, ax = plt.subplots(figsize=(15,5))
  ax.plot(df.index, df['value'], color='red', linewidth=1)
  ax.set_title("Daily freeCodeCamp Forum Page Views 5/2016-12/2019")
  ax.set_xlabel("Date")
  ax.set_ylabel("Page Views")

  # Save image and return fig (don't change this part)
  fig.savefig('line_plot.png')
  return fig

def draw_bar_plot():
    # Copy and modify data for monthly bar plot
  df_bar = df.copy()
  df_bar['Years'] = df_bar.index.year
  df_bar['Months'] = df_bar.index.month_name()
  df_bar = pd.DataFrame(df_bar.groupby(['Years', 'Months'], sort=False)['value'].mean().round().astype(int))
  df_bar = df_bar.rename(columns={'value': "Average Page Views"})
  df_bar = df_bar.reset_index()
  add = {'Years': [2016, 2016, 2016, 2016], 'Months': ['January', 'February', 'March', 'April'], "Average Page Views": [0, 0, 0, 0]}

  df_bar = pd.concat([pd.DataFrame(add), df_bar])
   
  # Draw bar plot
  fig, ax = plt.subplots(figsize=(12, 9))

  chart = sns.barplot(data=df_bar, x="Years", y="Average Page Views", hue="Months", palette='tab10')
  chart.set_xticklabels(chart.get_xticklabels(), rotation=90, horizontalalignment='center')

  # Save image and return fig (don't change this part)
  fig.savefig('bar_plot.png')
  return fig

def draw_box_plot():
  # Prepare data for box plots (this part is done!)
  df_box = df.copy()
  df_box.reset_index(inplace=True)
  df_box['year'] = [d.year for d in df_box.date]
  df_box['month'] = [d.strftime('%b') for d in df_box.date]

  # Draw box plots (using Seaborn)
  fig, (ax1, ax2) = plt.subplots(1, 2)
  fig.set_figwidth(20)
  fig.set_figheight(10)

  ax1 = sns.boxplot(x = df_box['year'], y = df_box['value'], linewidth=0.5, ax = ax1)
  ax1.set_title("Year-wise Box Plot (Trend)")  
  ax1.set_xlabel("Year")
  ax1.set_ylabel("Page Views")

  range = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  ax2 = sns.boxplot(x= df_box['month'], y= df_box['value'], order= range, linewidth= 0.5, ax= ax2)
  ax2.set_title("Month-wise Box Plot (Seasonality)")
  ax2.set_xlabel('Month')
  ax2.set_ylabel("Page Views")

  # Save image and return fig (don't change this part)
  fig.savefig('box_plot.png')
  return fig
