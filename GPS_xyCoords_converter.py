import __init__
#
from sgTaxiCommon.geo_functions import get_sgBorder, get_sgRoads, get_sgGrid, get_sgBuildings
from sgTaxiCommon.fileHandling_functions import path_merge, check_path_exist, check_dir_create, \
                                                save_pickle_file, load_pickle_file
#
xyCoords = 'xyCoords'
try:
    check_dir_create(xyCoords)
except OSError:
    pass


min_lon, max_lon = 1e400, -1e400
min_lat, max_lat = 1e400, -1e400
#
sgBorder = get_sgBorder()
for lon, lat in sgBorder:
    if lon < min_lon:
        min_lon = lon
    if lon > max_lon:
        max_lon = lon
    if lat < min_lat:
        min_lat = lat
    if lat > max_lat:
        max_lat = lat


def convert_GPS2xy(scale, lon, lat):
    x = (lon - min_lon) * scale
    y = (max_lat - (lat - min_lat)) * scale
    return x, y

def convert_xy2GPS(scale, x, y):
    lon = 0
    lat = 0
    return lon, lat


def get_sgBoarder_xy(scale):
    ofpath = path_merge(xyCoords, 'sgBorder_xy(s%d).pkl' % scale)
    if not check_path_exist(ofpath):
        sgBorder_xy = []
        for lon, lat in sgBorder:
            x, y = convert_GPS2xy(scale, lon, lat)
            sgBorder_xy += [(x, y)]
        save_pickle_file(ofpath, sgBorder_xy)
    else:
        sgBorder_xy = load_pickle_file(ofpath)
    return sgBorder_xy


def get_sgGrid_xy(scale):
    ofpath = path_merge(xyCoords, 'sgGrid_xy(s%d).pkl' % scale)
    if check_path_exist(ofpath):
        sgGrid_xy = load_pickle_file(ofpath)
    else:
        sgGrid_xy = []
        lons, lats = get_sgGrid()
        for lon in lons:
            sx, sy = convert_GPS2xy(scale, lon, lats[0])
            ex, ey = convert_GPS2xy(scale, lon, lats[-1])
            sgGrid_xy += [[(sx, sy), (ex, ey)]]
        for lat in lats:
            sx, sy = convert_GPS2xy(scale, lons[0], lat)
            ex, ey = convert_GPS2xy(scale, lons[-1], lat)
            sgGrid_xy += [[(sx, sy), (ex, ey)]]
        save_pickle_file(ofpath, sgGrid_xy)
    return sgGrid_xy


def get_sgGrid_hLines(scale):
    ofpath = path_merge(xyCoords, 'sgGrid_hLines(s%d).pkl' % scale)
    if check_path_exist(ofpath):
        sgGrid_hLines = load_pickle_file(ofpath)
    else:
        sgGrid_hLines = []
        lons, lats = get_sgGrid()
        for lat in lats:
            sx, sy = convert_GPS2xy(scale, lons[0], lat)
            ex, ey = convert_GPS2xy(scale, lons[-1], lat)
            sgGrid_hLines += [[(sx, sy), (ex, ey)]]
        save_pickle_file(ofpath, sgGrid_hLines)
    return sgGrid_hLines


def get_sgGrid_vLines(scale):
    ofpath = path_merge(xyCoords, 'sgGrid_vLines(s%d).pkl' % scale)
    if check_path_exist(ofpath):
        sgGrid_vLines = load_pickle_file(ofpath)
    else:
        sgGrid_vLines = []
        lons, lats = get_sgGrid()
        for lon in lons:
            sx, sy = convert_GPS2xy(scale, lon, lats[0])
            ex, ey = convert_GPS2xy(scale, lon, lats[-1])
            sgGrid_vLines += [[(sx, sy), (ex, ey)]]
        save_pickle_file(ofpath, sgGrid_vLines)
    return sgGrid_vLines


def get_sgRords_xy(scale):
    ofpath = path_merge(xyCoords, 'sgRoards_xy(s%d).pkl' % scale)
    if check_path_exist(ofpath):
        sgRoards_xy = load_pickle_file(ofpath)
    else:
        sgRoards_xy = []
        for _, coords in get_sgRoads():
            road_fd = []
            for lon, lat in coords:
                road_fd += [convert_GPS2xy(scale, lon, lat)]
            sgRoards_xy += [road_fd]
        save_pickle_file(ofpath, sgRoards_xy)
    return sgRoards_xy


def get_sgBuildings_xy(scale):
    ofpath = path_merge(xyCoords, 'sgBuildings_xy(s%d).pkl' % scale)
    if check_path_exist(ofpath):
        sgBuildings_xy = load_pickle_file(ofpath)
    else:
        sgBuildings_xy = []
        for _, coords in get_sgBuildings():
            road_fd = []
            for lon, lat in coords:
                road_fd += [convert_GPS2xy(scale, lon, lat)]
            sgBuildings_xy += [road_fd]
        save_pickle_file(ofpath, sgBuildings_xy)
    return sgBuildings_xy



if __name__ == '__main__':
    BASE_SCALE = 2500
    print get_sgBoarder_xy(BASE_SCALE * 1)
    # get_sgRoards_xy()
    # get_sgGrid_xy()