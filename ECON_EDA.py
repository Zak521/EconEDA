## Economic Data Analysis Project
## Zak Kotschegarow

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

## Set style and options for better visuals
plt.style.use('fivethirtyeight')
pd.set_option('display.max_columns', 500)
color_pal = plt.rcParams['axes.prop_cycle'].by_key()['color']

## from the anaconda prompt window
## pip install fredapi, then
from fredapi import Fred

## 1. Create the Fred object
fred = Fred(api_key='e0fb5aaa932be45a0c8bd4f00c8c6284')

## 2. Search for economic data
sp_search = fred.search('S&P', order_by='popularity')  ## S&P 500

## 3. Pull raw data & Plot the S&P500
sp500 = fred.get_series(series_id='SP500')
sp500.plot(figsize=(10, 5), title='S&P500', lw=2)
plt.show()

## 4. Pull and join multiple data series 
unemp_df = fred.search('unemployment rate state', filter=('frequency', 'Monthly'))
unemp_df = unemp_df.query('seasonal_adjustment == "Seasonally Adjusted" and units == "Percent"')
unemp_df = unemp_df.loc[unemp_df['title'].str.contains('Unemployment Rate')]

## Fetch and combine unemployment data series
all_results = []
for myid in unemp_df.index:
    results = fred.get_series(myid)
    results = results.to_frame(name=myid)  ## Store each series as a DataFrame
    all_results.append(results)
uemp_results = pd.concat(all_results, axis=1)

## Drop problematic columns with unusual lengths
cols_to_drop = []
for i in uemp_results:
    if len(i) > 4:
        cols_to_drop.append(i)
uemp_results = uemp_results.drop(columns=cols_to_drop, axis=1)

## Clean up and rename columns for clarity
uemp_states = uemp_results.copy()
uemp_states = uemp_states.dropna()   ## Remove any rows with missing data
id_to_state = unemp_df['title'].str.replace('Unemployment Rate in ', '').to_dict()
uemp_states.columns = [id_to_state[c] for c in uemp_states.columns]

# Plot States Unemployment Rate
fig = px.line(uemp_states, title="Unemployment Rates by State")
fig.show(renderer="browser")

## Pull May 2020 Unemployment Rate Per State
ax = uemp_states.loc[uemp_states.index == '2020-05-01'].T \
    .sort_values('2020-05-01') \
    .plot(kind='barh', figsize=(8, 12), width=0.7, edgecolor='black',
          title='Unemployment Rate by State, May 2020')
ax.legend().remove()
ax.set_xlabel('% Unemployed')
plt.show()

## Pull Participation Rate
part_df = fred.search('participation rate state', filter=('frequency', 'Monthly'))
part_df = part_df.query('seasonal_adjustment == "Seasonally Adjusted" and units == "Percent"')

part_id_to_state = part_df['title'].str.replace('Labor Force Participation Rate for ', '').to_dict()

all_results = []
for myid in part_df.index:
    results = fred.get_series(myid)
    results = results.to_frame(name=myid)
    all_results.append(results)
part_states = pd.concat(all_results, axis=1)
part_states.columns = [part_id_to_state[c] for c in part_states.columns]

## Plot Unemployment vs Participation for each state
# Fix DC
uemp_states = uemp_states.rename(columns={'the District of Columbia': 'District Of Columbia'})

# Filter out invalid states
valid_states = [state for state in uemp_states.columns if state not in ["District Of Columbia", "Puerto Rico"]]
n_states = len(valid_states)

# Setup subplot grid dynamically
cols = 5
rows = -(-n_states // cols)  # Ceiling division
fig, axs = plt.subplots(rows, cols, figsize=(cols * 6, rows * 3), sharex=True)
axs = axs.flatten()

## Plot each state's unemployment and participation
for i, state in enumerate(valid_states):
    ax2 = axs[i].twinx()
    uemp_states.query('index >= 2020 and index < 2022')[state].plot(ax=axs[i], label='Unemployment')
    part_states.query('index >= 2020 and index < 2022')[state].plot(ax=ax2, label='Participation', color=color_pal[1])
    ax2.grid(False)
    axs[i].set_title(state)

## Hide any unused subplots
for j in range(i + 1, len(axs)):
    fig.delaxes(axs[j])

plt.tight_layout()
plt.show()

## Single state detail: California
state = 'California'
fig, ax = plt.subplots(figsize=(10, 5), sharex=True)
ax2 = ax.twinx()
uemp_states2 = uemp_states.asfreq('MS')
l1 = uemp_states2.query('index >= 2020 and index < 2022')[state].plot(ax=ax, label='Unemployment')
l2 = part_states.dropna().query('index >= 2020 and index < 2022')[state].plot(ax=ax2, label='Participation', color=color_pal[1])
ax2.grid(False)
ax.set_title(state)
fig.legend(labels=['Unemployment', 'Participation'])
plt.show()
