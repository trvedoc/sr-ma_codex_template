"""Run the artificial example without changing the review's data files."""
from pathlib import Path
import shutil
import subprocess
import sys
from demo_fixture import create_demo

root = Path(__file__).resolve().parents[1]
destination = root / 'work/demo-project'
try:
    create_demo(root, destination)
except FileExistsError as exc:
    raise SystemExit(f'{exc}\nMove the old demo folder before running a new one.')
rscript = shutil.which('Rscript')
if not rscript:
    raise SystemExit('Demo folder created. Install R and run analysis/setup.R before running it.')
result = subprocess.run([rscript, str(destination / 'analysis/run.R'), '--root', str(destination)])
sys.exit(result.returncode)
