import configparser

config = configparser.ConfigParser()
config.read('../getting_started.ini')
bootstrap_servers = config['default']['bootstrap.servers']
topic = 'logs_consumer'
index_name = 'index_dyte'