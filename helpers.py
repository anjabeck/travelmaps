country_cols = {
    'DE': 'peru',
    'AT': 'darkmagenta',
    'CH': 'fuchsia',
    'IT': 'gold',
    'SE': 'darkmagenta',
    'NO': 'fuchsia',
    'FI': 'peru',
    'DK': 'gold',
    'GB': 'peru',
    'IE': 'fuchsia',
    'TR': 'darkmagenta',
    'BG': 'fuchsia',
    'FR': 'darkmagenta',
    'ES': 'fuchsia',
    'CZ': 'fuchsia',
    'BE': 'fuchsia',
    'NL': 'gold',
    'HR': 'peru',
    'VA': 'darkmagenta',
}

country_cols_ca = {
    24: 'peru',
    35: 'fuchsia',
}

country_cols_us = {
    6: 'fuchsia',
    12: 'peru',
    17: 'darkmagenta',
    25: 'darkmagenta',
    36: 'gold',
    49: 'darkmagenta',
    32: 'peru',
    4: 'gold',
    34: 'fuchsia',
    33: 'fuchsia',
}

xmin, xmax = 0, 0
ymin, ymax = 0, 0

mycrs = "EPSG:4326"
plotting = '+proj=aeqd +lat_0=90'


def update_bounds(xmin_new, xmax_new, ymin_new, ymax_new):
    global xmin, xmax, ymin, ymax
    xmin = min(xmin, xmin_new)
    xmax = max(xmax, xmax_new)
    ymin = min(ymin, ymin_new)
    ymax = max(ymax, ymax_new)


def plot_world(world_file, plotting):
    import geopandas as gpd
    import matplotlib.pyplot as plt
    iso_europe = ['008', '040', '056', '070', '100', '191', '196', '203', '208', '233', '246', '250', '276', '300', '348', '352', '372', '380', '428', '440', '442', '470', '498', '499', '528', '578', '616', '620', '642', '688', '703', '705', '724', '752', '756', '792', '807', '826', '804', '807']

    world = gpd.read_file(world_file)
    world = world.to_crs(plotting)
    world = world[~world['CNTRY_CODE'].isin(['630', '840', '124']+iso_europe)]
    world.plot(ax=plt.gca(), linewidth=0.1, facecolor='black', zorder=0, alpha=0.3)#, rasterized=True)
    return


def plot_contintent(key, ax):
    import geopandas as gpd
    import matplotlib.pyplot as plt
    import pandas as pd

    args_state = {
        'linewidth': 0.1, 'facecolor': 'black', 'zorder': 0, 'alpha': 0.3
    }

    if key == 'europe':
        eu_file = '../NUTS_RG_01M_2024_4326.shp/NUTS_RG_01M_2024_4326.shp'
        uk_file = '../ITL2_JAN_2025_UK_BUC_-2862694911944528901/ITL2_JAN_2025_UK_BUC.shp' 
        nuts_eu = gpd.read_file(eu_file)
        nuts_uk = gpd.read_file(uk_file)
        nuts_uk['CNTR_CODE'] = 'GB'
        nuts_uk.rename(columns={'ITL325CD': 'NUTS_ID', 'ITL325NM': 'NUTS_NAME'}, inplace=True)
        nuts = gpd.GeoDataFrame(pd.concat([nuts_eu, nuts_uk.to_crs(mycrs)], ignore_index=True))
        nuts[(nuts['LEVL_CODE'] == 0)].to_crs(plotting).plot(ax=plt.gca(), **args_state)
        travel_key = 'travels_europe.csv'
        cols = country_cols
    elif key == 'usa':
        us_file = '../cb_2018_us_county_500k/cb_2018_us_county_500k.shp'
        us = gpd.read_file(us_file)
        us = us.to_crs(mycrs)
        us.to_crs(plotting).plot(ax=plt.gca(), **args_state)
        travel_key = 'travels_us.csv'
        cols = country_cols_us
    elif key == 'canada':
        ca_file = '../lcd_000b21a_e/lcd_000b21a_e.shp'
        ca = gpd.read_file(ca_file)
        ca = ca.to_crs(mycrs)
        ca.to_crs(plotting).plot(ax=plt.gca(), **args_state)
        travel_key = 'travels_ca.csv'
        cols = country_cols_ca

    travels = pd.read_csv(travel_key, header=0, sep='\t')
    unique = travels['state'].unique()

    for c in unique:
        travels_c = travels[travels['state'] == c]
        if key == 'europe':
            state = nuts[nuts['CNTR_CODE']==c].dissolve(by='CNTR_CODE').to_crs(plotting)
            geo_info = nuts[nuts['CNTR_CODE'] == c]
            if c in ['NO', 'SE', 'FI']:
                geo_info = geo_info[geo_info['LEVL_CODE'] == 3]
            elif c not in ['GB']:
                geo_info = geo_info[geo_info['LEVL_CODE'] == 2]
        elif key == 'usa':
            if len(str(c)) == 1:
                geo_info = us[us['STATEFP'] == "0"+str(c)]
            else:
                geo_info = us[us['STATEFP'] == str(c)]
            state = geo_info.dissolve(by='STATEFP').to_crs(plotting)
        elif key == 'canada':
            geo_info = ca[ca['PRUID'] == str(c)]
            state = geo_info.dissolve(by='PRUID').to_crs(plotting)
        state.plot(ax=ax, linewidth=0, zorder=0, facecolor='cornsilk')

        for i, row in travels_c.iterrows():
            long, lat = row['longitude'], row['latitude']
            found = False
            for poly in geo_info.geometry:
                if poly.contains(gpd.points_from_xy([long], [lat])):
                    plot = geo_info.loc[geo_info.geometry == poly].to_crs(plotting)
                    plot.plot(ax=ax, color=cols[c])
                    update_bounds(plot.geometry.values[0].bounds[0],
                                  plot.geometry.values[0].bounds[2],
                                  plot.geometry.values[0].bounds[1],
                                  plot.geometry.values[0].bounds[3])
                    found = True
                    if key in ['usa', 'canada']:
                        if state.geometry.area.values[0] * 0.2 > plot.geometry.area.values[0]:
                            # Find all neighboring polygons and plot them too
                            neighbors = geo_info[geo_info.touches(poly)]
                            for _, nrow in neighbors.iterrows():
                                nplot = geo_info.loc[geo_info.geometry == nrow.geometry].to_crs(plotting)
                                nplot.plot(ax=ax, color=cols[c])
                                update_bounds(nplot.geometry.values[0].bounds[0],
                                              nplot.geometry.values[0].bounds[2],
                                              nplot.geometry.values[0].bounds[1],
                                              nplot.geometry.values[0].bounds[3])
                    break
            if not found:
                print(f"{row['place']} not found in {c} ({long}, {lat})")

    return


args_homes = {
    'zorder': 201,
    's': u'\u2302',
    'fontsize': 10, 'ha': 'center', 'va': 'center',
    'color': 'k',
}


def plot_homes(ax):
    import pandas as pd
    import geopandas as gpd
    travels = pd.read_csv('homes.csv', header=0, sep='\t')
    for i, row in travels.iterrows():
        long, lat = row['longitude'], row['latitude']
        point = gpd.GeoSeries(gpd.points_from_xy([long], [lat]), crs=mycrs)
        point = point.to_crs(plotting)
        ax.text(point.x.values[0], point.y.values[0], **args_homes)
    return
