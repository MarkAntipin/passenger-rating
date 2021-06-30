from pydantic import BaseSettings, PostgresDsn

from my_rabbit import RabbitConfig, set_config


class Settings(BaseSettings):
    TITLE: str = 'passenger rating service Api'
    VERSION: str = '0..0.1'

    PG_HOST: str
    PG_PORT: int
    PG_USER: str
    PG_PASSWORD: str
    PG_DATABASE: str

    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    def rabbitmq_conn(self):
        RabbitConfig(
            login=self.RABBITMQ_USER,
            password=self.RABBITMQ_PASSWORD,
            host=self.RABBITMQ_HOST,
            port=self.RABBITMQ_PORT,

        )

    def pg_url(self) -> str:
        return PostgresDsn.build(
            scheme='postgresql',
            user=self.PG_USER,
            password=self.PG_PASSWORD,
            host=self.PG_HOST,
            path=f'/{self.PG_DATABASE}',
        )

    class Config:
        env_file = '.env'


settings = Settings()
set_config(config=settings.rabbitmq_conn())
