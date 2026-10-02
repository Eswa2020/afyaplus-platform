"""The release manifest must describe what is actually in the repo and the pipeline."""
import json
import re
from pathlib import Path

import yaml

REL = yaml.safe_load(Path("release.yaml").read_text(encoding="utf-8"))
PIN = json.loads(Path("prompts/pin.json").read_text(encoding="utf-8"))
MCP_SRC = Path("logistics_mcp_versioned.py").read_text(encoding="utf-8")
CI = yaml.safe_load(Path("../.github/workflows/ci.yml").read_text(encoding="utf-8"))


def test_release_tags_align():
    v = REL["release"]
    assert REL["git_tag"] == f"v{v}"
    assert REL["image"].endswith(f":{v}")


def test_release_prompt_matches_pin():
    assert REL["components"]["prompt"]["version"] == PIN["prompt_version"]
    assert REL["components"]["prompt"]["sha256"] == PIN["prompt_sha256"]


def test_release_mcp_version_matches_server():
    m = re.search(r'^MCP_VERSION = "([^"]+)"', MCP_SRC, re.MULTILINE)
    assert m, "MCP_VERSION constant not found"
    assert REL["components"]["mcp_server"]["version"] == m.group(1)


def test_deploy_job_builds_the_release_version():
    assert CI["jobs"]["deploy-staging"]["env"]["RELEASE_VERSION"] == REL["release"]
