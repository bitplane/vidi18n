import argparse
import os


def bootstrap():
    model_root = os.environ.get("VIDI18N_MODEL_ROOT", "/models")
    os.makedirs(model_root, exist_ok=True)

    from faster_whisper import WhisperModel

    WhisperModel(
        os.environ.get("VIDI18N_WHISPER_MODEL", "tiny.en"),
        download_root=model_root,
        device="cpu",
    )

    import argostranslate.package

    argostranslate.package.update_package_index()
    packages = argostranslate.package.get_available_packages()
    package = next(
        item
        for item in packages
        if item.from_code == "en" and item.to_code == "fr"
    )
    installed = argostranslate.package.get_installed_packages()
    if not any(item.from_code == "en" and item.to_code == "fr" for item in installed):
        argostranslate.package.install_from_path(package.download())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["bootstrap"])
    args = parser.parse_args()
    if args.command == "bootstrap":
        bootstrap()


if __name__ == "__main__":
    main()
