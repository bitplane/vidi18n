"""
Main entrypoint for testing.
"""
from functools import partial
from multiprocessing import Process
from pkgutil import get_loader, iter_modules

from vidi18n.services import ALL_PACKAGES


def main():
    services = [__import__(p, fromlist=["run"]) for p in ALL_PACKAGES]
    names = [service.__name__ for service in services]
    short_names = [name.split(".")[-2] for name in names]
    print("Services:", ", ".join(short_names))

    entrypoints = [service.main for service in services]
    processes = [Process(target=t) for t in entrypoints]
    process_dict = {name: process for name, process in zip(short_names, processes)}

    for service, process in process_dict.items():
        print("Starting", service)
        process.start()

    print("Startup complete, waiting for processes to finish...")

    for service, process in process_dict.items():
        process.join()
        print(service, "finished")

    print("All processes finished, exiting...")


if __name__ == "__main__":
    main()
