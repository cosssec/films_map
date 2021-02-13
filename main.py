'''
This module works with the database of films, their year and location of
directing. Creates map with 3 layers which shows 10 films produced in the
year the user has chosen and that are located the closest
to the user's location.
'''
import folium
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from geopy import distance
from ipyleaflet import Map, AntPath, MeasureControl


def read_data(path: str):
    """
    Read file from given path. Return list of strings with text.
    """
    with open(path, "r", encoding="utf-8") as file:
        text = file.readlines()
    lines = []
    smalline = []

    for line in text:
        line = line.strip()
        line = line.split('\t')
        line = list(filter(lambda a: a != '', line))
        lines.append(line)
    new_list = []
    lines = lines[15:]

    for line in lines:

        try:
            line1 = line[0].split('{')
        except:
            IndexError

        if len(line1) == 2:
            del line1[1]

        try:
            line[0] = line1
        except:
            IndexError

        try:
            line.extend(line[0])
        except:
            IndexError

        try:
            del line[0]
        except:
            IndexError

        line.reverse()

        if len(line) == 3:
            del line[1]

        try:
            line1 = line[0].split('(')
        except:
            IndexError
        try:
            line1.append(line[1])
            line1[1] = line1[1][:4]
            if len(line1) >= 4:
                del line1
            new_list.append(line1)
        except:
            IndexError

    set_tuples = set(tuple(row) for row in new_list)

    return [list(item) for item in set_tuples]


# print(read_data("locations2222.list"))

def filter_films(base):
    '''
    Creates base of films only of needed year.
    '''

    new_base = []
    for line in base:
        if line[1] == year:
            new_base.append(line)
    return new_base


# print(filter_films(read_data("locations2222.list")))

def add_location(base):
    '''
    Turns location of every film into coordinates.
    '''
    try:
        geolocator = Nominatim(user_agent="mandaryna")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        for line in base:
            location = geolocator.geocode(line[2])
            try:
                coords = (location.latitude, location.longitude)
            except:
                continue
            line.append(coords)
        return base
    except:
        GeocoderUnavailable
        pass


# print(add_location(filter_films(read_data("locations2222.list"))))


def find_distance(base):
    '''
    Finds distance between user's location and films location and creates \
    base that consists of 10 films and their locations.
    '''

    place_coords = tuple(place_coords_str.split(', '))
    lst_distances = []
    riadok = []

    for line in base:
        film_coords = line[-1]
        try:
            distance = geopy.distance.geodesic(place_coords, film_coords).km
            riadok = [line[0], line[1], place_coords, film_coords, distance]
            lst_distances.append(riadok)
            riadok = []
        except:
            ValueError
            pass

    return sorted(lst_distances, key=lambda x: x[-1])[:10]


# print(find_distance(add_location(filter_films\
# (read_data("locations2222.list")))))


def create_map(base):
    '''
    Creates map with 3 layers.
    '''

    map = folium.Map(location=[place_coords_str.split(', ')[
        0], place_coords_str.split(', ')[1]], zoom_start=10)

    myloc = folium.FeatureGroup(name="My location")
    myloc.add_child(folium.Marker(
        location=[50.71900700787894, 25.310020500171138], popup="hi im there",
        icon=folium.Icon()))
    map.add_child(myloc)

    yourloc = folium.FeatureGroup(name="Your location")
    yourloc.add_child(folium.Marker(
        location=[place_coords_str.split(', ')[0],
                  place_coords_str.split(', ')[1]],
        popup="hi ur there", icon=folium.Icon()))
    map.add_child(yourloc)

    locs = folium.FeatureGroup(name="Films locations")
    for line in base:
        locs.add_child(folium.Marker(
            location=[list(line[-2])[0], list(line[-2])[1]],
            popup=line[0], icon=folium.Icon()))
        map.add_child(locs)

    map.add_child(folium.LayerControl())
    map.save('MapFilms.html')


if __name__ == "__main__":
    print("Please enter a year you would like to have a map for:")
    year = str(input())
    print("Please enter your location (format: lat, long):")
    place_coords_str = str(input())
    print("Map is generating...Please wait...")
    create_map(find_distance(add_location(
        filter_films(read_data("small_locations.list")))))
    print("Finished. Please have look at the map MapFilms.html")
