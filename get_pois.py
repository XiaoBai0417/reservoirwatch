import requests
import json
from urllib.parse import quote
import xlwt

# Conversion between the Baidu Coordinate System (BD-09) and the Mars Coordinate System (GCJ-02)
# i.e., converting Baidu coordinates to Google or Amap coordinates
# @param bd_lon: Longitude in the Baidu coordinate system (BD-09)
# @param bd_lat: Latitude in the Baidu coordinate system (BD-09)
# @returns: A tuple containing the converted coordinates (longitude, latitude) in the GCJ-02 system
import math
def bd09togcj02(bd_lon, bd_lat):
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


# * GCJ-02 to BD-09
# */
def gcj02tobd09(lng, lat):
    x_PI = 3.14159265358979324 * 3000.0 / 180.0
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_PI)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_PI)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


# wgs84 to amap
def wgs84togcj02(lng, lat):
    PI = 3.1415926535897932384626
    ee = 0.00669342162296594323
    a = 6378245.0
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


# WGS84 gcj02towgs84
def gcj02towgs84(localStr):
    lng = float(localStr.split(',')[0])
    lat = float(localStr.split(',')[1])
    PI = 3.1415926535897932384626
    ee = 0.00669342162296594323
    a = 6378245.0
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * PI)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng,lat * 2 - mglat]


def transformlat(lng, lat):
    PI = 3.1415926535897932384626
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * \
          lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 *
            math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320 *
            math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


def transformlng(lng, lat):
    PI = 3.1415926535897932384626
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 *
            math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 *
            math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 *
            math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


def Get_poi(key, city, types, page):
    '''
    Function to retrieve POI data from AMap API.
    key: API key registered with AMap
    city: Target city for POI data
    types: Type of POI data
    page: Current page number in API query
    '''
    # Setting the request header
    header = {
        'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"}

    # Constructing the URL
    url = 'https://restapi.amap.com/v3/place/text?key={}&types={}&city={}&page={}&output=json'.format(key, types, quote(city), page)

    # Sending the GET request
    r = requests.get(url, headers=header)
    # Setting the response encoding to 'utf-8'
    r.encoding = 'utf-8'
    # Decoding the response data to a string
    data = r.text
    return data

def Get_times(key, city, types):
    '''
    Function to control the number of API requests.
    '''
    page = 1
    # Creating an empty list for POIs
    poilist = []
    # Loop until 'count' from API response is '0'
    while True:
        # Retrieve data by calling the Get_poi function
        result = Get_poi(key, city, types, page)

        # Decoding the JSON formatted data
        content = json.loads(result)

        # Extracting the 'pois' field from the content
        pois = content['pois']

        # Appending POI data to the list
        for i in range(len(pois)):
            poilist.append(pois[i])

        # Increment the page number
        page += 1

        # Exit the loop if 'count' is '0'
        if content['count'] == '0':
            break
    # Return the list containing POI data
    return poilist

def write_to_excel(poilist, city, types):
    '''
    Function to write the list of POIs to an Excel file.
    poilist: List of POIs
    city: City name, used in the filename of the Excel file
    types: POI category, also used for the filename
    '''
    # Creating a new Excel file
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    # Adding a new sheet to the Excel file
    sheet = book.add_sheet(types, cell_overwrite_ok=True)

    # Writing column titles
    sheet.write(0, 0, 'Longitude')
    sheet.write(0, 1, 'Latitude')
    sheet.write(0, 2, 'Count')
    sheet.write(0, 3, 'Name')
    sheet.write(0, 4, 'Address')
    sheet.write(0, 5, 'District Name')

    # Writing data to the sheet
    for i in range(len(poilist)):
        name = poilist[i]['name']
        location = poilist[i]['location']
        address = poilist[i]['address']
        adname = poilist[i]['adname']
        lng, lat = location.split(",")

        # Coordinate transformation
        lng, lat = gcj02towgs84(float(lng), float(lat))

        # Writing row data
        sheet.write(i + 1, 0, lng)
        sheet.write(i + 1, 1, lat)
        sheet.write(i + 1, 2, 1)
        sheet.write(i + 1, 3, name)
        sheet.write(i + 1, 4, address)
        sheet.write(i + 1, 5, adname)

    # Saving the Excel file
    book.save(city + "_" + types + '.xls')

# Replace with your AMap API key
key = '**********'

# List of POI types you're interested in
types = ['Park Plaza', 'reservoir']

# It is recommended to divide large areas into smaller regions to ensure complete data collection
city_list = ['Baiyun District', 'Tianhe District', 'Yuexiu District', 'Huangpu District']

# Iterate over each region in the city_list
for city in city_list:
    # Iterate over each POI category
    for type in types:
        poi = Get_times(key, city, type)
        print('Current city: ' + str(city) + ', Category: ' + str(type) + ", Total data: " + str(len(poi)) + " items")
        write_to_excel(poi, city, type)
        print('*' * 50 + 'Category: ' + str(type) + " written successfully" + '*' * 50)
print('==== Data retrieval complete ====')
