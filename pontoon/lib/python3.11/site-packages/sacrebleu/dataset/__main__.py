import sys

from . import DATASETS

try:
    cmd = sys.argv[1]
except IndexError:
    print(f"Usage: {sys.argv[0]} --check | --dump")
    sys.exit(1)

if cmd == "--check":
    import hashlib
    import urllib.request

    url_md5 = {}

    for item in DATASETS.values():
        if item.md5 is not None:
            assert item.data
            assert item.md5
            assert len(item.data) == len(item.md5)
            pairs = zip(item.data, item.md5)
            for url, md5_hash in pairs:
                url_md5[url] = md5_hash

    for url, md5_hash in url_md5.items():
        try:
            print("Downloading ", url)
            with urllib.request.urlopen(url) as f:
                data = f.read()
        except Exception as exc:
            raise (exc)

        if hashlib.md5(data).hexdigest() != md5_hash:
            print("MD5 check failed for", url)
elif cmd == "--dump":
    import re

    # Dumps a table in markdown format
    print(f'| {"Dataset":<30} | {"Description":<115} |')
    header = "| " + "-" * 30 + " | " + "-" * 115 + " |"
    print(header)
    for name, item in DATASETS.items():
        desc = re.sub(r"(http[s]?:\/\/\S+)", r"[URL](\1)", str(item.description))
        print(f"| {name:<30} | {desc:<115} |")
