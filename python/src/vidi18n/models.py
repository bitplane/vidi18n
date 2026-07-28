import argparse
import json
import os
import tempfile
import wave
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path


def model_root() -> Path:
    return Path(os.environ.get("VIDI18N_MODEL_ROOT", "/models"))


def bootstrap():
    root = model_root()
    root.mkdir(parents=True, exist_ok=True)
    model_name = os.environ.get("VIDI18N_WHISPER_MODEL", "tiny.en")

    from faster_whisper import WhisperModel

    WhisperModel(model_name, download_root=str(root), device="cpu")

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

    manifest = {
        "schema_version": 1,
        "bootstrapped_at": datetime.now(timezone.utc).isoformat(),
        "transcribe": {
            "engine": "faster-whisper",
            "engine_version": version("faster-whisper"),
            "model": model_name,
            "revision": whisper_revision(root, model_name),
        },
        "translate": {
            "engine": "argostranslate",
            "engine_version": version("argostranslate"),
            "package": "translate-en_fr",
            "package_version": getattr(package, "package_version", None),
        },
    }
    target = root / "manifest.json"
    temporary = root / "manifest.json.tmp"
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, target)
    verify()


def whisper_revision(root: Path, model_name: str) -> str | None:
    reference = (
        root
        / f"models--Systran--faster-whisper-{model_name}"
        / "refs"
        / "main"
    )
    return reference.read_text().strip() if reference.exists() else None


def verify():
    root = model_root()
    manifest_path = root / "manifest.json"
    if not manifest_path.exists():
        raise RuntimeError("Model manifest is missing; run bootstrap first")
    manifest = json.loads(manifest_path.read_text())

    from faster_whisper import WhisperModel

    whisper = WhisperModel(
        manifest["transcribe"]["model"],
        download_root=str(root),
        device="cpu",
        compute_type="int8",
        local_files_only=True,
    )
    with tempfile.NamedTemporaryFile(suffix=".wav") as audio:
        with wave.open(audio.name, "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(16000)
            output.writeframes(b"\0\0" * 16000)
        list(whisper.transcribe(audio.name, language="en")[0])

    import argostranslate.translate

    translated = argostranslate.translate.translate("Hello", "en", "fr")
    if not translated or translated.lower() == "hello":
        raise RuntimeError("Argos English-to-French verification failed")
    print(json.dumps({"status": "ok", "manifest": manifest}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["bootstrap", "verify"])
    args = parser.parse_args()
    if args.command == "bootstrap":
        bootstrap()
    else:
        verify()


if __name__ == "__main__":
    main()
