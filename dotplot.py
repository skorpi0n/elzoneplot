from matplotlib import pyplot as plt
import requests
import pandas as pd

# Get data from file "Förbrukning och tillförsel per timme (i normaltid)"
# Statistics available at https://www.svk.se/om-kraftsystemet/kraftsystemdata/elstatistik/
url = 'https://www.svk.se/siteassets/1.om-kraftsystemet/kraftsystemdata/statistik/forbrukning-tillforsel-per-timme/n_fot2022-01-12.xls' # Data for 2022
r = requests.get(url)
open('Förbrukning och tillförsel per timme (i normaltid).xlsx', 'wb').write(r.content)

# Put the data in a dataframe.
df = pd.read_excel('Förbrukning och tillförsel per timme (i normaltid).xls', header=6, usecols=['Import/export'])
df.rename(columns={'Import/export': 'balance'}, inplace=True)

# Create columns.
df['hour']=df.index
df['y']=df['hour'].apply(lambda x: int(x/120))
df['x']=df['hour'].apply(lambda x: int(x%120))

# Set colors for export and import
export_color = 'orange'
import_color = 'grey'
df['color'] = df['balance'].apply(lambda x: export_color if x < 0 else import_color)

# Plot the data.
ax = df.plot(kind='scatter', x='x', y='y', c='color')

# Hide irrelevant names on axes.
ax.axes.get_xaxis().set_visible(False)
ax.axes.get_yaxis().set_visible(False)

# Show plot.
plt.show()
