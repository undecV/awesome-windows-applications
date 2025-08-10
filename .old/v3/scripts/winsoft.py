from pathlib import Path
import yaml  # pip install pyyaml
from datetime import datetime


# ===== Setting ====================================

data_path = Path("winsoft.yml")
head_md = Path("head.md")
foot_md = Path("foot.md")
output_md = Path("winsoft.md")
flags_filter = ['Abandon', 'Pro', 'Old', 'Discontinued']

# ==================================================

print(f'Flags filter: {flags_filter}')


def subline(i):
    sl = []
    if "flag" in i:
        sl.append(f'[{", ".join([f"`{f}`" for f in i["flag"]])}]')
    if "cmnt" in i:
        sl.append(f'{i["cmnt"]}')
    if "tags" in i:
        sl.append(f'[{", ".join([f"`{f}`" for f in i["tags"]])}]')
    if "refs" in i:
        for ref in i["refs"]:
            sl.append(f'([{ref["text"]}]({ref["href"]}))')
    return sl


def iter_folder(i, head_level, indent_level):
    text = f'{"#" * head_level} '
    text += f'{i["text"]}\n\n' if "link" not in i else f'[{i["text"]}]({i["link"]})\n\n'
    sl = subline(i)
    if sl:
        text += f'{" ".join(sl)}\n\n'
    return text


def iter_element(i, head_level, indent_level):
    text = "    " * indent_level + "- "
    foss = ''
    if "lice" in i:
        if i["lice"] not in ("Proprietary", ):
            foss += '`自由` '
        if (i["lice"] in ("Proprietary", )) and ("cost" in i) and (i["cost"] in ("paid", )):
            foss += "`商業` "
    text += foss
    text += f'**{i["text"]}**: ' if "link" not in i else f'[**{i["text"]}**]({i["link"]}): '
    sl = subline(i)
    if sl:
        text += f'{" ".join(sl)}'
    return text +'\n'


text = f"<!-- flags_filter: {flags_filter} -->\n\n"
folderc = 0
elementc = 0
ignoredc = 0


def iter_winsoft(subi, head_level, indent_level):
    global text
    global folderc
    global elementc
    global ignoredc

    for i in subi:
        if ("flag" in i) and any(flag in flags_filter for flag in i["flag"]):
            ignoredc += 1
            print(f'ignored {ignoredc:>4d}: {i["text"]}')
            continue
        if "type" in i and i["type"] in ("folder", ):  # folder
            print(f'folder  {folderc:>4d}: {i["text"]}')
            folderc += 1
            text += '\n' if text[-2:] != '\n\n' else ''
            text += iter_folder(i, head_level, indent_level)
            if "subi" in i:
                iter_winsoft(i["subi"], head_level + 1, indent_level)
        else:  # element
            print(f'element {elementc:>4d}: {i["text"]}')
            elementc += 1
            text += iter_element(i, head_level, indent_level)
            if "subi" in i:
                iter_winsoft(i["subi"], head_level, indent_level + 1)


def main():
    global text
    now_str = datetime.now().strftime("%Y-%m-%d %H:00:00")

    with open(data_path) as fp:
        doc = yaml.safe_load(fp)

    iter_winsoft(doc["data"], 3, 0)

    text += '\n'
    text += f'<!-- folder_count: {folderc} -->\n'
    text += f'<!-- element_count: {elementc} -->\n'
    text += f'<!-- ignored_count: {ignoredc} -->\n'
    text += f'<!-- build_tile: {now_str} -->\n'

    hffmt = {"date": now_str, "modified": now_str}
    hffmt.update(doc["meta"])

    with open(head_md) as fp:
        head = fp.read().format(**hffmt) + '\n'
    with open(foot_md) as fp:
        foot = '\n' + fp.read().format(**hffmt)
    with open(output_md, mode='w') as fp:
        fp.write(head)
        fp.write(text)
        fp.write(foot)


if __name__ == "__main__":
    main()
