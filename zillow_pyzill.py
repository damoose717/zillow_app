import pyzill
import pandas as pd
import math
from geopy.geocoders import Nominatim

from flask import Flask

app = Flask(__name__)

#pagination is for the list that you see at the right when searching
#you don't need to iterate over all the pages because zillow sends the whole 
# data on mapresults at once on the first page
#however the maximum result zillow returns is 500, so if mapResults is 500
#try playing with the zoom or moving the coordinates, pagination won't help 
# because you will always get at maximum 500 results

pagination = 1

coordinates = [
    (34.04822022478224, -118.54380808534304),
    (33.94286974516112, -118.40348813649958),
    (34.09105382290195, -118.36531820536337),
    (34.07427520976152, -118.3594909268181),
]
ne_lat = max([coord[0] for coord in coordinates])
ne_long = max([coord[1] for coord in coordinates])
sw_lat = min([coord[0] for coord in coordinates])
sw_long = min([coord[1] for coord in coordinates])

geolocator = Nominatim(user_agent="my-app")

fieldnames = [
    "type",
    "address",
    "zipcode",
    "price",
    "area",
    "beds",
    "baths",
    "detailUrl",
    "listedBy",
    "isBuilding",
    "flexFieldText",
    "daysOnZillow",
    "isFavorite",
    "listingType",
]

cols_to_consolidate = [
    "area",
    "beds",
    "baths",
]

cols_to_rename = {
    "statusText": "type",
    "info3String": "listedBy",
    "info6String": "listedBy",
    "timeOnZillow": "daysOnZillow",
}

def get_zipcode(address):
    zip = address.split(" ")[-1]
    return zip if zip.isnumeric() else None


def get_data(
        location="Los Angeles, CA",
        radius=10,
        min_beds=None,
        max_beds=None,
        min_bathrooms=None,
        max_bathrooms=None,
        min_price=None,
        max_price=None
    ) -> list:
    geolocation = geolocator.geocode(location)
    lat = geolocation.latitude
    long = geolocation.longitude 
    radius = int(radius)
    ne_lat = lat + (180/math.pi)*(radius/3963.1)  
    ne_long = long + (180/math.pi)*(radius/3963.1)  
    sw_lat = lat - (180/math.pi)*(radius/3963.1)  
    sw_long = long - (180/math.pi)*(radius/3963.1)  
    # print(f"northeast point: ({ne_lat}, {ne_long})")
    # print(f"southwest point: (f{sw_lat}, {sw_long})")
    print('min beds', min_beds, type(min_beds))

    results_sale = pyzill.for_sale(
        pagination, 
        search_value="",
        min_beds=min_beds, max_beds=max_beds,
        min_bathrooms=min_bathrooms, max_bathrooms=max_bathrooms,
        min_price=min_price, max_price=max_price,
        ne_lat=ne_lat, ne_long=ne_long, sw_lat=sw_lat, sw_long=sw_long,
        zoom_value=10,
    )

    map_results = results_sale['mapResults']
    # print(f"found {len(map_results)} results")

    # with open("./jsondata_sale.json", "w") as f:    
    #     f.write(json.dumps(results_sale, indent=4))

    # with open("./map_results.json", "w") as f:
    #     f.write(json.dumps(map_results, indent=4))

    return map_results

def generate_df(map_results) -> pd.DataFrame:
    df = pd.DataFrame(map_results)
    df = df.loc[df.address.notnull()]
    df["zipcode"] = df["address"].apply(get_zipcode)
    df["timeOnZillow"] = (df.timeOnZillow / 1000 / 60 / 60 / 24).astype(int)
    for col in cols_to_consolidate:
        min_col = f"min{col.title()}"
        if min_col in df.columns:
            df[col] = df[col].fillna(df[min_col])
    df = df.rename(columns=cols_to_rename)
    df = df[[name for name in fieldnames if name in df.columns]]
    return df

    # df.to_csv("./map_results.csv")
    # print('written to ./map_results.csv')
