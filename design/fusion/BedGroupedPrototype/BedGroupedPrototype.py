import traceback
from pathlib import Path
ROOT=Path("/Users/ivanyalov/Desktop/Bed prototype")
def run(context):
    log=ROOT/".cache/grouped-cad/run.log"
    log.write_text("RUNNING\n")
    try:
        source=ROOT/"design/fusion/grouped_bed.py"
        ns={"__name__":"bed_grouped_builder","__file__":str(source)}
        exec(compile(source.read_text(),str(source),"exec"),ns)
        ns["build_and_export"](ROOT)
        with log.open("a") as f:f.write("COMPLETE\n")
    except Exception:
        with log.open("a") as f:f.write("FAILED\n"+traceback.format_exc())
        print(traceback.format_exc())
