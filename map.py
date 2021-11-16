import folium

def style_function(feature):
    return {
        "opacity": 0.1,
        "color": '#F76552',
    }


routes_map = folium.Map(
    location=[50.9411228, 6.9409058],
    zoom_start=11.5,
    tiles='Stamen Toner',
)
folium.GeoJson('data/routes_20210301_20210314.json', name='route2',
               style_function=style_function).add_to(routes_map)
routes_map.save('routes_index.html')

# points_map = folium.Map(
#     location=[50.9411228, 6.9409058],
#     zoom_start=11.5,
#     tiles='Stamen Toner',
# )
# folium.GeoJson('data/feature_collection_points.json',
#                ).add_to(points_map)
# points_map.save('points_index.html')
