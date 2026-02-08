import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import numpy as np

import helpers

plotting = '+proj=aeqd +lat_0=90'

world_file = '../IPUMSI_world_release2024/IPUMSI_world_release2024.shp'

eu_file = '../NUTS_RG_01M_2024_4326.shp/NUTS_RG_01M_2024_4326.shp'
uk_file = '../ITL2_JAN_2025_UK_BUC_-2862694911944528901/ITL2_JAN_2025_UK_BUC.shp'
us_file = '../cb_2018_us_county_500k/cb_2018_us_county_500k.shp'
ca_file = '../lcd_000b21a_e/lcd_000b21a_e.shp'

fig, ax = plt.subplots(figsize=(10, 10))

helpers.plot_world(world_file, plotting)
helpers.plot_contintent('europe', ax)
helpers.plot_contintent('usa', ax)
helpers.plot_contintent('canada', ax)
helpers.plot_homes(ax)

args_lines = {
    'linewidth': 1,
    'linestyle': 'dotted',
    'edgecolor': 'cornsilk',
    'facecolor': 'none',
    'zorder': 100,
    'alpha': 0.5
}

for lat in np.linspace(0, 90, 10):
    geometry = Polygon([[long, lat] for long in np.linspace(-180, 180, 100)])
    circle = gpd.GeoSeries(geometry, crs="EPSG:4326")
    circle = circle.to_crs(plotting)
    circle.plot(ax=ax, **args_lines)

for long in np.linspace(-180, 180, 37)[1:]:
    geometry = Polygon([[long, lat] for lat in np.linspace(0, 90, 100)])
    circle = gpd.GeoSeries(geometry, crs="EPSG:4326")
    circle = circle.to_crs(plotting)
    circle.plot(ax=ax, **args_lines)

plt.xlim(helpers.xmin*1.1, helpers.xmax*1.1)
plt.ylim(helpers.ymin*1.1, helpers.ymax*1.1)
plt.xticks([])
plt.yticks([])
ax.set_facecolor('dodgerblue')
plt.tight_layout()
print("Saving figure...")
plt.savefig('travels.pdf')
# plt.xkcd()
plt.savefig('travels.png')
plt.close()
