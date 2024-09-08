#!/usr/bin/env python3

import re, os, json
from urllib.request import urlopen


def simple_asset(asset):
    d = {}
    for k in ["name", "browser_download_url", "size"]:
        d[k] = asset[k]
    return d


def find_asset(assets, key, ext):
    for asset in assets:
        name = asset["name"]
        if re.search(rf"\b{key}\b", name) and re.search(rf"\b{ext}\b", name):
            return asset
    raise ValueError("Asset not found")


def wget(url):
    print(f"wget: {url}")
    resp = urlopen(url)
    if resp.status != 200:
        print(f"error: {resp.status}")
        raise OSError("Download failed.")
    return resp.read().decode("utf-8")


def main():
    root_dir = os.getcwd()
    print(f"set root dir: {root_dir}")
    output_dir = os.path.join(root_dir, "_site")
    print(f"set output dir: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    # fetch json from github:
    url = "https://api.github.com/repos/riscv/riscv-isa-manual/releases/latest"
    data = json.loads(wget(url))
    published_at = data["published_at"]
    version = published_at[: published_at.find("T")]
    print(f"version: {version}")
    assets = [simple_asset(asset) for asset in data["assets"]]
    print(f"assets: {', '.join([asset['name'] for asset in assets])}")
    unprivileged_html = find_asset(assets, "unprivileged", "html")
    unprivileged_pdf = find_asset(assets, "unprivileged", "pdf")
    unprivileged_epub = find_asset(assets, "unprivileged", "epub")
    privileged_html = find_asset(assets, "privileged", "html")
    privileged_pdf = find_asset(assets, "privileged", "pdf")
    privileged_epub = find_asset(assets, "privileged", "epub")

    # download html:
    with open(os.path.join(output_dir, "unprivileged.html"), "w") as f:
        f.write(wget(unprivileged_html["browser_download_url"]))
    with open(os.path.join(output_dir, "privileged.html"), "w") as f:
        f.write(wget(privileged_html["browser_download_url"]))

    # generate index.html:
    with open(os.path.join(root_dir, "index.html"), "r") as f:
        index_html = f.read()
    index_html = index_html.replace("{VERSION}", version)
    index_html = index_html.replace("{UNPRIVILEGED_PDF}", unprivileged_pdf["browser_download_url"])
    index_html = index_html.replace("{UNPRIVILEGED_EPUB}", unprivileged_epub["browser_download_url"])
    index_html = index_html.replace("{PRIVILEGED_PDF}", privileged_pdf["browser_download_url"])
    index_html = index_html.replace("{PRIVILEGED_EPUB}", privileged_epub["browser_download_url"])
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(index_html)

    print("ok.")


if __name__ == "__main__":
    main()
