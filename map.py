# %%
from geojson import LineString
import folium

# %%
map = folium.Map(
    location=[50.9411228, 6.9409058],
    zoom_start=11.5,
    tiles='Stamen Toner',
)
folium.GeoJson(route_data, name='route1').add_to(map)
folium.GeoJson('data/route2.json', name='route2').add_to(map)
map
# %%
import os
route_data = os.path.join('data/route.json')
# %%
from geojson import MultiLineString, LineString
pew = LineString(
    [[50.99527713, 6.90742275],
        [50.99566189999999, 6.9084501],
        [50.9974464, 6.9078314],
        [50.9946792, 6.9000905],
        [50.9960834, 6.8983129],
        [50.9923857, 6.8926257],
        [50.9919637, 6.8922206],
        [50.9909972, 6.8935235],
        [50.9907998, 6.893892300000001],
        [50.9894207, 6.892273700000001],
        [50.9898828, 6.891292099999999]]
    )
pew

# %%
map = folium.Map(
    location=[50.9411228, 6.9409058],
    zoom_start=11.5,
    tiles='Stamen Toner',
)
folium.GeoJson(pew, name='pew').add_to(map)
map

# %%
import shapely2geojson

# %%
shapely2geojson.get_feature()
