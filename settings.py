import pathlib

# Get directory this file resides in (should be the project root directory).
PROJECT_ROOT_DIR = pathlib.Path(__file__).parent.absolute()
DATABASE_FILENAME = 'sane-psh.db'
DATABASE_PATH = PROJECT_ROOT_DIR.joinpath(DATABASE_FILENAME)
CONFIG_PATH = PROJECT_ROOT_DIR.joinpath('config.json')
SAMPLE_CONFIG_PATH = PROJECT_ROOT_DIR.joinpath('config.json.sample')
LOG_DIR = PROJECT_ROOT_DIR.joinpath('logs')
LOG_FILE = LOG_DIR.joinpath('sane-psh.log')