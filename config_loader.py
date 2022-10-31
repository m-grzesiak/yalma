import codecs
import platform
from configparser import ConfigParser
from pathlib import Path

__CONFIGURATION_FILE_NAME = "config.ini"


class ConfigurationValidationException(Exception):
    pass


def initialize_app_configuration():
    configuration_directory_path = __get_configuration_directory_path()
    Path(configuration_directory_path).mkdir(parents=False, exist_ok=True)
    path_to_config_file = configuration_directory_path + __CONFIGURATION_FILE_NAME
    Path(path_to_config_file).touch()


def read_configuration(configuration_section: str, expected_mandatory_fields: [] = ()) -> {}:
    path_to_config_file = __get_configuration_directory_path() + __CONFIGURATION_FILE_NAME
    config_parser = ConfigParser()

    with codecs.open(path_to_config_file, "r", encoding="utf-8") as config_file:
        config_parser.read_file(config_file)
        configuration = dict(config_parser.items(configuration_section))

        for field in expected_mandatory_fields:
            if not configuration.get(field):
                error_message = __prepare_validation_error_message(configuration_section, field)
                raise ConfigurationValidationException(error_message)

        return configuration


def __get_configuration_directory_path() -> str:
    current_platform = platform.system()
    user_home_path = Path.home()

    if current_platform == "Linux" or current_platform == "Darwin":
        return str(user_home_path) + "/.config/yalma/"
    else:
        if current_platform == "Windows":
            return str(user_home_path) + "/AppData/Local/yalma/"


def __prepare_validation_error_message(configuration_section, field) -> str:
    return f"A value for field '{field}' in section '{configuration_section}' is not set in a " \
           f"{__CONFIGURATION_FILE_NAME} file"
