from __init__ import *
#
import GPS_xyCoords_converter as GPS_xyDrawing
from sgTaxiCommon.fileHandling_functions import path_merge, check_path_exist, load_pickle_file, save_pickle_file
#
from datetime import datetime
import csv
#
VEHICLE_STATE_COLARS = [
            wx.Brush(wx.Colour(200, 200, 200)),
            wx.Brush(wx.Colour(225, 225, 225)),
            wx.Brush(wx.Colour(0, 0, 255)),
            wx.Brush(wx.Colour(255, 193, 193)),
            wx.Brush(wx.Colour(0, 255, 0)),
            wx.Brush(wx.Colour(255, 255, 0))]

ST_FREE, ST_POB = 0, 5
COL_FREE = wx.Brush(wx.Colour(0, 255, 0))
COL_POB = wx.Brush(wx.Colour(255, 0, 0))
COL_ETC = wx.Brush(wx.Colour(0, 0, 255))
VEH_SIZE = 5


if_dpath = dpaths['driverLogGPS']
if_prefix = 'driverLogGPS-'


class driver(object):
    def __init__(self, did):
        self.did = did
        self.dt_lonlat_state = self.get_trajectory()
        #
        self.curLog_index = 0
        #
        self.prev_update_time = None
        self.prev_x, self.prev_y = None, None
        self.state = None
        #
        self.next_update_time = None
        self.next_x, self.next_y = None, None
        #
        self.time_interval = None
        #
        self.size = VEH_SIZE

    def __repr__(self):
        return 'did %d' % self.did

    def get_trajectory(self):
        ofpath = path_merge(if_dpath, '%s%d.pkl' % (if_prefix, self.did))
        if check_path_exist(ofpath):
            dt_lonlat_state = load_pickle_file(ofpath)
        else:
            ifpath = path_merge(if_dpath, '%s%d.csv' % (if_prefix, self.did))
            dt_lonlat_state = []
            with open(ifpath, 'rb') as logFile:
                reader = csv.reader(logFile)
                header = reader.next()
                # header: time,vehicle-id,driver-id,longitude,latitude,speed,state
                hid = {h: i for i, h in enumerate(header)}
                for row in reader:
                    dt = datetime.fromtimestamp(eval(row[hid['time']]))
                    lon, lat = map(eval, [row[hid[cn]] for cn in ['longitude', 'latitude']])
                    dt_lonlat_state += [(dt, lon, lat, int(row[hid['state']]))]
            save_pickle_file(ofpath, dt_lonlat_state)
        return dt_lonlat_state

    def set_logIndex(self, given_dt, scale, min_x, min_y):
        if self.prev_update_time == None:
            self.update_prev_next_position(scale, min_x, min_y)
        while True:
            if self.prev_update_time <= given_dt and given_dt < self.next_update_time:
                break
            self.curLog_index += 1
            self.update_prev_next_position(scale, min_x, min_y)
        if self.prev_update_time != given_dt:
            self.curLog_index += 1
            self.update_prev_next_position(scale, min_x, min_y)

    def update_prev_next_position(self, scale, min_x, min_y):
        dt, lon, lat, state = self.dt_lonlat_state[self.curLog_index]
        self.prev_update_time = dt
        actualX, actualY = GPS_xyDrawing.convert_GPS2xy(scale, lon, lat)
        self.prev_x, self.prev_y = self.x, self.y = actualX - min_x, actualY - min_y
        self.state = state
        #
        self.next_update_time = self.dt_lonlat_state[self.curLog_index + 1][0]
        nextLon, nextLat = self.dt_lonlat_state[self.curLog_index + 1][1:3]
        actualX, actualY = GPS_xyDrawing.convert_GPS2xy(scale, nextLon, nextLat)
        self.next_x, self.next_y = actualX - min_x, actualY - min_y
        #
        self.time_interval = (self.next_update_time - self.prev_update_time).seconds
        if self.time_interval == 0:
            try:
                self.update_prev_next_position(scale, min_x, min_y)
            except RuntimeError:
                pass

    def update_trajectory(self, cur_dt, scale, min_x, min_y):
        if self.next_update_time <= cur_dt:
            self.curLog_index += 1
            self.update_prev_next_position(scale, min_x, min_y)
        else:
            td = cur_dt - self.prev_update_time
            time_passed = td.seconds + td.microseconds / float(1e6)
            if self.time_interval == 0:
                self.x = self.prev_x
                self.y = self.prev_y
            else:
                ratio = time_passed / float(self.time_interval)
                self.x = self.prev_x + (self.next_x - self.prev_x) * ratio
                self.y = self.prev_y + (self.next_y - self.prev_y) * ratio

    def draw(self, gc):
        old_tr = gc.GetTransform()
        gc.Translate(self.x, self.y)
        #
        gc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
        state, col = None, None
        if self.state == ST_FREE:
            col = COL_FREE
            state = 'FREE'
        elif self.state == ST_POB:
            col = COL_POB
            state = 'POB'
        else:
            col = COL_ETC
            state = 'ETC'
        gc.SetBrush(col)
        gc.DrawEllipse(-self.size / 2.0, -self.size / 2.0,
                       self.size, self.size)
        #
        gc.DrawLines([(0, 0), (self.size / 2.0, self.size * 1.5)])
        gc.SetFont(DEFAULT_FONT)
        gc.DrawText('%s(%s)' % (self.did, state), self.size / 2.0, self.size * 1.5)
        gc.SetTransform(old_tr)


if __name__ == '__main__':
    print driver(32768).dt_lonlat_state





