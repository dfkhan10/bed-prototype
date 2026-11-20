"""Compatibility entry: rebuild the grouped CAD in a new Fusion document."""
from pathlib import Path
ROOT=Path("/Users/ivanyalov/Desktop/Bed prototype")
def run(context):
    source=ROOT/"design/fusion/grouped_bed.py"
    ns={"__name__":"bed_grouped_builder","__file__":str(source)}
    exec(compile(source.read_text(),str(source),"exec"),ns)
    ns["build_and_export"](ROOT)
