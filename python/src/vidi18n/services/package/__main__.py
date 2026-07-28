from vidi18n.common.settings import STREAM_PACKAGE
from vidi18n.common.workflow import run_worker
from vidi18n.services.package.listeners import package_chunk


def main():
    run_worker(
        STREAM_PACKAGE,
        "package",
        package_chunk,
        readiness={"status": "ready"},
    )


if __name__ == "__main__":
    main()
