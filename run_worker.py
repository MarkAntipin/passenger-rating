import importlib

import click

# from my_rabbit.get_rabbit_connection import get_rabbit_connection, ConnectionType


@click.command()
@click.option('--worker', '-w')
def run_worker(worker):
    module = importlib.import_module(f'workers.{worker}')
    conn = get_rabbit_connection(ConnectionType.CONSUMER)
    module.run(conn)


if __name__ == "__main__":
    run_worker()
