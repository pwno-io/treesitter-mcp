from typing import List, Any
import json
import os
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_MODULE = "treesitter_mcp.cli.ts_cli"
TEST_FILE = REPO_ROOT / "test_files" / "test.py"


def _run_cli(args: List[str]) -> subprocess.CompletedProcess[str]:
    """Run ts-cli in a subprocess.

    Args:
        args: CLI arguments to pass.

    Returns:
        Completed subprocess result.
    """
    env = os.environ.copy()
    python_path = str(REPO_ROOT / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{python_path}{os.pathsep}{existing}" if existing else python_path
    )

    executable = sys.executable
    if ".venv" not in executable and os.path.exists(
        REPO_ROOT / ".venv" / "bin" / "python"
    ):
        executable = str(REPO_ROOT / ".venv" / "bin" / "python")

    return subprocess.run(
        [executable, "-m", CLI_MODULE, *args],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _load_json(result: subprocess.CompletedProcess[str]) -> Any:
    """Parse JSON from CLI output.

    Args:
        result: Completed subprocess result.

    Returns:
        Parsed JSON payload.
    """
    return json.loads(result.stdout)


def test_ts_cli_default_analysis() -> None:
    """Runs default analysis for a Python file.

    Args:
        None.

    Returns:
        None.
    """
    result = _run_cli([str(TEST_FILE)])

    assert result.returncode == 0, result.stderr
    payload = _load_json(result)

    assert payload["language"] == "python"
    assert payload["file_path"] == str(TEST_FILE.resolve())
    symbol_names = {symbol["name"] for symbol in payload["symbols"]}
    assert "factorial" in symbol_names


def test_ts_cli_ast_max_depth() -> None:
    """Limits AST depth for the AST output.

    Args:
        None.

    Returns:
        None.
    """
    result = _run_cli([str(TEST_FILE), "--ast", "--max-depth", "1"])

    assert result.returncode == 0, result.stderr
    payload = _load_json(result)

    assert payload["type"] == "module"
    assert "children" in payload


def test_ts_cli_find_function_include_source() -> None:
    """Finds a function and includes its source.

    Args:
        None.

    Returns:
        None.
    """
    result = _run_cli(
        [str(TEST_FILE), "--find-function", "factorial", "--include-source"]
    )

    assert result.returncode == 0, result.stderr
    payload = _load_json(result)

    match = next(
        (item for item in payload["matches"] if item["name"] == "factorial"), None
    )
    assert match is not None
    assert "def factorial" in match["source"]


def test_ts_cli_supported_languages() -> None:
    """Lists supported languages.

    Args:
        None.

    Returns:
        None.
    """
    result = _run_cli(["--supported-languages"])

    assert result.returncode == 0, result.stderr
    payload = _load_json(result)

    assert "python" in payload


def test_ts_cli_output_file(tmp_path: Path) -> None:
    """Writes results to an output file.

    Args:
        tmp_path: Temporary directory fixture.

    Returns:
        None.
    """
    output_path = tmp_path / "ast.json"
    result = _run_cli([str(TEST_FILE), "--ast", "--output-file", str(output_path)])

    assert result.returncode == 0, result.stderr
    payload = _load_json(result)

    assert payload["status"] == "written"
    assert output_path.exists()
    output_payload = json.loads(output_path.read_text())
    assert output_payload["type"] == "module"
