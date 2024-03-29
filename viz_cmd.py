from __init__ import *
#
from sgTaxiCommon.fileHandling_functions import path_merge
#
import wx
import os.path as opath

# message IDs
ID_CONTROL_PLAY = wx.NewId()
ID_CONTROL_S_UP = wx.NewId()
ID_CONTROL_S_DOWN = wx.NewId()
ID_CONTROL_SKIP = wx.NewId()
# ID_CONTROL_F_UP = wx.NewId()
# ID_CONTROL_F_DOWN = wx.NewId()


res_dpath = dpaths['res']

def set_command_interface(frame):
    frame.mbar = wx.MenuBar()
    cmenu = wx.Menu()
    cmenu.AppendCheckItem(ID_CONTROL_PLAY, '&Play')
    cmenu.Append(ID_CONTROL_S_UP, 'Speed &Up')
    cmenu.Append(ID_CONTROL_S_DOWN, 'Speed &Down')
    cmenu.AppendSeparator()
    cmenu.Append(ID_CONTROL_SKIP, 'S&kip to Next Event')
    cmenu.AppendSeparator()
    # cmenu.Append(ID_CONTROL_F_UP, 'Frame &Rate Up')
    # cmenu.Append(ID_CONTROL_F_DOWN, 'Frame Ra&te Down')
    # cmenu.AppendSeparator()
    frame.mbar.Append(cmenu, '&Control')
    frame.SetMenuBar(frame.mbar)
    # tool bar
    frame.tbar = frame.CreateToolBar()
    frame.tbar.AddCheckTool(ID_CONTROL_PLAY, load_icon('play.bmp'))
    frame.tbar.AddSimpleTool(ID_CONTROL_S_DOWN, load_icon('speed_down.bmp'))
    frame.tbar.AddSimpleTool(ID_CONTROL_S_UP, load_icon('speed_up.bmp'))
    frame.tbar.AddSeparator()
    frame.tbar.AddSimpleTool(ID_CONTROL_SKIP, load_icon('skip.bmp'))
    # frame.tbar.AddSeparator()
    # frame.tbar.AddSimpleTool(ID_CONTROL_F_DOWN, load_icon('frame_down.bmp', bd))
    # frame.tbar.AddSimpleTool(ID_CONTROL_F_UP, load_icon('frame_up.bmp', bd))
    frame.tbar.Realize()
    #
    frame.Bind(wx.EVT_MENU, frame.OnPlay, id=ID_CONTROL_PLAY)
    frame.Bind(wx.EVT_MENU, frame.OnSpeed, id=ID_CONTROL_S_UP)
    frame.Bind(wx.EVT_MENU, frame.OnSpeed, id=ID_CONTROL_S_DOWN)
    frame.Bind(wx.EVT_MENU, frame.OnSkip, id=ID_CONTROL_SKIP)
    # frame.Bind(wx.EVT_MENU, frame.OnFrameRate, id=ID_CONTROL_F_UP)
    # frame.Bind(wx.EVT_MENU, frame.OnFrameRate, id=ID_CONTROL_F_DOWN)


def load_icon(path):
    bmp = wx.Bitmap(path_merge(res_dpath, path), wx.BITMAP_TYPE_BMP)
    bmp.SetMaskColour(wx.Colour(0, 128, 128))
    return bmp