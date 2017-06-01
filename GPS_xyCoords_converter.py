from __init__ import *
#
from sgTaxiCommon.geo_functions import get_sgBorder, get_sgRoads, get_sgGrid, get_sgBuildings
from sgTaxiCommon.fileHandling_functions import path_merge, check_path_exist, check_dir_create, \
                                                save_pickle_file, load_pickle_file
#
of_dpath = dpaths['bgXY']


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


def get_sgBoarderXY(scale):
    ofpath = path_merge(of_dpath, 'sgBorderXY(s%d).pkl' % scale)
    if not check_path_exist(ofpath):
        sgBorder_xy = []
        for lon, lat in sgBorder:
            x, y = convert_GPS2xy(scale, lon, lat)
            sgBorder_xy += [(x, y)]
        save_pickle_file(ofpath, sgBorder_xy)
    else:
        sgBorder_xy = load_pickle_file(ofpath)
    return sgBorder_xy


def get_sgGridXY(scale):
    ofpath = path_merge(of_dpath, 'sgGridXY(s%d).pkl' % scale)
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


def get_sgRordsXY(scale):
    ofpath = path_merge(of_dpath, 'sgRoardsXY(s%d).pkl' % scale)
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


def get_sgBuildingsXY(scale):
    ofpath = path_merge(of_dpath, 'sgBuildingsXY(s%d).pkl' % scale)
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


def convert_GPS2xy(scale, lon, lat):
    x = (lon - min_lon) * scale
    y = (max_lat - (lat - min_lat)) * scale
    return x, y


def get_sgLonsLatsXY(scale):
    ofpath = path_merge(of_dpath, 'sgLonsLatsXY(s%d).pkl' % scale)
    if check_path_exist(ofpath):
        sgLonsX, sgLatsY = load_pickle_file(ofpath)
    else:
        lons, lats = get_sgGrid()
        sgLonsX = [(lon - min_lon) * scale for lon in lons]
        sgLatsY = [(max_lat - (lat - min_lat)) * scale for lat in lats]
        sgLonsX.sort(); sgLatsY.sort()
        save_pickle_file(ofpath, [sgLonsX, sgLatsY])
    return sgLonsX, sgLatsY


if __name__ == '__main__':
    BASE_SCALE = 2500
    print get_sgBoarderXY(BASE_SCALE * 1)
    # get_sgRoards_xy()
    # get_sgGrid_xy()