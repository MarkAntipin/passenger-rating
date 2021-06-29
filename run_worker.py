import importlib

import click

# from my_rabbit.get_rabbit_connection import get_rabbit_connection, ConnectionType


@click.command()
@click.option('--worker', '-w')
def run_worker(worker):
    module = importlib.import_module(f'workers.{worker}')
    module.run()


if __name__ == "__main__":
    run_worker()
