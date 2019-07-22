import pathlib
import shutil
import zipfile
import tempfile
from alabs.common.util.vvhash import get_file_md5




################################################################################
class ScenarioRepoHandler:
    """
    @startuml

    title
    Bot 저장소 사용
    end title

    ' 선언
    participant "PAM Manager(//Rest API//)" as PM
    database "Bot Store" as STORE
    ' collections BOT

    == Bot 추가 ==
    PM -> STORE: add_bot()
    note over PM
    Bot 추가 요청
    Bot ZIP 압축파일 or 경로
    end note
    activate STORE
    return bool

    == Bot 목록 가져오기 ==
    PM -> STORE: get_bots()
    activate STORE
    return list

    == Bot 삭제 하기 ==
    PM -> STORE: remove_bots()
    note over PM
    get_bots() 통해서 얻은
    인덱스 번호를 사용
    end note
    activate STORE
    return bool
    @enduml
    """
    STORE_DIR = '.argos-rpa.bots'
    STORE_IMAGES_DIR = 'Images'

    # ==========================================================================
    def __init__(self, store_path=None):
        if not store_path:
            store_path = pathlib.Path.home() / self.STORE_DIR
        self._store_path = store_path
        self.init_store()

    # ==========================================================================
    def init_store(self):
        """
        저장소가 존재하지 않으면 생성
        :return:
        """
        store = pathlib.Path(self.store_path)
        if not store.exists():
            store.mkdir()
        return True

    # ==========================================================================
    @property
    def store_path(self):
        return self._store_path

    # ==========================================================================
    def get_store_image_dir(self):
        """
        Bot Store에서 사용하는 Bot의 Images 디렉토리를 반환
        :return:
            Bot Store의 Images 경로 반환남
        """
        path = self.store_path / pathlib.Path(ScenarioRepoHandler.STORE_IMAGES_DIR)
        # path = '.argos-rpa.bots/Images'
        return str(path)

    # ==========================================================================
    @staticmethod
    def get_images_dir(path):
        """
        받은 Bot(Scenario)의 Image 디렉토리 반환
        :param path:
        :return:
        """
        bot_path = pathlib.Path(path)
        if not bot_path.exists() or not bot_path.is_file():
            raise
        bot_path = list(bot_path.parts)
        bot_path.insert(-1, 'Images')
        return str(pathlib.Path(*bot_path))

    @property
    def tempdir(self):
        path = pathlib.Path(tempfile.gettempdir()) / \
               pathlib.Path(ScenarioRepoHandler.STORE_DIR)
        return str(path)

    # ==========================================================================
    @staticmethod
    def get_bots() -> list:
        """
        저장소의 json 파일을 검색해서 Bot 파일을 찾아서 반환
        :return:
        """
        # .argos-rpa.bots에서 JSON 파일 목록 가져오기
        path = str(pathlib.Path(pathlib.Path.home(), ScenarioRepoHandler.STORE_DIR))
        bots_dir = sorted(pathlib.Path(path).glob('*.json'))
        # Bot 파일이 아니면 거르기
        # Scenario 클래스 사용하여 검사.
        return bots_dir

    # ==========================================================================
    @staticmethod
    def get_bot(idx) -> str:
        """
        index를 받아서 해당 봇을 반환
        :param idx:
        :return:
        """
        bots = ScenarioRepoHandler.get_bots()
        return str(bots[idx])

    # ==========================================================================
    def remove_bots(self, idx: list):
        """
        하나 또는 다수의 봇 Index를 받아서 삭제.
        순서 상관없이 순차 삭제 가능
        :param idx:
        :return:
        """
        idx.sort()
        idx.reverse()
        bots = self.get_bots()
        for i in idx:
            self._remove_bot(str(bots[i]))
        return True

    # ==========================================================================
    def _remove_bot(self, bot_file):
        """
        Bot 파일 경로를 받아서 Json과 Images를 삭제
        :param bot_file:
        :return:
        """
        bot_image_dir = self.get_images_dir(bot_file)
        pathlib.Path(bot_file).unlink()
        shutil.rmtree(bot_image_dir, ignore_errors=True)
        return True

    # ==========================================================================
    def remove_bots_zip_file(self, idx: list):
        idx.sort()
        idx.reverse()
        bots = self.get_bots_with_zip_file()
        for i in idx:
            self._remove_bot_zip_file(str(bots[i]))
        return True

    # ==========================================================================
    def _remove_bot_zip_file(self, zip_path):
        pathlib.Path(zip_path).unlink()
    # ==========================================================================
    def add_bot_with_zip_file(self, file_path):
        """
        zip 형태로 압축된 Bot을 Store에 추가
        :param file_path:
        :return:
        """
        shutil.copy(file_path, self.store_path)

        name = pathlib.Path(file_path).name
        if not pathlib.Path(self.store_path).glob(name):
            return False
        # ZIP 파일 인스턴스 생성
        # 저장소에 압축풀기
        # file = zipfile.ZipFile(file_path)
        # file.extractall(self.store_path)
        return True

    # ==========================================================================
    def get_bots_with_zip_file(self):
        bots_dir = sorted(
            pathlib.Path(self.store_path).glob('*.zip'))
        # Bot 파일이 아니면 거르기
        # Scenario 클래스 사용하여 검사.
        bots_dir = [str(x) for x in bots_dir]
        return bots_dir

    # ==========================================================================
    def get_bot_with_zip_file(self, idx: int, prefix=''):
        """
        BOT ZIP 파일을 임시 폴더에 압축 해제
        :param idx:
        :param prefix:
        :return:
            /var/folders/sm/_fpq5m_s2g37096_6gzzk5fw0000gn/T/.argos-rpa.bots/LA-Scenario0020/LA-Scenario0020.json
        """
        bots = self.get_bots_with_zip_file()
        bot_path = bots[idx]

        name = pathlib.Path(bot_path).name
        name = name.split('.')[0]
        path = str(pathlib.Path(self.tempdir, prefix, name))

        with zipfile.ZipFile(bot_path) as file:
            file.extractall(path)
        path = pathlib.Path(path, name + '.json')
        return path


    # ==========================================================================
    def add_bot(self, source_json_path: str):
        """
        경로를 받아서 해당 BOT 파일을 Store에 복사
        Images 폴더에 같은 이름의 디렉토리 내용도 함께 복사
        """
        # source_json_path =
        # '/Users/limdeokyu/Files/LA-Scenario0010/LA-Scenario0010.json'
        name = pathlib.Path(source_json_path).name
        source_images_dir = self.get_images_dir(source_json_path)
        store_image_dir = self.get_store_image_dir()
        store_image_dir = str(pathlib.Path(store_image_dir, name))

        # Bot 파일들 복사
        try:
            shutil.copy(source_json_path, self.store_path)
            shutil.copytree(source_images_dir, store_image_dir)
        except FileExistsError as e:
            print(e)
            return False
        if not pathlib.Path(self.store_path).exists() \
                or not pathlib.Path(store_image_dir).exists():
            raise
        return True
