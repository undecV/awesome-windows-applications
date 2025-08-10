from jinja2 import Environment, PackageLoader
import yaml

WINSOFT_PATH = "winsoft\winsoft.yml"

with open(WINSOFT_PATH, 'r') as fp:
    winsoft = yaml.safe_load(fp)

version = winsoft["meta"]["version"][0]["ver"]

def subi_classify(e, init="subi"):
    e["recr"] = {}
    e["recr"]["eles"] = []
    e["recr"]["flds"] = []
    for i in e[init]:
        if 'type' in i and i['type'] in ("folder", ):
            e["recr"]["flds"].append(i)
            if "subi" in i:
                i = subi_classify(i, "subi")
        else:
            e["recr"]["eles"].append(i)
    return e

winsoft = subi_classify(winsoft, "data")
# print(yaml.dump(winsoft, allow_unicode=True))

def isdisjoint(a, b):
    return set(a).isdisjoint(set(b))

def foss_str(i):
    """Not stable, Not safe."""
    if i["lice"] not in ("Proprietary", ):
        return '自由'
    if (i["lice"] in ("Proprietary", )) and ("cost" in i) and (i["cost"] in ("paid", )):
        return '商業'

env = Environment(
    loader=PackageLoader('winsoft'),
)
env.add_extension('jinja2.ext.loopcontrols')
# env.trim_blocks = True
# env.lstrip_blocks = True
env.globals['foss_str'] = foss_str
env.globals['isdisjoint'] = isdisjoint

# template = env.get_template('t.html.j2')
template = env.get_template('template.md.j2')
with open(f'Winsoft_{version}.md', 'w') as fp:
    fp.write(template.render(**winsoft))
