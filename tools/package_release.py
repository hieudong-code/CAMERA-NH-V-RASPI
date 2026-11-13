"""Create a versioned ZIP from committed files only; no credentials or .git."""
import argparse
import io
from pathlib import Path
import re
import subprocess
import zipfile

PROJECT = "robot_hai_banh"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = subprocess.check_output(
        ["git", "show", "HEAD:VERSION"], cwd=root, text=True
    ).strip()
    if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version):
        raise SystemExit("VERSION must be a committed major.minor.patch value")
    name = f"{PROJECT}_v{version}"
    data = subprocess.check_output(
        ["git", "archive", "--format=zip", f"--prefix={name}/", "HEAD"], cwd=root
    )
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if archive.testzip() is not None:
            raise SystemExit("Invalid ZIP")
        names = archive.namelist()
        if any(not p.startswith(name + "/") or ".." in Path(p).parts for p in names):
            raise SystemExit("Unsafe archive paths")
    outdir = (args.output_dir or root / "dist").resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / (name + ".zip")
    if path.exists() and path.read_bytes() != data:
        raise SystemExit("This version already has a different ZIP; increase VERSION")
    path.write_bytes(data)
    print(path)


if __name__ == "__main__":
    main()
