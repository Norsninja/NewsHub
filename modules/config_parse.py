import configparser

# Load the configuration file
config = configparser.ConfigParser()
config.read('modules/suite_config.ini')

# Print out the sections
print(config.sections())