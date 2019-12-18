import unittest
import pathlib
import shutil
from alabs.pam.scenario_repository import ScenarioRepoHandler

HOME_DIR = pathlib.Path.home()
STORE_DIR = pathlib.Path(ScenarioRepoHandler.STORE_DIR)
STORE_IMAGE_DIR = pathlib.Path(ScenarioRepoHandler.STORE_DIR,
                               ScenarioRepoHandler.STORE_IMAGES_DIR)

SCENARIO_PATH = 'scenarios/MacOS/LA-Scenario0010/LA-Scenario0010.json'
SCENARIO_PATH_2 = 'scenarios/MacOS/LA-Scenario0010/LA-Scenario0010.json'


class TestPostHandler(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test001_init(self):
        store = ScenarioRepoHandler()
        self.assertEqual(
            HOME_DIR / pathlib.Path(store.STORE_DIR), store.store_path)

    # ==========================================================================
    def test005_store_image_dir(self):
        """
        Store에 Images 디렉토리 구해오기
        :return:
        """
        store = ScenarioRepoHandler()
        home = pathlib.Path.home()
        images = pathlib.Path(store.STORE_DIR, store.STORE_IMAGES_DIR)
        home_images = home / images
        self.assertEqual(str(home_images), store.get_store_image_dir())

    # ==========================================================================
    def test010_add_bot_get_bots(self):
        """
        add_bot, get_bots, got_bot 검사
        :return:
        """
        store = ScenarioRepoHandler()
        store.add_bot('./' + SCENARIO_PATH)
        value = HOME_DIR / pathlib.Path(store.STORE_DIR) / \
                pathlib.Path(SCENARIO_PATH).name
        result = store.get_bot(0)
        self.assertEqual(str(value), str(result))

    # ==========================================================================
    def test011_get_image_dir(self):
        """
        Source의 Images 디렉토리 구해오기
        :return:
        """
        store = ScenarioRepoHandler()
        expected_image_dir = 'scenarios/MacOS/LA-Scenario0010/Images/' \
                             'LA-Scenario0010.json'
        self.assertEqual(
            expected_image_dir, store.get_images_dir(SCENARIO_PATH))

    # ==========================================================================
    def test020_remove_bots(self):
        store = ScenarioRepoHandler()
        store.remove_bots([0, ])
        self.assertEqual(
            [], list(pathlib.Path(store.store_path).glob('*.json')))

    # ==========================================================================
    def test030_add_bot_with_zip_file(self):
        path = pathlib.Path(SCENARIO_PATH_2)
        name = path.name[:-5]
        shutil.make_archive(name, 'zip', str(path.parent))
        store = ScenarioRepoHandler()
        result = store.add_bot_with_zip_file('%s.zip' % name)
        self.assertTrue(result)
        pathlib.Path("%s.zip" % name).unlink()

    def test040_get_bots_with_zip_file(self):
        self.test030_add_bot_with_zip_file()
        path = pathlib.Path(SCENARIO_PATH_2)
        name = path.name[:-5]
        store = ScenarioRepoHandler()
        exp = pathlib.Path(store.store_path) / pathlib.Path(name + '.zip')
        bots = store.get_bots_with_zip_file()
        self.assertEqual([str(exp),], bots)

    def test041_get_bots_with_zip_file(self):
        store = ScenarioRepoHandler()
        self.assertTrue(store.get_bot_with_zip_file(0))









