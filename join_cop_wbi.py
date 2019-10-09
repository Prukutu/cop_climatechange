""" Script to join estimated loss of A/C COP due to increases in temperature
    due to climate change to World Bank socioeconomic indicators. The latter
    only exist by country (by definition), so at best we'll get a value for
    each country. Some smaller countries might get skipped because GCMs are
    very coarse.
"""


import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import pandas as pd

from shapely.geometry import Point
import seaborn as sns


def load_loss_GDF(filename, lon, lat):
    """ Convert a csv of COP values representing global model pixels
        to a GeoDataFrame using central lat/lon coordinates.
    """
    df = pd.read_csv(filename)
    x, y = np.meshgrid(lon, lat)
    coords = [Point(xval, yval) for xval, yval in zip(x.ravel(), y.ravel())]
    
    df['geometry'] = coords
    df = gpd.GeoDataFrame(df)
    df.crs = {'init': 'epsg:4326'}
    return df


lat = np.arange(-89.5, 90, 1.0)
lon = np.arange(0, 360, 1.0)
lon[lon >= 180] = lon[lon >= 180] - 360

cop = load_loss_GDF('cop_loss.csv', lon, lat)
country = gpd.read_file('wdb_shapefile.shp')

# use spatial join to combine COP data to world bank GDP (PPP) per capita
joined = gpd.sjoin(country, cop)

joined_percountry = joined.groupby(by='ISO_A3_EH').mean()
country.set_index('ISO_A3_EH', inplace=True)

for rcp in ('rcp45', 'rcp85'):
    # Add mean COP loss value to each row in country
    country.loc[joined_percountry.index, rcp] = joined_percountry[rcp].values

# Set the USL style
plt.style.use('../../mpl_styles/usl-presentations')

# Some exploratory figures to peek into the relationship between socioeconomic
# and climate impact on COP
fig1, ax1 = plt.subplots(figsize=(4.5, 4.5))
alpha = 0.75
colors = ('#004466', '#BE3526')
im1 = sns.scatterplot(x='2016', 
                      y='rcp45', 
                      data=country,
                      color='#004466', 
                      ax=ax1,
                      label='RCP4.5',
                      alpha=alpha)

im1 = sns.scatterplot(x='2016', 
                      y='rcp85', 
                      data=country,
                      color='#BE3526', 
                      ax=ax1,
                      alpha=alpha,
                      label='RCP8.5',
                      legend='brief')
ax1.get_legend().set_frame_on(True)
# ax1.set_xlim(0, 60000)
ax1.set_xlabel('GDP (PPP) per capita')
ax1.set_ylabel('COP Reduction (%)')

fig1.savefig('scatter_cop_gdp_ppp.png', dpi=300)

# Drawbox the bar plot
fig2, ax2 = plt.subplots(figsize=(6, 4))
joined_percontinent = joined.groupby(by='CONTINENT').mean()
joined_percontinent['cont'] = joined_percontinent.index
# Melt the variables so it's easier to use seaborn
databar = pd.melt(joined_percontinent, 
                  id_vars='cont',
                  value_vars=('rcp45', 'rcp85'),
                  var_name='rcp',
                  value_name='cop_loss')

databar.replace(to_replace='rcp45', value='RCP4.5', inplace=True)
databar.replace(to_replace='rcp85', value='RCP8.5', inplace=True)

bar_order = joined_percontinent.sort_values(by='2016').index 
sns.barplot(x='cont', 
            y='cop_loss',
            hue='rcp',
            data=databar, 
            palette=colors,
            order=bar_order)

ax2.set_xlabel('Continent')
ax2.set_ylabel('COP Reduction (%)')
ax2.set_title('A/C Performance loss by continent', loc='left')
fig2.savefig('continent_loss_bar.png', dpi=300)


fig3, ax3 = plt.subplots(figsize=(7, 5))

databox = pd.melt(joined, 
                  id_vars='CONTINENT',
                  value_vars=('rcp45', 'rcp85'),
                  var_name='rcp',
                  value_name='cop_loss')

databox.replace(to_replace='rcp45', value='RCP4.5', inplace=True)

databox.replace(to_replace='rcp85', value='RCP8.5', inplace=True)

lw = 1.5  # linewidths to use

box = sns.boxplot(x='CONTINENT', 
                  y='cop_loss', 
                  data=databox,
                  linewidth=lw,
                  hue='rcp',
                  palette=colors,
                  order=bar_order,
                  fliersize=0,
                  width=0.5)

# I hate the default look of the boxplots, so spruce them up.
# Maybe make this a function at some point?
for n, artist in enumerate(ax3.artists):
    fcolor = artist.get_facecolor()
    artist.set_edgecolor(fcolor)
    artist.set_facecolor('none')
    
    for m in range(n*6, n*6+6):
        line = ax3.lines[m]
        line.set_color(fcolor)
        line.set_mfc(fcolor)
        line.set_mec(fcolor)

for legpatch in ax3.get_legend().get_patches():
    col = legpatch.get_facecolor()
    legpatch.set_edgecolor(col)
    legpatch.set_facecolor('none')
    legpatch.set_linewidth(lw)

ax3.get_legend().set_title('')
ax3.set_ylim(-3, 11)
ax3.set_xlabel('Continent')
ax3.set_ylabel('COP Reduction (%)')
ax3.set_title('A/C Performance loss by continent', loc='left')
fig3.savefig('continent_loss_box.png', dpi=300)

