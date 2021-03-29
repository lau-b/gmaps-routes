import pandas as pd


def create_routes(df):
    """
    Expects a DataFrame with the exact following columns, which describe the
    first and last time a bike was seen at certain location:
    "bike_number","longitude","latitude", "first_seen_at" and "last_seen_at".

    Returns a DataFrame, that creates routes out of the positional information
    by shifting the longitude, latitude and first seen information of the next
    row into the previous. The resulting last row per bike now contains NaNs
    and is therefore dropped. It is also not a route.
    """
    df.sort_values(['bike_number', 'first_seen_at'], inplace=True)
    df[['lng_dest', 'lat_dest', 'end_at']] = df.groupby(
        'bike_number').shift(-1)[['longitude', 'latitude', 'first_seen_at']]
    df.dropna(inplace=True)
    df.rename(columns={
        'longitude': 'lng_start',
        'latitude': 'lat_start',
        'last_seen_at': 'start_at'},
        inplace=True)
    df.reset_index(inplace=True)
    df.drop(columns=['index', 'first_seen_at'], inplace=True)
    return df


if __name__ == '__main__':
    bike_locations = pd.read_csv('data/bike_locations.csv')
    routes = create_routes(bike_locations)
    routes.to_csv('data/bike_routes.csv', header=False, index=False)
