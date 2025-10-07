import re
import logging
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import yaml
from minify_html import minify
from jinja2 import Environment, FileSystemLoader

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

data_file_path = Path("./data/winsoft6.app.yml")
export_file_path = Path("./docs/index.html")

log.debug("Loading data.")

data = yaml.safe_load(data_file_path.read_text(encoding="utf-8"))

log.debug("Loading template.")

def sanitize_id(value: str) -> str:
    """將輸入清洗成安全的 HTML id 格式"""
    if not value:
        return ""

    value = value.strip().lower()
    value = re.sub(r'[<>#"%{}|\\^~\[\]`;/?:@=&]', '', value)
    value = re.sub(r'\s+', '_', value)
    return value

env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True
)
env.filters["sanitize_id"] = sanitize_id
template = env.get_template("winsoft.html.j2")

log.debug("rendering page.")

html = template.render(
    contents=data["contents"],
    now=datetime.now(ZoneInfo("Asia/Taipei"))
)

before_size = len(html.encode("utf-8"))

log.debug("Compressing page.")

minified = minify(html)

after_size = len(minified.encode("utf-8"))
compression_ratio = (1 - after_size / before_size) * 100

log.info(
    "HTML size: %d → %d bytes (%.2f%% smaller)",
    before_size, after_size, compression_ratio
)

export_file_path.write_text(minified, encoding="utf-8")
logging.info("Render success.")
