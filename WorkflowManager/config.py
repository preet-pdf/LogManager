import configparser

config = configparser.ConfigParser()
config.read('../getting_started.ini')

bootstrap_servers = config['default']['bootstrap.servers']
group_id = config['consumer']['group.id']
auto_offset_reset = config['consumer']['auto.offset.reset']
topic = 'logs_consumer'
bulk_size=10
bulk_timeout_seconds=30
index_name = 'index_dyte'
