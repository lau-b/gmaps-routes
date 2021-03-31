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

def create_parking_locations(df):
    df.sort_values(['first_seen_at'], inplace=True)
    df.reset_index(inplace=True)
    df.drop(columns=['index', 'bike_number', 'last_seen_at'], inplace=True)
    df.set_index('first_seen_at', inplace=True)
    return df


if __name__ == '__main__':
    timeframe = '_20210301_20210314'
    bike_locations = pd.read_csv(f'data/bike_locations{timeframe}.csv')
    coordinates = create_parking_locations(bike_locations)
    coordinates.to_csv(f'data/bike_parking_locations{timeframe}.csv')

    # Anscheinend tranformieren die funktionen den bike_locations dataframe
    bike_locations = pd.read_csv(f'data/bike_locations{timeframe}.csv')
    routes = create_routes(bike_locations)
    routes.to_csv(f'data/bike_routes{timeframe}.csv',
                header=False, index=False)


