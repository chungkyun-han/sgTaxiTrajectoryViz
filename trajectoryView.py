from __init__ import *
#
import GPS_xyCoords_converter as GPS_xyDrawing
import timeKeeper as tk
#
from sgTaxiCommon.fileHandling_functions import path_merge, check_path_exist, check_dir_create
from sgTaxiCommon.geo_functions import viz_aZone_html
#
import os.path as opath
from bisect import bisect
import webbrowser
import threading
import wx


bgImgs_dpath = dpaths['bgImgs']
html_dpath = dpaths['z_html']

EPSILON = 1 / float(1e4)
BASE_SCALE = 2500
SCALE_INC = 2**0.5
SCALE_UNIT = 2
CANVAS_UNIT = 500
MAX_ZOOM = 16.0
SMALL_MARGIN = 3
ZOOM_BTN_SIZE = 25
WIDTH, HEIGHT = 1440.0, 1008.0


class TrajectoryView(wx.Panel):
    def __init__(self, parent, drivers=None):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour(wx.WHITE)
        #
        self.main_frame = self.Parent.Parent.Parent
        self.drivers = drivers
        #
        self.scale = 1.0
        self.set_minXminY_llXY()
        for d in self.drivers.itervalues():
            d.set_logIndex(tk.now, BASE_SCALE * self.scale, self.min_x, self.min_y)
        #
        self.InitUI()

    def InitUI(self):
        self.SetDoubleBuffered(True)
        #
        (self.translate_x, self.translate_y), self.translate_mode = (0, 0), False
        # prepare stock objects.
        self.default_pen = self.create_pen(wx.BLACK, 1)
        self.default_font = self.create_font(8, wx.SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        #
        self.zoomBtns = {}
        for i, img_name in enumerate(['zoomIn', 'zoomOut']):
            img = wx.Image('res/%s.png' % img_name).AdjustChannels(1.0, 1.0, 1.0, 1.0)
            bmp = wx.BitmapFromImage(img)
            px, py = (SMALL_MARGIN,
                        SMALL_MARGIN + DEVICE_DRAW_FONT.GetPointSize() + SMALL_MARGIN +
                        i * (ZOOM_BTN_SIZE + SMALL_MARGIN))
            self.zoomBtns[img_name] = zoomBtn(bmp, (px, py))
        self.bg_bmps = {}
        self.encountered_zones = set()
        self.marked_zone = None
        #
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.popupmenu = wx.Menu()
        for text in ['Show the chosen zone']:
            item = self.popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnShowPopup)

    def create_pen(self, color, width):
        return wx.Pen(color, width)

    def create_font(self, size, family, style, weight):
        return wx.Font(size, family, style, weight)

    def OnShowPopup(self, e):
        x, y = e.GetX(), e.GetY()
        actualX = (self.min_x + (x - self.translate_x))
        actualY = (self.min_y + (y - self.translate_y))
        LonsX, LatsY = self.sgLonsLatsXY
        self.zi, self.zj = bisect(LonsX, actualX) - 1, len(LatsY) - bisect(LatsY, actualY) - 1
        print self.zi, self.zj
        pos = self.ScreenToClient(wx.GetMousePosition())
        self.PopupMenu(self.popupmenu, pos)

    def OnPopupItemSelected(self, e):
        item = self.popupmenu.FindItemById(e.GetId())
        text = item.GetText()
        if text == 'Show the chosen zone':
            fpath = path_merge(html_dpath, 'zizj(%d-%d).html' % (self.zi, self.zj))
            if not check_path_exist(fpath):
                viz_aZone_html(self.zi, self.zj, fpath)
            html_url = 'file://%s' % (path_merge(opath.dirname(__file__), fpath))
            webbrowser.get('safari').open_new(html_url)

    def OnLeftDown(self, e):
        x, y = e.GetX(), e.GetY()
        for btnName, btn in self.zoomBtns.iteritems():
            if btn.btnPressed(x, y):
                self.zoom(True if btnName == 'zoomIn' else False)
                break
        else:
            self.translate_mode, self.prev_x, self.prev_y = True, x, y
            self.SetFocus()
            self.CaptureMouse()

    def OnMotion(self, e):
        if self.translate_mode:
            self.translate(e.GetX() - self.prev_x, e.GetY() - self.prev_y)
            self.prev_x, self.prev_y = e.GetX(), e.GetY()

    def OnLeftUp(self, _e):
        if self.translate_mode:
            self.translate_mode = False
            self.ReleaseMouse()

    def zoom(self, magnify):
        if abs(self.scale - MAX_ZOOM) < EPSILON and magnify:
            wx.MessageBox('This is the maximum zoom-in state')
        else:
            # magnify: True, if zoom-in; False, otherwise
            self.set_scale(self.scale * (SCALE_INC if magnify else (1 / SCALE_INC)))
            self.set_minXminY_llXY()
            for d in self.drivers.itervalues():
                d.update_prev_next_position(BASE_SCALE * self.scale, self.min_x, self.min_y)
            self.Refresh()
            self.Update()

    def set_scale(self, s):
        w, h = self.GetSize()
        cx, cy = w / 2.0, h / 2.0
        old_scale, self.scale = self.scale, s
        # print 'old_scale, cur_scale', old_scale, self.scale
        self.translate_x = cx - self.scale / old_scale * (cx - self.translate_x)
        self.translate_y = cy - self.scale / old_scale * (cy - self.translate_y)

    def set_minXminY_llXY(self):
        sgBorder_xy = GPS_xyDrawing.get_sgBoarderXY(BASE_SCALE * self.scale)
        self.min_x, self.min_y = 1e400, 1e400
        for x, y in sgBorder_xy:
            if x < self.min_x:
                self.min_x = x
            if y < self.min_y:
                self.min_y = y
        self.sgLonsLatsXY = GPS_xyDrawing.get_sgLonsLatsXY(BASE_SCALE * self.scale)

    def translate(self, dx, dy):
        self.translate_x += dx
        self.translate_y += dy
        self.Refresh()
        self.Update()

    def update_trjectory(self):
        if self.drivers == None:
            pass
        for d in self.drivers.itervalues():
            d.update_trajectory(tk.now, BASE_SCALE * self.scale, self.min_x, self.min_y)

    def update(self, ani_update=True):
        if ani_update:
            self.update_trjectory()
        self.Refresh()

    def OnPaint(self, _):
        # prepare.
        self.dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(self.dc)
        gc.SetPen(self.default_pen)
        gc.SetFont(self.default_font, wx.BLACK)
        # draw on logical space.
        oldTransform = gc.GetTransform()
        gc.Translate(self.translate_x, self.translate_y)

        self.OnDraw(gc)
        gc.SetTransform(oldTransform)
        self.OnDrawDevice(gc)

    def mark_zone(self, zi, zj):
        z = self.sgZones[zi, zj]
        self.marked_zone = z
        self.encountered_zones.add(z)

    def OnDrawDevice(self, gc):
        gc.SetFont(DEVICE_DRAW_FONT)
        tx = self.main_frame.tx
        txs = ('%.1f' if tx < 1e5 else '%.1e') % tx
        gc.DrawText('%d/%02d/%02d %02d:%02d:%02d (speed X%s)' %
                    (tk.now.year, tk.now.month, tk.now.day,
                     tk.now.hour, tk.now.minute, tk.now.second, txs), SMALL_MARGIN, SMALL_MARGIN)
        #
        for btn in self.zoomBtns.values():
            bmp = btn.bmp
            px, py = btn.pos
            w, h = btn.w, btn.h
            gc.DrawBitmap(bmp, px, py, w, h)

    def loadNextScales(self, oriScale):
        nextScale = oriScale
        while True:
            nextScale *= SCALE_INC
            # print 'load %.2f' % nextScale
            if not self.bg_bmps.has_key('%.2f' % nextScale):
                self.bg_bmps['%.2f' % nextScale] = self.gen_bg_img(nextScale)
            if MAX_ZOOM < nextScale:
                break
        # print 'complete loading!!'

    def OnDraw(self, gc):
        if not self.bg_bmps.has_key('%.2f' % self.scale):
            self.bg_bmps['%.2f' % self.scale] = self.gen_bg_img(self.scale)
            threading_object = threading.Thread(target=self.loadNextScales, args=(self.scale,))
            threading_object.daemon = True
            threading_object.start()
        bmp, w, h = self.bg_bmps['%.2f' % self.scale]
        gc.DrawBitmap(bmp, 0, 0, w, h)
        #
        gc.SetBrush(wx.Brush(wx.Colour(200, 20, 20)))
        for z in self.encountered_zones:
            gc.DrawLines(z.polyPoints_xy)
        if self.marked_zone:
            gc.SetBrush(wx.Brush(wx.Colour(0, 193, 193)))
            gc.DrawLines(self.marked_zone.polyPoints_xy)

        if self.drivers != None:
            for d in self.drivers.itervalues():
                d.draw(gc)
        #
        # gc.DrawLines([(10, 10), (20, 20)])

    def gen_bg_img(self, scale):
        bg_img_fpath = path_merge(bgImgs_dpath, 'bg_img(z%.2f).png' % scale)
        if check_path_exist(bg_img_fpath):
            img = wx.Image(bg_img_fpath).AdjustChannels(1.0, 1.0, 1.0, 0.4)
            bmp = wx.BitmapFromImage(img)
        else:
            sgBorder_xy = GPS_xyDrawing.get_sgBoarderXY(BASE_SCALE * scale)
            sgRoads_xy = GPS_xyDrawing.get_sgRordsXY(BASE_SCALE * scale)
            sgBuildings_xy = GPS_xyDrawing.get_sgBuildingsXY(BASE_SCALE * scale)
            sgGrid_xy = GPS_xyDrawing.get_sgGridXY(BASE_SCALE * scale)
            #
            min_x, min_y = 1e400, 1e400
            for x, y in sgBorder_xy:
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
            bmp = wx.EmptyBitmap(WIDTH * scale, HEIGHT * scale)
            # Create a memory DC that will be used for actually taking the screenshot
            dc = wx.MemoryDC(bmp)
            gc = wx.GraphicsContext.Create(dc)
            gc.SetPen(self.default_pen)
            gc.SetFont(self.default_font, wx.BLACK)
            # draw on logical space.
            oldTransform = gc.GetTransform()
            gc.Translate(-min_x, -min_y)
            #
            gpath = gc.CreatePath()
            gpath.MoveToPoint(sgBorder_xy[0])
            for i in range(1, len(sgBorder_xy)):
                gpath.AddLineToPoint(sgBorder_xy[i])
            #
            for r_coords in sgRoads_xy:
                gpath.MoveToPoint(r_coords[0])
                for i in range(1, len(r_coords)):
                    gpath.AddLineToPoint(r_coords[i])
                    #
            if 8 <= scale:
                for r_coords in sgBuildings_xy:
                    gpath.MoveToPoint(r_coords[0])
                    for i in range(1, len(r_coords)):
                        gpath.AddLineToPoint(r_coords[i])
            #
            gc.SetPen(wx.Pen(wx.Colour(100, 100, 100), 1.0))
            for l in sgGrid_xy:
                gpath.MoveToPoint(l[0])
                for i in range(1, len(l)):
                    gpath.AddLineToPoint(l[i])
            gc.DrawPath(gpath)
            gc.SetTransform(oldTransform)
            #
            img = bmp.ConvertToImage()
            img.SaveFile(bg_img_fpath, wx.BITMAP_TYPE_PNG)
            bmp = wx.BitmapFromImage(img.AdjustChannels(1.0, 1.0, 1.0, 0.4))
        return bmp, WIDTH * scale, HEIGHT * scale


class zoomBtn(object):
    def __init__(self, bmp, pos):
        self.bmp = bmp
        self.pos = pos
        self.w, self.h = ZOOM_BTN_SIZE, ZOOM_BTN_SIZE

    def btnPressed(self, x, y):
        px, py = self.pos
        w, h = self.w, self.h
        if (px <= x <= px + w) and (py <= y <= py + h):
            return True
        else:
            False
