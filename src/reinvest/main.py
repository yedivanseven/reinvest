from swak.cli import Importer
from .config import config, actions


import_steps = Importer(config.package)
steps = import_steps(*actions)


def run() -> None:
    for step in steps:
        step()


if __name__ == '__main__':
    run()
