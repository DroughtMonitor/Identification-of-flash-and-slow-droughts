__author__ = "Weiqi Liu"
__copyright__ = "Copyright (C) 2025 Weiqi Liu"
__license__ = "NIEER"
__version__ = "2025.03"
__Reference paper__ == "Anthropogenic shift towards higher risk of flash drought over China"

import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Arial'

def convert_rgb_to_01(rgb):
    """将RGB值从0-255转换为0-1范围"""
    return tuple([c / 255.0 for c in rgb])
colors=[convert_rgb_to_01((255,130,171)),convert_rgb_to_01((255,192,203)),convert_rgb_to_01((255,69,0)), convert_rgb_to_01((255,203,173))]


df = pd.read_csv('/home/lwq/桌面/result.csv', encoding='utf-8')
# Define two different time ranges
df['date'] = pd.to_datetime(df['date'])
#a flash drough period
start_date_1 = '2013-08-09'
end_date_1 = '2013-09-13'

#a slow drough period
start_date_2 = '2007-04-16'
end_date_2 = '2007-06-05'

# Filter data based on the date ranges
df_filtered1 = df[(df['date'] >= start_date_1) & (df['date'] <= end_date_1)]
df_filtered2 = df[(df['date'] >= start_date_2) & (df['date'] <= end_date_2)]

# Create two subplots
fig, axs = plt.subplots(2, 1, figsize=(10, 12), dpi=600)

# Plot the first subplot (Flash drought)
axs[0].plot(df_filtered1['date'], df_filtered1['Percentile'], marker='o', linestyle='-', color='black', label='SM percentile')

# Set the title and add horizontal lines at specific values
axs[0].set_title('(a) Flash drought', x=0.03, y=.92, loc='left', fontsize=16, fontweight='bold')
axs[0].axhline(y=40, linestyle="--", color="black", linewidth=1)
axs[0].axhline(y=20, linestyle="--", color="black", linewidth=1)
axs[0].set_ylabel('SM percentile (%)', fontsize=16)

# Set the x-ticks at regular intervals
axs[0].set_xticks(df_filtered['date'].values[::2])

# Add shaded regions for specific date ranges (indicating onset and recovery)
mask = (df_filtered1['date'] >= '2013-08-19') & (df_filtered1['date'] <= '2013-08-29')
axs[0].fill_between(df_filtered1['date'][mask], 40, df_filtered1['Percentile'][mask], color=colors[0], alpha=0.5)
mask = (df_filtered1['date'] >= '2013-08-29') & (df_filtered1['date'] <= '2013-09-03')
axs[0].fill_between(df_filtered1['date'][mask], 40, df_filtered1['Percentile'][mask], color=colors[1], alpha=0.5)

# Annotate the onset and recovery phases
axs[0].text(0.43, 0.55, 'Onset', color='black', fontsize=18, transform=axs[0].transAxes)
axs[0].text(0.58, 0.55, 'Recovery', color='black', fontsize=18, transform=axs[0].transAxes)

# Set tick marks and labels
axs[0].set_xticks(df_filtered1['date'].values[::2])
axs[0].set_yticks([10, 20, 30, 40, 50])
axs[0].tick_params(labelsize=16)
axs[0].set_ylim(10, 50)
axs[0].legend(fontsize=16, framealpha=False)

# Plot the second subplot (Slow drought)
axs[1].plot(df_filtered2['date'], df_filtered2['Percentile'], marker='o', linestyle='-', color='black', label='SM percentile')

# Set the title and add horizontal lines at specific values
axs[1].set_title('(b) Slow drought', x=0.03, y=.92, loc='left', fontsize=16, fontweight='bold')
axs[1].axhline(y=40, linestyle="--", color="black", linewidth=1)
axs[1].axhline(y=20, linestyle="--", color="black", linewidth=1)
axs[1].set_ylabel('SM percentile (%)', fontsize=16)

# Set the x-ticks at regular intervals
axs[1].set_xticks(df_filtered['date'].values[::2])

# Add shaded regions for specific date ranges (indicating onset and recovery)
mask = (df_filtered2['date'] >= '2007-04-26') & (df_filtered2['date'] <= '2007-05-16')
axs[1].fill_between(df_filtered2['date'][mask], 40, df_filtered2['Percentile'][mask], color=colors[2], alpha=0.5)
mask = (df_filtered2['date'] >= '2007-05-16') & (df_filtered2['date'] <= '2007-05-26')
axs[1].fill_between(df_filtered2['date'][mask], 40, df_filtered2['Percentile'][mask], color=colors[3], alpha=0.5)

# Annotate the onset and recovery phases
axs[1].text(0.48, 0.55, 'Onset', color='black', fontsize=18, transform=axs[1].transAxes)
axs[1].text(0.6, 0.55, 'Recovery', color='black', fontsize=18, transform=axs[1].transAxes)

# Set tick marks and labels
axs[1].set_xticks(df_filtered2['date'].values[::2])
axs[1].set_yticks([10, 20, 30, 40, 50])
axs[1].tick_params(labelsize=16)
axs[1].set_ylim(10, 50)

# Adjust spacing between subplots
plt.subplots_adjust(wspace=0.1, hspace=0.1)

# Display the plots
plt.show()
