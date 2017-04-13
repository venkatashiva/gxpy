import unittest
import os
import numpy as np

import geosoft
import geosoft.gxapi as gxapi
import geosoft.gxpy.gx as gx
import geosoft.gxpy.system as gsys
import geosoft.gxpy.map as gxmap
import geosoft.gxpy.view as gxv
import geosoft.gxpy.geometry as gxgm
import geosoft.gxpy.coordinate_system as gxcs
import geosoft.gxpy.system as gxsys
import geosoft.gxpy.group as gxg
import geosoft.gxpy.agg as gxagg
import geosoft.gxpy.grd as gxgrd

from geosoft.gxpy.tests import GXPYTest

def new_test_data_map(mapname=None, rescale=1.0):

    if mapname is None:
        mapname = os.path.join(gx.GXpy().temp_folder(), 'test')

    with gxmap.GXmap.new(mapname, overwrite=True) as map:
        with gxv.GXview(map, "rectangle_test") as v:
            with gxg.GXdraw(v, 'rectangle') as g:
                g.xy_rectangle((gxgm.Point((0, 0)), gxgm.Point((250, 110))), pen=gxg.Pen(line_thick=1))
    
                p1 = gxgm.Point((5, 5)) * rescale
                p2 = gxgm.Point((100, 100)) * rescale
                poff = gxgm.Point((10, 5)) * rescale
                g.pen = gxg.Pen(fill_color=gxg.C_LT_GREEN)
                g.xy_rectangle((p1, p2))
    
                g.pen = gxg.Pen(line_style=2, line_pitch=2.0)
                g.xy_line((p1 + poff, p2 - poff))

        with gxv.GXview(map, "poly") as v:
            with gxg.GXdraw(v, 'poly') as g:
                plinelist = [[110, 5],
                             [120, 20],
                             [130, 15],
                             [150, 50],
                             [160, 70],
                             [175, 35],
                             [190, 65],
                             [220, 50],
                             [235, 18.5]]
                pp = gxgm.PPoint.from_list(plinelist) * rescale
                g.pen = gxg.Pen(line_style=2, line_pitch=2.0)
                g.xy_poly_line(pp)
                g.pen = gxg.Pen(line_style=4, line_pitch=2.0, line_smooth=gxg.SMOOTH_AKIMA)
                g.xy_poly_line(pp)
    
                ppp = np.array(plinelist)
                pp = gxgm.PPoint(ppp[3:, :]) * rescale
                g.pen = gxg.Pen(line_style=5, line_pitch=5.0,
                              line_smooth=gxg.SMOOTH_CUBIC,
                              line_color=gxapi.C_RED,
                              line_thick=0.25,
                              fill_color=gxapi.C_LT_BLUE)
                g.xy_poly_line(pp, close=True)
    
                g.pen = gxg.Pen(fill_color=gxapi.C_LT_GREEN)
                pp = (pp - (100, 0, 0)) / 2 + (100, 0, 0)
                g.xy_poly_line(pp, close=True)
                pp += (0, 25, 0)
                g.pen = gxg.Pen(fill_color=gxapi.C_LT_RED)
                g.xy_poly_line(pp, close=True)

        return map.file_name

def test_data_map(name=None, data_area=(1000,0,11000,5000)):

    if name is None:
        name = os.path.join(gx.GXpy().temp_folder(), "test")
    gxmap.delete_files(name)
    cs = gxcs.GXcs("WGS 84 / UTM zone 15N")
    return gxmap.GXmap.new(file_name=name,
                           data_area=data_area,
                           cs=cs,
                           media="A4",
                           margins=(1.5, 3, 1.5, 1),
                           inside_margin=0.5)

class Test(unittest.TestCase, GXPYTest):

    @classmethod
    def setUpClass(cls):
        GXPYTest.setUpClass(cls, __file__)

    @classmethod
    def tearDownClass(cls):
        GXPYTest.tearDownClass(cls)

    
    @classmethod
    def start(cls, test, test_name):
        parts = os.path.split(__file__)
        test.result_dir = os.path.join(parts[0], 'results', parts[1], test_name)
        cls.gx.log("*** {} > {}".format(parts[1], test_name))

    def test_version(self):
        Test.start(self, gsys.func_name())
        self.assertEqual(gxmap.__version__, geosoft.__version__)

    def test_newmap(self):
        Test.start(self, gsys.func_name())

        # test map
        name = 'test_newmap'
        gxmap.delete_files(name)
        with gxmap.GXmap.new(name) as map:
            self.assertEqual(map.name, name)
            mapfile = map.file_name
            self.assertEqual(mapfile, os.path.abspath((name + '.map')))
        self.assertTrue(os.path.isfile(mapfile))

        # verify can't write on a new map
        self.assertRaises(gxmap.MapException, gxmap.GXmap.new, name)
        self.assertRaises(gxmap.MapException, gxmap.GXmap.new, mapfile)
        with gxmap.GXmap.new(name, overwrite=True):
            pass

        # but I can open it
        with gxmap.GXmap.open(name):
            pass
        with gxmap.GXmap.open(mapfile):
            pass

        gxmap.delete_files(mapfile)
        self.assertFalse(os.path.isfile(mapfile))

        self.assertRaises(gxmap.MapException, gxmap.GXmap, 'bogus')

    def test_new_geosoft_map(self):
        Test.start(self, gsys.func_name())

        # temp map
        with gxmap.GXmap.new(data_area=(0, 0, 100, 80)) as map:
            views = map.view_list
            self.assertTrue('base' in views)
            self.assertTrue('data' in views)

        with gxmap.GXmap.new(data_area=(0, 0, 100, 80),
                             cs=gxcs.GXcs("DHDN / Okarito 2000 [geodetic]")) as map:
            with gxv.GXview(map, 'data', mode=gxv.WRITE_OLD) as v:
                self.assertEqual("DHDN / Okarito 2000 [geodetic]", str(v.cs))

    def test_lists(self):
        Test.start(self, gsys.func_name())

        mapname = new_test_data_map()
        with gxmap.GXmap.open(mapname) as map:
            views = map.view_list
            self.assertTrue('rectangle_test' in views)
            self.assertTrue('poly' in views)

            views = map.view_list_2D
            self.assertTrue('rectangle_test' in views)
            self.assertTrue('poly' in views)

            views = map.view_list_3D
            self.assertEqual(len(views), 0)

    def test_map_delete(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(file_name='test_geosoft', overwrite=True) as map:
            file_name = map.file_name
            self.assertEqual(len(map.view_list), 2)
            self.assertTrue(map.has_view('data'))
            self.assertTrue(map.has_view('base'))
        self.assertTrue(os.path.isfile(file_name))
        with open(file_name, 'rb') as f:
            pass

        with gxmap.GXmap.new(file_name='test_geosoft',
                             overwrite=True,
                             data_area=(1000, 200, 11000, 5000)) as map:
            file_name = map.file_name
            self.assertEqual(len(map.view_list), 2)
            self.assertTrue(map.has_view('data'))
            self.assertTrue(map.has_view('base'))
        self.assertTrue(os.path.isfile(file_name))
        with open(file_name, 'rb') as f:
            pass

        with gxmap.GXmap.new(file_name='test_geosoft', overwrite=True) as map:
            file_name = map.file_name
            map.remove_on_close(True)
        self.assertFalse(os.path.isfile(file_name))

        for i in range(3):
            map = gxmap.GXmap.new(file_name='t{}'.format(i), overwrite=True)
            map.remove_on_close(True)
            map.close()

    def test_map_classes(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(file_name='test_geosoft', overwrite=True) as map:
            self.assertEqual(map.get_class_name('data'), 'data')
            self.assertEqual(map.get_class_name('base'), 'base')
            self.assertEqual(map.get_class_name('section'), 'section')
            self.assertEqual(map.get_class_name('some_class_name'), 'some_class_name')

            map.set_class_name('base', 'bogus')
            self.assertEqual(map.get_class_name('base'), 'bogus')
            map.set_class_name('data', 'bogus_data')
            #self.assertEqual(map.get_class_name('data'), 'bogus_data')
            map.set_class_name('Section', 'yeah')
            self.assertEqual(map.get_class_name('Section'), 'yeah')
            map.set_class_name('mine', 'boom')
            self.assertEqual(map.get_class_name('mine'), 'boom')

        with gxmap.GXmap.new(data_area=(0, 0, 100, 80),
                             cs=gxcs.GXcs("DHDN / Okarito 2000 [geodetic]")) as map:

            self.assertEqual(map.get_class_name('base'), 'base')
            self.assertEqual(map.get_class_name('data'), 'data')

            with gxv.GXview(map, "copy_data", mode=gxv.WRITE_NEW, copy="data"): pass
            map.set_class_name('data', 'copy_data')
            self.assertEqual(map.get_class_name('data'), 'copy_data')

    def test_current_view(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new() as map:
            self.assertEqual(map.current_data_view, 'data')
            map.current_data_view = 'base'
            self.assertEqual(map.current_data_view, 'base')
            self.assertEqual(map.get_class_name('data'), 'base')
            map.current_data_view = 'data'
            self.assertEqual(map.current_data_view, 'data')
            try:
                map.current_data_view = 'Bogus'
                self.assertTrue(False)
            except gxmap.MapException:
                pass

            map.copy_view('data', 'Bogus')
            map.current_data_view = 'Bogus'
            self.assertEqual(map.current_data_view, 'bogus')
            self.assertRaises(gxmap.MapException, map.copy_view, 'Data', 'bogus')
            self.assertRaises(gxmap.MapException, map.copy_view, 'data', 'bogus')
            map.copy_view('data', 'bogus', overwrite=True)
            self.assertEqual(map.current_data_view, 'bogus')

    def test_media(self):
        Test.start(self, gsys.func_name())

        def crc_media(map_file, test_number):
            with gxmap.GXmap.open(map_file) as map:
                with gxv.GXview(map, "base") as v:
                    with gxg.GXdraw(v) as g:
                        g.xy_rectangle(v.extent_clip, pen=gxg.Pen(line_thick=0.2, line_color='K'))
                with gxv.GXview(map, "data") as v:
                    with gxg.GXdraw(v) as g:
                        g.xy_rectangle(v.extent_clip, pen=gxg.Pen(line_thick=0.2, line_color='R'))
            self.crc_map(map_file,
                         pix_width=256,
                         alt_crc_name='{}_{}'.format(gxsys.func_name(1), test_number))

        test_media_map = os.path.join(gx.GXpy().temp_folder(), 'test_media')

        test_number = 0
        with gxmap.GXmap.new(test_media_map + 'scale_800', overwrite=True, scale=800,
                             data_area=(5, 10, 50, 100)) as map:
            file_name = map.file_name
        crc_media(file_name, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'scale_100', overwrite=True, scale=100,
                             data_area=(5, 10, 50, 100)) as map:
            file_name = map.file_name
        crc_media(file_name, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'a4_portrait',
                             overwrite=True,
                             media='A4',
                             layout=gxmap.MAP_PORTRAIT) as map:
            file_name = map.file_name
        crc_media(file_name, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'portrait_a4',
                             overwrite=True,
                             media='a4',
                             fixed_size=True,
                             layout=gxmap.MAP_PORTRAIT) as map:
            file_name = map.file_name
        crc_media(file_name, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'a4_landscape',
                             overwrite=True,
                             media='A4',
                             fixed_size=True,
                             layout=gxmap.MAP_LANDSCAPE) as map:
            file_name = map.file_name
        crc_media(file_name, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'A4_1',
                             overwrite=True, media='A4',
                             fixed_size=True,
                             data_area=(10, 5, 100, 50)) as map:
            file_name = map.file_name
        crc_media(file_name, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'A4_2',
                             overwrite=True, media='A4',
                             fixed_size=True,
                             data_area=(5, 10, 50, 100), layout=gxmap.MAP_LANDSCAPE) as map:
            file_name = map.file_name
        crc_media(file_name, test_number)
        test_number += 1

        with gxmap.GXmap.new(test_media_map + 'A4_3',
                             overwrite=True,
                             media='A4',
                             data_area=(5, 10, 50, 100)) as map:
            file_name = map.file_name
        crc_media(file_name, test_number)
        test_number += 1

        for m in (None, (60, 50), 'unlimited', 'bogus', 'A4', 'A3', 'A2', 'A1', 'A0',
                  'A', 'B', 'C', 'D', 'E'):
            with gxmap.GXmap.new(media=m) as map: pass

        self.assertRaises(gxmap.MapException,
                          gxmap.GXmap.new,
                          test_media_map, overwrite=True, media='A4',
                          data_area=(100, 50, 10, 5), layout='landscape')

    def test_multiple_temp_maps(self):
        Test.start(self, gsys.func_name())

        mapfiles = []
        for i in range(3):
            with gxmap.GXmap.new() as map:
                mapfiles.append(map.file_name)
                with gxv.GXview(map, 'data') as v:
                    with gxg.GXdraw(v) as g:
                        g.xy_rectangle(v.extent_clip)

        for fn in mapfiles:
            self.assertTrue(os.path.isfile(fn))


    def test_north_arrow_0(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(cs='ft') as map:
            mapfile = map.file_name

            with gxv.GXview(map, 'base') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)
            with gxv.GXview(map, 'data') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)

            map.north_arrow()

        self.crc_map(mapfile)

    def test_north_arrow_1(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(cs='m', data_area=(0,0,20,10), scale=100) as map:
            mapfile = map.file_name

            with gxv.GXview(map, 'base') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)
            with gxv.GXview(map, 'data') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)

            map.north_arrow(location=(2, 0, 3), inclination=-12, declination=74.5,
                            text_def=gxg.Text_def(font='Calibri'))

        self.crc_map(mapfile)


    def test_scale_1(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(data_area=(350000,7000000,400000,7030000), cs='ft') as map:
            mapfile = map.file_name
            with gxv.GXview(map, 'base') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)
            with gxv.GXview(map, 'data') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)
            map.scale_bar()
            map.scale_bar(location=(2, 0, 2), length=10, sections=12)
            map.scale_bar(location=(5, 0, 0), length=8, sections=2, post_scale=True)
            map.scale_bar(location=(3, -3, 1.5), length=4,
                          text=gxg.Text_def(height=0.2, italics=True), post_scale=True)

        self.crc_map(mapfile)

    def test_scale_2(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(data_area=(350000,7000000,400000,7030000), cs='NAD83 / UTM zone 15N') as map:
            mapfile = map.file_name
            with gxv.GXview(map, 'base') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)
            with gxv.GXview(map, 'data') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)
            map.scale_bar()
            map.scale_bar(location=(2, 0, 2), length=10, sections=12)

        self.crc_map(mapfile)


    def test_surround_1(self):
        Test.start(self, gsys.func_name())

        cs = gxcs.GXcs('NAD83 / UTM zone 15N')
        with gxmap.GXmap.new(data_area=(350000, 7000000, 400000, 7030000), cs=cs) as map:
            mapfile = map.file_name
            with gxv.GXview(map, 'data') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)
            map.surround()
        self.crc_map(mapfile)

    def test_surround_2(self):
        Test.start(self, gsys.func_name())

        cs = gxcs.GXcs('NAD83 / UTM zone 15N')
        with gxmap.GXmap.new(data_area=(350000, 7000000, 400000, 7030000), cs=cs) as map:
            mapfile = map.file_name
            with gxv.GXview(map, 'data') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)
            map.surround(gap=0.2)
        self.crc_map(mapfile)

    def test_surround_3(self):
        Test.start(self, gsys.func_name())

        with gxmap.GXmap.new(data_area=(350000, 7000000, 400000, 7030000)) as map:
            mapfile = map.file_name
            with gxv.GXview(map, 'data') as v:
                with gxg.GXdraw(v) as g:
                    g.xy_rectangle(v.extent_clip)
            map.surround(gap=0.2,
                         outer_pen=gxg.Pen.from_mapplot_string('rt500'),
                         inner_pen=gxg.Pen.from_mapplot_string('K16'))
        self.crc_map(mapfile)

    def test_annotate_xy_0(self):
        Test.start(self, gsys.func_name())

        with test_data_map() as map:
            mapfile = map.file_name
            map.annotate_data_xy(x_sep=1500)

        self.crc_map(mapfile)

    def test_annotate_xy_1(self):
        Test.start(self, gsys.func_name())

        with test_data_map() as map:
            mapfile = map.file_name
            map.annotate_data_xy(x_sep=1500,
                                 grid=gxmap.GRID_DOTTED,
                                 offset=0.5,
                                 text_def=gxg.Text_def(color='R', weight=gxg.FONT_WEIGHT_BOLD))

        self.crc_map(mapfile)

    def test_annotate_xy_2(self):
        Test.start(self, gsys.func_name())

        with test_data_map() as map:
            mapfile = map.file_name
            map.annotate_data_xy(x_sep=1500,
                                 tick=0.1,
                                 text_def=gxg.Text_def(color='G', weight=gxg.FONT_WEIGHT_ULTRALIGHT),
                                 grid=gxmap.GRID_CROSSES,
                                 grid_pen=gxg.Pen(line_color='b', line_thick=0.015))

        self.crc_map(mapfile)

    def test_annotate_xy_3(self):
        Test.start(self, gsys.func_name())

        with test_data_map() as map:
            mapfile = map.file_name
            map.annotate_data_xy(x_sep=1500,
                                 tick=0.1,
                                 grid=gxmap.GRID_LINES,
                                 offset=0.2,
                                 edge_pen=gxg.Pen(line_color='k64', line_thick=0.3),
                                 grid_pen=gxg.Pen(line_color='b', line_thick=0.015))

        self.crc_map(mapfile)

    def test_annotate_ll_0(self):
        Test.start(self, gsys.func_name())

        with test_data_map(data_area=(350000,7000000,400000,7030000)) as map:
            mapfile = map.file_name
            map.annotate_data_ll()
        self.crc_map(mapfile)

    def test_annotate_ll_1(self):
        Test.start(self, gsys.func_name())

        with test_data_map(data_area=(350000,7000000,400000,7030000)) as map:
            mapfile = map.file_name
            map.annotate_data_ll(grid=gxmap.GRID_LINES,
                                 grid_pen=gxg.Pen(line_color='b'),
                                 text_def=gxg.Text_def(color='K127',
                                                       font='cr.gfn',
                                                       weight=gxg.FONT_WEIGHT_BOLD,
                                                       italics=True))
        self.crc_map(mapfile)

    def test_annotate_ll_2(self):
        Test.start(self, gsys.func_name())

        with test_data_map(data_area=(350000,7000000,400000,7030000)) as map:
            mapfile = map.file_name
            map.annotate_data_xy()
            map.annotate_data_ll(grid=gxmap.GRID_LINES,
                                  grid_pen=gxg.Pen(line_color='b', line_thick=0.015),
                                  text_def=gxg.Text_def(color='r', height=0.2, italics=True),
                                  top=gxmap.TOP_IN)
        self.crc_map(mapfile)

    def test_annotate_ll_3(self):
        Test.start(self, gsys.func_name())

        with test_data_map(data_area=(350000,7000000,400000,7030000)) as map:
            mapfile = map.file_name
            map.annotate_data_xy(tick=0.1, grid=gxmap.GRID_LINES,
                                 text_def=gxg.Text_def(weight=gxg.FONT_WEIGHT_ULTRALIGHT),
                                 grid_pen=gxg.Pen(line_thick=0.01))
            map.annotate_data_ll(grid=gxmap.GRID_LINES,
                                 grid_pen=gxg.Pen(line_color='b', line_thick=0.025),
                                 text_def=gxg.Text_def(height=0.18, italics=True, color='g'))
        self.crc_map(mapfile)

    def test_annotate_ll_4(self):
        Test.start(self, gsys.func_name())

        with test_data_map(data_area=(350000,7000000,400000,7030000)) as map:
            mapfile = map.file_name
            map.annotate_data_xy(tick=0.1, grid=gxmap.GRID_LINES,
                                 text_def=gxg.Text_def(weight=gxg.FONT_WEIGHT_BOLD),
                                 top=gxmap.TOP_IN)
            map.annotate_data_ll(grid=gxmap.GRID_LINES,
                                 grid_pen=gxg.Pen(line_color='b', line_thick=0.025),
                                 text_def=gxg.Text_def(height=0.18, italics=True),
                                 top=gxmap.TOP_IN)
        self.crc_map(mapfile)

    #TODO - JB to fix test framework to pass tests like this
    @unittest.skip("test fail due to temp file use - JB to correct in testing framework")
    def test_color_bar(self):
        Test.start(self, gsys.func_name())

        def test_agg_map():

            # test grid file
            folder, files = gsys.unzip(os.path.join(os.path.dirname(__file__), 'testgrids.zip'),
                                       folder=self.gx.temp_folder())
            grid_file = os.path.join(folder, 'test_agg_utm.grd')
            map_file = os.path.join(self.gx.temp_folder(), "test_agg_utm")

            with gxgrd.GXgrd(grid_file) as grd:
                ex = grd.extent_2d()
                cs = grd.cs
            with gxmap.GXmap.new(map_file, overwrite=True, cs=cs,
                                 data_area=ex, margins=(6,6,5,5)) as map:
                mapfile = map.file_name
                with gxv.GXview(map, "data") as v:
                    with gxg.GXdraw(v) as g:
                        g.xy_rectangle(v.extent_clip, pen=g.new_pen(line_thick = 0.1, line_color = 'R'))

                    with gxagg.GXagg(grid_file, shade=True) as agg:
                        gxg.GXaggregate(v, agg)

                with gxv.GXview(map, "data") as v:
                    with gxg.GXdraw(v) as g:
                        g.xy_rectangle(v.extent_clip, pen=g.new_pen(line_thick=0.1, line_color='R'))

                with gxv.GXview(map, "base") as v:
                    with gxg.GXdraw(v) as g:
                        g.xy_rectangle(v.extent_clip, pen=g.new_pen(line_thick = 0.1, line_color = 'B'))

                map.annotate_data_ll(grid=gxmap.GRID_LINES,
                                      grid_pen=gxg.Pen.from_mapplot_string("bt250"),
                                      text_def=gxg.Text_def(height=0.25, italics=True),
                                      top=gxmap.TOP_IN)
            return mapfile

        mapfile = test_agg_map()
        with gxmap.GXmap.open(mapfile) as map:
            map.agg_legend()
            with gxv.GXview(map, '*data') as v:
                v.delete_group('temp_agg')
        self.crc_map(mapfile, alt_crc_name='color_bar_0')

        mapfile = test_agg_map()
        with gxmap.GXmap.open(mapfile) as map:
            map.agg_legend(bar_location=gxg.COLOR_BAR_LEFT,
                           annotation_side=gxg.COLOR_BAR_ANNOTATE_LEFT,
                           title="Left Bar\nsub_title\n(nano-things)")
            with gxv.GXview(map, '*data') as v:
                v.delete_group('temp_agg')
        self.crc_map(mapfile, alt_crc_name='color_bar_1')

        mapfile = test_agg_map()
        with gxmap.GXmap.open(mapfile) as map:
            map.agg_legend(bar_location=gxg.COLOR_BAR_BOTTOM,
                           annotation_height=0.5,
                           title='Bottom')
            with gxv.GXview(map, '*data') as v:
                v.delete_group('temp_agg')
        self.crc_map(mapfile, alt_crc_name='color_bar_2')

        mapfile = test_agg_map()
        with gxmap.GXmap.open(mapfile) as map:
            map.agg_legend(bar_location=gxg.COLOR_BAR_TOP,
                           annotation_side=gxg.COLOR_BAR_ANNOTATE_BOTTOM,
                           title='This is a Top Centred Bar')
            with gxv.GXview(map, '*data') as v:
                v.delete_group('temp_agg')
        self.crc_map(mapfile, alt_crc_name='color_bar_3')

if __name__ == '__main__':
    unittest.main()
