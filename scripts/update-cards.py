"""Fetch public GitHub Readme Stats-compatible SVG snapshots."""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import os
import time
import xml.etree.ElementTree as ET

owner = os.environ.get("PROFILE_OWNER", "rokmc1893")
common = dict(username=owner, theme="radical", bg_color="0D1117",
              title_color="FF3535", icon_color="FF3535",
              text_color="C9D1D9", border_color="30363D")
cards = [
    ("stats.svg", "", dict(show_icons="true", include_all_commits="true",
                           hide_rank="true", custom_title="Season Telemetry",
                           card_width="495")),
    ("top-langs.svg", "/top-langs", dict(layout="compact", langs_count="6",
                                        card_width="495",
                                        custom_title="Power Unit Languages")),
    ("pin-healthcare.svg", "/pin", dict(repo="Capstone-Design")),
    ("pin-legal.svg", "/pin", dict(repo="Google_AI_Agent")),
    ("pin-policy.svg", "/pin", dict(repo="INU-X-UOU")),
]
output = Path("profile")
pending = {}
for filename, route, options in cards:
    url = "https://github-stats-extended.vercel.app/api" + route
    url += "?" + urlencode({**common, **options})
    for attempt in range(3):
        try:
            request = Request(url, headers={"User-Agent": "racing-profile/1.0"})
            with urlopen(request, timeout=45) as response:
                data = response.read()
            root = ET.fromstring(data)
            if root.tag != "{http://www.w3.org/2000/svg}svg":
                raise ValueError("Response is not an SVG image")
            visible = " ".join(
                " ".join(node.itertext()) for node in root.iter()
                if node.tag.rsplit("}", 1)[-1] in ("title", "desc", "text")
            ).lower()
            errors = ("something went wrong", "could not resolve",
                      "please deploy your own", "rate limit exceeded")
            if any(message in visible for message in errors):
                raise ValueError("Service returned an error card")
            pending[filename] = data
            print(f"Validated {filename}: {len(data)} bytes")
            break
        except (HTTPError, URLError, TimeoutError, ValueError, ET.ParseError):
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))
output.mkdir(exist_ok=True)
for filename, data in pending.items():
    (output / filename).write_bytes(data)
