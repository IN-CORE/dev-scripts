#!/usr/bin/env python
"""Execute the incore-docs notebooks one by one and write a pass/fail report.

Each notebook runs in its own fresh kernel inside a scratch copy of the
incore-docs ``notebooks/`` folder, so the incore-docs checkout is never
modified. Zipped notebooks (the testbeds and the create_* how-tos) are
extracted into their own folder first so their relative data paths still work.

Run it with the python of the environment you want to test (the kernel uses
that interpreter), for example:

    conda activate pyincore
    ./utils/pyincore_utils/run_docs_notebooks.py --docs-root /path/to/incore-docs
    INCORE_DOCS_ROOT=../incore-docs ./utils/pyincore_utils/run_docs_notebooks.py --list
    ./utils/pyincore_utils/run_docs_notebooks.py --docs-root ../incore-docs building_dmg.ipynb "*_testbed*"
    ./utils/pyincore_utils/run_docs_notebooks.py --docs-root ../incore-docs --jobs 4 --timeout 3600

Requirements in that environment: pyincore (+ pyincore-viz / pyincore-data for
the notebooks that use them), nbclient, nbformat, ipykernel, pyyaml.

Per-notebook skips and timeouts live in docs_notebooks_skip.yml next to this
script (override with --skip-file). Output goes to logs/docs_notebooks/<timestamp>/
(override with --out): report.md, results.json and the executed notebooks.

Auth: before running, the script makes sure a valid IN-CORE token is cached.
If ``INCORE_TOKEN`` is set it is written to pyincore's token cache; otherwise
``IncoreClient()`` is created once here and prompts in the terminal if needed.
Notebooks that still try to prompt fail immediately instead of hanging.

Other environment variables (``CENSUS_API_KEY``, ...) are passed through to the
kernels unchanged.
"""

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import shutil
import sys
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKIP_FILE = SCRIPT_DIR / "docs_notebooks_skip.yml"
NOTEBOOKS_DIR = None  # set in main() from --docs-root / INCORE_DOCS_ROOT
ZIP_SUFFIX = "__zip"  # extracted zips live in <stem>__zip/ inside the work dir


# ---------------------------------------------------------------------------
# discovery
# ---------------------------------------------------------------------------
def _ignore(_dir, names):
    return [
        n
        for n in names
        if n.endswith(".zip")
        or n in (".ipynb_checkpoints", "__MACOSX", "ci", ".DS_Store")
    ]


def stage(work_dir: Path):
    """Copy notebooks/ into work_dir, extract zips, return {id: path}."""
    shutil.copytree(NOTEBOOKS_DIR, work_dir, ignore=_ignore)
    found = {}
    for nb in sorted(work_dir.glob("*.ipynb")):
        found[nb.name] = nb

    for zp in sorted(NOTEBOOKS_DIR.glob("*.zip")):
        dest = work_dir / (zp.stem + ZIP_SUFFIX)
        with zipfile.ZipFile(zp) as zf:
            members = [
                m
                for m in zf.namelist()
                if not m.startswith("__MACOSX/") and "/._" not in "/" + m
            ]
            zf.extractall(dest, members)
        for nb in sorted(dest.rglob("*.ipynb")):
            if ".ipynb_checkpoints" in nb.parts:
                continue
            found[f"{zp.name}/{nb.relative_to(dest).as_posix()}"] = nb
    return found


def list_ids():
    """Notebook ids without staging anything (used by --list)."""
    ids = [p.name for p in sorted(NOTEBOOKS_DIR.glob("*.ipynb"))]
    for zp in sorted(NOTEBOOKS_DIR.glob("*.zip")):
        with zipfile.ZipFile(zp) as zf:
            for m in zf.namelist():
                if (
                    m.endswith(".ipynb")
                    and not m.startswith("__MACOSX/")
                    and ".ipynb_checkpoints" not in m
                    and "/._" not in "/" + m
                ):
                    ids.append(f"{zp.name}/{m}")
    return ids


def load_rules(skip_file):
    if not skip_file.exists():
        return {}
    import yaml

    data = yaml.safe_load(skip_file.read_text()) or {}
    return data.get("notebooks", {}) or {}


def rule_for(nb_id, rules):
    """Merge every rule whose glob matches the id (later entries win)."""
    merged = {}
    for pattern, rule in rules.items():
        if fnmatch.fnmatch(nb_id, pattern):
            merged.update(rule or {})
    return merged


def select(ids, patterns, rules, run_skipped):
    selected, skipped = [], []
    for nb_id in ids:
        if patterns and not any(fnmatch.fnmatch(nb_id, p) for p in patterns):
            continue
        rule = rule_for(nb_id, rules)
        if rule.get("skip") and not run_skipped:
            skipped.append((nb_id, rule["skip"]))
        else:
            selected.append((nb_id, rule))
    return selected, skipped


# ---------------------------------------------------------------------------
# auth
# ---------------------------------------------------------------------------
def ensure_token():
    from pyincore import IncoreClient, globals as pyglobals

    token = os.environ.get("INCORE_TOKEN", "").strip()
    if token:
        if not token.lower().startswith("bearer "):
            token = "bearer " + token
        url = pyglobals.INCORE_API_PROD_URL
        hashed = hashlib.sha256(url.encode()).hexdigest()
        os.makedirs(pyglobals.PYINCORE_USER_CACHE, exist_ok=True)
        token_file = os.path.join(pyglobals.PYINCORE_USER_CACHE, f".{hashed}_token")
        with open(token_file, "w") as f:
            f.write(token)
        os.chmod(token_file, 0o600)
    # Validates the cached token, or prompts for username/password here once.
    try:
        IncoreClient()
    except EOFError:
        sys.exit(
            "No valid IN-CORE token is cached and there is no terminal to log in from.\n"
            "Run once interactively, set INCORE_TOKEN, or pass --no-auth-check."
        )


# ---------------------------------------------------------------------------
# execution (runs in a worker process)
# ---------------------------------------------------------------------------
def first_error(nb):
    for idx, cell in enumerate(nb.cells):
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                src = cell.get("source", "")
                return {
                    "cell": idx,
                    "ename": out.get("ename", ""),
                    "evalue": out.get("evalue", "")[:500],
                    "source": src[:300],
                }
    return None


def execute(nb_id, nb_path, out_path, timeout, kernel):
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError, CellTimeoutError, DeadKernelError

    os.environ.setdefault("MPLBACKEND", "Agg")
    nb = nbformat.read(nb_path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=timeout,
        kernel_name=kernel,
        allow_errors=False,
        record_timing=True,
        resources={"metadata": {"path": str(Path(nb_path).parent)}},
    )
    start = time.time()
    status, error = "pass", None
    try:
        client.execute()
    except CellTimeoutError as e:
        status, error = "timeout", {"ename": "CellTimeoutError", "evalue": str(e)[:500]}
    except DeadKernelError as e:
        status, error = "fail", {"ename": "DeadKernelError", "evalue": str(e)[:500]}
    except CellExecutionError:
        status, error = "fail", first_error(nb)
    except Exception as e:  # kernel start failures, bad notebook json, ...
        status, error = "error", {"ename": type(e).__name__, "evalue": str(e)[:500]}
    duration = time.time() - start

    out_path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, out_path)
    if status == "fail" and error is None:
        error = first_error(nb)
    return {
        "id": nb_id,
        "status": status,
        "seconds": round(duration, 1),
        "error": error,
        "executed": str(out_path),
    }


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def write_report(run_dir, results, skipped, meta):
    (run_dir / "results.json").write_text(
        json.dumps({"meta": meta, "results": results, "skipped": skipped}, indent=2)
    )
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    lines = [
        f"# Notebook run {meta['started']}",
        "",
        f"- notebooks: `{meta['notebooks']}`",
        f"- python: `{meta['python']}`",
        f"- versions: {', '.join(f'{k} {v}' for k, v in meta['versions'].items())}",
        f"- result: {', '.join(f'{v} {k}' for k, v in sorted(counts.items()))}"
        f", {len(skipped)} skipped",
        "",
        "| notebook | status | time | error |",
        "|---|---|---|---|",
    ]
    order = {"fail": 0, "error": 1, "timeout": 2, "pass": 3}
    for r in sorted(results, key=lambda r: (order.get(r["status"], 9), r["id"])):
        err = ""
        if r["error"]:
            e = r["error"]
            cell = f"cell {e['cell']}: " if "cell" in e else ""
            msg = (e.get("evalue") or "").splitlines()[0][:150] if e.get("evalue") else ""
            err = f"{cell}`{e.get('ename', '')}` {msg}".replace("|", "\\|")
        lines.append(f"| {r['id']} | {r['status']} | {r['seconds']:.0f}s | {err} |")
    if skipped:
        lines += ["", "## Skipped", ""]
        lines += [f"- {nb_id}: {reason}" for nb_id, reason in skipped]
    (run_dir / "report.md").write_text("\n".join(lines) + "\n")


def package_versions():
    from importlib.metadata import PackageNotFoundError, version

    out = {}
    for pkg in ("pyincore", "pyincore-viz", "pyincore-data"):
        try:
            out[pkg] = version(pkg)
        except PackageNotFoundError:
            out[pkg] = "not installed"
    return out


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument(
        "patterns",
        nargs="*",
        help="glob(s) on notebook ids, e.g. building_dmg.ipynb '*.zip/*'",
    )
    ap.add_argument(
        "--docs-root",
        default=os.environ.get("INCORE_DOCS_ROOT", ""),
        help="incore-docs checkout (or its notebooks/ folder); default $INCORE_DOCS_ROOT",
    )
    ap.add_argument(
        "--skip-file",
        type=Path,
        default=SKIP_FILE,
        help="per-notebook skip/timeout rules (default docs_notebooks_skip.yml next to this script)",
    )
    ap.add_argument("--list", action="store_true", help="list notebook ids and exit")
    ap.add_argument("--jobs", type=int, default=1, help="notebooks run in parallel (default 1)")
    ap.add_argument(
        "--timeout", type=int, default=1800, help="per-cell timeout in seconds (default 1800)"
    )
    ap.add_argument("--kernel", default="python3", help="kernel name (default python3)")
    ap.add_argument(
        "--run-skipped", action="store_true", help="also run notebooks marked skip in the skip file"
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("logs") / "docs_notebooks",
        help="parent folder for run output (default ./logs/docs_notebooks)",
    )
    ap.add_argument(
        "--no-auth-check", action="store_true", help="don't check the IN-CORE token first"
    )
    args = ap.parse_args()

    global NOTEBOOKS_DIR
    if not args.docs_root:
        ap.error("pass --docs-root /path/to/incore-docs or set INCORE_DOCS_ROOT")
    root = Path(args.docs_root).expanduser().resolve()
    NOTEBOOKS_DIR = root / "notebooks" if (root / "notebooks").is_dir() else root
    if not any(NOTEBOOKS_DIR.glob("*.ipynb")):
        ap.error(f"no notebooks found in {NOTEBOOKS_DIR}")

    rules = load_rules(args.skip_file)
    if args.list:
        selected, skipped = select(list_ids(), args.patterns, rules, args.run_skipped)
        for nb_id, rule in selected:
            extra = f"  (timeout {rule['timeout']}s)" if rule.get("timeout") else ""
            print(f"run   {nb_id}{extra}")
        for nb_id, reason in skipped:
            print(f"skip  {nb_id}  -- {reason}")
        print(f"\n{len(selected)} to run, {len(skipped)} skipped")
        return 0

    if not args.no_auth_check:
        ensure_token()

    started = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = (args.out / started).resolve()
    work_dir = run_dir / "work"
    exec_dir = run_dir / "executed"
    found = stage(work_dir)
    selected, skipped = select(list(found), args.patterns, rules, args.run_skipped)
    if not selected:
        print("Nothing matched.")
        return 1

    meta = {
        "started": started,
        "python": sys.executable,
        "notebooks": str(NOTEBOOKS_DIR),
        "versions": package_versions(),
        "timeout": args.timeout,
    }
    print(f"Running {len(selected)} notebooks ({len(skipped)} skipped) -> {run_dir}")
    print("  " + ", ".join(f"{k} {v}" for k, v in meta["versions"].items()))

    results = []
    with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = {}
        for nb_id, rule in selected:
            out_path = exec_dir / nb_id.replace(".zip/", ZIP_SUFFIX + "/")
            fut = pool.submit(
                execute,
                nb_id,
                str(found[nb_id]),
                out_path,
                int(rule.get("timeout", args.timeout)),
                args.kernel,
            )
            futures[fut] = nb_id
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                r = fut.result()
            except Exception as e:  # worker crashed
                r = {
                    "id": futures[fut],
                    "status": "error",
                    "seconds": 0,
                    "error": {"ename": type(e).__name__, "evalue": str(e)[:500]},
                    "executed": "",
                }
            results.append(r)
            msg = ""
            if r["error"]:
                msg = f"  {r['error'].get('ename', '')}: {(r['error'].get('evalue') or '')[:120]}"
            print(f"[{i}/{len(selected)}] {r['status']:<7} {r['seconds']:>6.0f}s  {r['id']}{msg}")
            write_report(run_dir, results, skipped, meta)  # keep report current

    write_report(run_dir, results, skipped, meta)
    failed = [r for r in results if r["status"] != "pass"]
    print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed. Report: {run_dir / 'report.md'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
