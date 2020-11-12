import codecs
from configparser import ConfigParser

_CONFIGURATION_FILE_NAME = 'config.ini'


class ConfigurationValidationException(Exception):
    pass


def _prepare_validation_error_message(configuration_section, field):
    return "A value for field '{}' in section '{}' is not set in a {} file".format(field,
                                                                                   configuration_section,
                                                                                   _CONFIGURATION_FILE_NAME)


def read_configuration(configuration_section: str, expected_mandatory_fields: [] = ()) -> {}:
    config_parser = ConfigParser()
    with codecs.open(_CONFIGURATION_FILE_NAME, 'r', encoding='utf-8') as config_file:
        config_parser.read_file(config_file)
        configuration = dict(config_parser.items(configuration_section))

        for field in expected_mandatory_fields:
            if not configuration.get(field):
                error_message = _prepare_validation_error_message(configuration_section, field)
                raise ConfigurationValidationException(error_message)

        return configuration
