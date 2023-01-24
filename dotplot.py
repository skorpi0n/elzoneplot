from matplotlib import pyplot as plt
import pandas as pd

# Import data and rename relevant column.
file_path = input()
df = pd.read_excel(file_path, header=6, usecols=['Import/export'])
df.rename(columns={'Import/export': 'balance'}, inplace=True)

# Create columns.
df['hour']=df.index
df['y']=df['hour'].apply(lambda x: int(x/120))
df['x']=df['hour'].apply(lambda x: int(x%120))

# Set export to orange and import to grey.
df['color'] = df['balance'].apply(lambda x: 'orange' if x < 0 else 'grey')

# Plot the data.
ax = df.plot(kind='scatter', x='x', y='y', c='color')

# Hide irrelevant names on axes.
ax.axes.get_xaxis().set_visible(False)
ax.axes.get_yaxis().set_visible(False)

# Show plot.
plt.show()
