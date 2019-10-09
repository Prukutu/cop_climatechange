import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.gridspec as gridspec
from matplotlib.offsetbox import AnchoredText
import pandas as pd
import numpy as np

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.util import add_cyclic_point


def mean_anomaly(early, late):
    delta = 100*(early - late)/early

    return delta.mean(axis=1)


def label_fractional_loc(ax, s, x, y):
    x0, x1, y0, y1 = ax.get_extent()
    
    newx = x0 + x*(x1 - x0)
    newy = y0 + y*(y1 - y0)
    
    txt = ax.text(newx, newy, s, zorder=101)
    
    return txt


plt.style.use('../../mpl_styles/usl-presentations')
fig = plt.figure(figsize=(5, 5))
gs = gridspec.GridSpec(3, 1,
                       hspace=.33,
                       height_ratios=(10, 10, 1))

scenarios = ('rcp45', 'rcp85')
dropcol = 'Unnamed: 0'
bounds = np.arange(0, 13, 2)

labels = ('a', 'b')
# Create a linear color map based on Claudia's Reds
cmap = matplotlib.colors.LinearSegmentedColormap.from_list('ClaudiaReds', 
                                                               ['#F2D7D4', '#BE3526'], 
                                                               N=7) 
cmap.set_under('#67A3C2')
cmap.set_over('#BE3526')
norm = matplotlib.colors.BoundaryNorm(bounds, ncolors=cmap.N, clip=False)

proj = ccrs.EckertIV()

# Save COP loss data to csv file
df_out = pd.DataFrame(columns=scenarios)

for n, rcp in enumerate(scenarios):

    lat = np.arange(-89.5, 90, 1.0)
    lon = np.arange(0, 360, 1.0)
    
#     ax = add_subplot(2, 1, n+1, projection=proj)
    ax = plt.subplot(gs[n], projection=proj)

    early_df = pd.read_csv('early_' + rcp + '_cop_mean.csv').drop(columns=dropcol)
    late_df = pd.read_csv('late_' + rcp + '_cop_mean.csv').drop(columns=dropcol)


    data = mean_anomaly(early_df, late_df).values.reshape((180, 360))
    df_out[rcp] = data.ravel()
    data, lon = add_cyclic_point(data, coord=lon)

    ax.add_feature(cartopy.feature.OCEAN, 
                   zorder=100, 
                   edgecolor='#555456',
                   facecolor='#DDDDDD')
    im = ax.contourf(lon, 
                     lat, 
                     data, 
                     bounds,
                     transform=ccrs.PlateCarree(),
                     cmap=cmap,
                     norm=norm,
                     extend='both')
    
    txt = label_fractional_loc(ax, labels[n], 0.12, 0.05)

cbarax = plt.subplot(gs[2],
                     position=[.25, .1, .5, .02])
cbar = plt.colorbar(im, 
                    orientation='horizontal', 
                    extend='both',
                    cax=cbarax,
                    use_gridspec=True)

cbar.ax.set_title('COP Reduction (%)', 
                  fontsize=12, 
                  loc='left',
                  pad=6)

fig.suptitle('A/C Performance Reduction\n(2006-2036 to 2070-2099)',
            fontsize=12,
            fontdict=dict(fontweight='bold'))
fig.savefig('global_cop_loss.png', bbox_inches='tight', dpi=300)
fig.savefig('global_cop_loss.svg', bbox_inches='tight')

df_out.to_csv('cop_loss.csv')
