"""One prompt version, three places: they must agree, or CI goes red."""
import json
from pathlib import Path

import yaml

CONFIG = yaml.safe_load(Path("config/triage.yaml").read_text(encoding="utf-8"))
PIN = json.loads(Path("prompts/pin.json").read_text(encoding="utf-8"))
CI = yaml.safe_load(Path("../.github/workflows/ci.yml").read_text(encoding="utf-8"))


def test_config_matches_pin():
    assert CONFIG["prompt_version"] == PIN["prompt_version"]


def test_ci_eval_uses_pinned_version():
    eval_env = next(s["env"] for s in CI["jobs"]["eval"]["steps"] if s.get("name") == "Eval gate")
    assert eval_env["PROMPT_VERSION"] == PIN["prompt_version"]


def test_config_values_are_sane():
    assert isinstance(CONFIG["prompt_version"], str), "quote the version in YAML"
    assert Path(f"prompts/triage_system_v{CONFIG['prompt_version']}.txt").is_file()
    assert 0.0 <= CONFIG["temperature"] <= 1.0
    assert CONFIG["max_tokens"] > 0