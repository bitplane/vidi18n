#!/usr/bin/env python3

import sys

import toml


def extract_deps(pyproject_path, temp_file, sections):
    with open(pyproject_path, "r") as f:
        data = toml.load(f)

    project = data["project"]

    deps = project.get("dependencies", [])
    for section in sections.split(","):
        deps += project.get("optional-dependencies", {}).get(section, [])

    with open(temp_file, "w") as f:
        for dep in deps:
            f.write(f"{dep}\n")


if __name__ == "__main__":
    sections = sys.argv[1]
    extract_deps("pyproject.toml", f"requirements_{sections}.txt", sections)
