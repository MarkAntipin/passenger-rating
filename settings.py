from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    TITLE: str = 'passenger rating service Api'
    VERSION: str = '0..0.1'

    PG_HOST: str
    PG_PORT: int
    PG_USER: str
    PG_PASSWORD: str
    PG_DATABASE: str

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
