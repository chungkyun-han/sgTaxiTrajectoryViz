import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/..')
from sgTaxiCommon.fileHandling_functions import path_merge, check_dir_create
#
import wx
app = wx.App(False)
#
MAX_FRAME_RATE = 30  # 30 refreshes per second (SHOULD be integer)
SPEED_BASE = 2**0.5
TIMER_INTERVAL = 1000 // MAX_FRAME_RATE  # milliseconds
SCENE_REFRESH_CYCLES = [1, 2, 3, 5, 6, 10, 15, 30]
DEVICE_DRAW_FONT = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
DEFAULT_FONT = wx.Font(20, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT)
BIG_BOLD_FONT = wx.Font(24, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.BOLD)

dpaths = {}
dpaths['res'] = 'res'
dpaths['bgImgs'] = path_merge(dpaths['res'], 'bgImgs')
dpaths['z_data'] = 'z_data'
for dn in ['driverLogGPS', 'bgXY']:
    dpaths[dn] = path_merge(dpaths['z_data'], dn)
dpaths['z_html'] = 'z_html'

for dn in ['res',
              'bgImgs',
           'z_data',
              'driverLogGPS', 'bgXY',
           'z_html']:
    try:
        check_dir_create(dpaths[dn])
    except OSError:
        pass