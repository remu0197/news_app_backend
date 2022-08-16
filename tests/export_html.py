import sys
import requests

def export_html(url, filepath):
    response = requests.get(url, timeout=10)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(response.text)

if __name__ == "__main__":
    args = sys.argv[1:]
    filepath = "../tests/resource/" + args[1] + ".html"
    export_html(
        url=args[0],
        filepath=filepath
    )
