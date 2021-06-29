import pika
from pydantic import BaseSettings


class RabbitConfig(BaseSettings):
    url: str = None
    host: str = 'localhost'
    port: int = 5672
    virtualhost: str = '/'
    login: str = 'guest'
    password: str = 'guest'
    ssl: bool = False

    @property
    def credentials(self):
        return pika.PlainCredentials(self.login, self.password)

    def __hash__(self):
        return hash(tuple(self.dict().keys()))


_CONF_NAME = 'default'
_GLOBAL_CONFIG = {
    _CONF_NAME: RabbitConfig()
}


def set_config(
        config: RabbitConfig = None,
        url: str = None,
        host: str = 'localhost',
        port: int = 5672,
        login: str = 'guest',
        password: str = 'guest',
        virtualhost: str = '/',
        ssl: bool = False,
):
    """Set global config for rabbitmq from `config` or from passed params
    """
    if config:
        _GLOBAL_CONFIG[_CONF_NAME] = config
        return
    config = RabbitConfig(
        url=url,
        host=host,
        port=port,
        login=login,
        password=password,
        virtualhost=virtualhost,
        ssl=ssl
    )
    _GLOBAL_CONFIG[_CONF_NAME] = config


def get_config():
    """Get global config for rabbitmq
    """
    return _GLOBAL_CONFIG[_CONF_NAME]
