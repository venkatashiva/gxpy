import unittest

import pprint

import geosoft.gxpy.system as gsys
import geosoft.gxpy.gx as gx

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gx = gx.GXpy()
        cls.pp = pprint.PrettyPrinter(indent=3)

    @classmethod
    def tearDownClass(cls):
        pass
    
    @classmethod
    def start(cls,test):
        print("\n*** {} ***".format(test))

    def test_gxpy(self):
        self.start(gsys.func_name())

        self.assertTrue(self.gx.gid.find('@') > 0)
        self.assertEqual(self.gx.main_wind_id(),0)
        self.assertEqual(self.gx.active_wind_id(), 0)

    def test_ui_onoff(self):
        self.start(gsys.func_name())

        self.gx.dissable_app()
        self.gx.enable_app()

    def test_env(self):
        self.start(gsys.func_name())

        env = self.gx.environment()
        self.assertFalse(env.get('gid') is None)
        self.assertFalse(env.get('id_window_main') is None)
        self.assertFalse(env.get('id_window_active') is None)
        self.assertFalse(env.get('id_thread') is None)
        self.assertFalse(env.get('current_date') is None)
        self.assertFalse(env.get('current_utc_date') is None)
        self.assertFalse(env.get('current_time') is None)
        self.assertFalse(env.get('current_utc_time') is None)
        self.assertFalse(env.get('license_class') is None)
        self.assertFalse(env.get('menu_default') is None)
        self.assertFalse(env.get('menu_loaded') is None)
        self.assertFalse(env.get('menu_user') is None)
        self.assertFalse(env.get('folder_workspace') is None)
        self.assertFalse(env.get('folder_temp') is None)
        self.assertFalse(env.get('folder_user') is None)

        env = self.gx.environment(2)
        self.assertTrue(isinstance(env,str))
        print(env)


    def test_entitlements(self):
        self.start(gsys.func_name())

        ent = self.gx.entitlements()
        self.assertTrue(ent.get('1000'), 'Oasis montaj Base')
        self.assertTrue(ent.get('1100'), 'Oasis montaj™ Viewer Mapping and Processing System')
        self.pp.pprint(ent)

    def test_display_message(self):
        self.start(gsys.func_name())

        self.gx.display_message('test title', 'test message')

###############################################################################################

if __name__ == '__main__':

    unittest.main()
