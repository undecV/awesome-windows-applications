"""Awesome Applications webpage renderer script."""

import logging
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from jinja2 import Environment, FileSystemLoader
from minify_html import minify

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

data_file_path = Path("./data/winsoft6.app.yml")
export_file_path = Path("./docs/index.html")

logger.debug("Loading data.")

data = yaml.safe_load(data_file_path.read_text(encoding="utf-8"))

logger.debug("Loading template.")


def sanitize_id(value: str) -> str:
    """Sanitize a string into a safe identifier."""
    if not value:
        return ""

    value = value.strip().lower()
    value = re.sub(r'[<>#"%{}|\\^~\[\]`;/?:@=&]', "", value)
    value = re.sub(r"\s+", "_", value)
    return value


env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=False,  # noqa: S701  # All snippets are loaded from locally.
)
env.filters["sanitize_id"] = sanitize_id
template = env.get_template("winsoft.html.j2")

logger.debug("rendering page.")

html = template.render(
    contents=data["contents"],
    now=datetime.now(ZoneInfo("Asia/Taipei")),
)

before_size = len(html.encode("utf-8"))

logger.debug("Compressing page.")

minified = minify(html, minify_css=True, minify_js=True)

after_size = len(minified.encode("utf-8"))
compression_ratio = (1 - after_size / before_size) * 100

logger.info(
    "HTML size: %d → %d bytes (%.2f%% smaller)",
    before_size,
    after_size,
    compression_ratio,
)

export_file_path.write_text(minified, encoding="utf-8")
logger.info("Render success.")
print("Render success. Output:", export_file_path.resolve().as_uri())
