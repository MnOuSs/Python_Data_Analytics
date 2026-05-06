import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress


def draw_plot():
  # Read data from file
  df = pd.read_csv('epa-sea-level.csv')

  # Create scatter plot
  fig, ax = plt.subplots(figsize=(12,9))
  plt.scatter(x= 'Year', y= "CSIRO Adjusted Sea Level", data= df)
  
  # Create first line of best fit
  lin = linregress(df['Year'], df["CSIRO Adjusted Sea Level"])
  x = pd.Series(i for i in range(1880, 2051))
  y = lin.slope * x + lin.intercept
  plt.plot(x, y, color='Red')

  # Create second line of best fit
  df_2000 = df.loc[df['Year'] >= 2000]
  x_2000 = df_2000['Year']
  y_2000 = df_2000["CSIRO Adjusted Sea Level"]
  lin_2 = linregress(x_2000, y_2000)
  new_x = pd.Series(i for i in range(2000, 2051))
  new_y = lin_2.slope * new_x + lin_2.intercept
  plt.plot(new_x, new_y, color='green')

  # Add labels and title
  ax.set_title("Rise in Sea Level")
  ax.set_xlabel('Year')
  ax.set_ylabel("Sea Level (inches)")
    
  # Save plot and return data for testing (DO NOT MODIFY)
  plt.savefig('sea_level_plot.png')
  return plt.gca()
