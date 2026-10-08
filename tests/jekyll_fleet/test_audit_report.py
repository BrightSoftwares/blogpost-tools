import json

import fleet_helpers  # noqa: F401  (puts scripts/jekyll_fleet on sys.path)
import audit_report as ar


def ba(*items):
    return json.dumps({"results": [
        {"type": "unpatched_gem", "gem": {"name": n, "version": "1.0"},
         "advisory": {"id": i, "criticality": c, "title": "t", "url": "https://u"}} for n, i, c in items]})


def test_parse_bundle_audit_unknown_severity_mapped():
    f = ar.parse_bundle_audit(ba(("a", "CVE-1", None), ("b", "CVE-2", "high")), unknown_as="medium")
    assert [x["severity"] for x in f] == ["medium", "high"]


def test_evaluate_threshold():
    f = ar.parse_bundle_audit(ba(("a", "CVE-1", "medium")))
    assert not ar.evaluate(f, "high")
    assert ar.evaluate(f, "medium")
    assert not ar.evaluate(f, "none")
    assert not ar.evaluate([], "low")


def test_pipfile_to_requirements_pins_only():
    lock = json.dumps({"default": {"requests": {"version": "==2.31.0"}, "vcs": {"git": "x"}},
                       "develop": {"pytest": {"version": "==8.0.0"}}})
    assert ar.pipfile_lock_to_requirements(lock) == "requests==2.31.0\npytest==8.0.0\n"
    assert ar.pipfile_lock_to_requirements(lock, include_dev=False) == "requests==2.31.0\n"


def test_parse_pip_audit_assigns_configured_severity():
    out = json.dumps({"dependencies": [{"name": "x", "version": "1", "vulns": [{"id": "PYSEC-1", "aliases": ["CVE-9"]}]},
                                       {"name": "y", "version": "2", "vulns": []}]})
    f = ar.parse_pip_audit(out, severity="critical")
    assert len(f) == 1 and f[0]["severity"] == "critical" and f[0]["title"] == "CVE-9"


def test_cli_exit_codes_and_step_summary(tmp_path, monkeypatch, capsys):
    p = tmp_path / "ba.json"
    p.write_text(ba(("a", "CVE-1", "high")))
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    assert ar.main(["bundler", "--input", str(p), "--fail-on", "high"]) == 1
    assert "FAIL" in summary.read_text()
    assert ar.main(["bundler", "--input", str(p), "--fail-on", "critical"]) == 0
    p.write_text(ba())
    assert ar.main(["bundler", "--input", str(p)]) == 0


def test_dedupe_collapses_repeated_advisories():
    f = ar.parse_bundle_audit(ba(("a", "CVE-1", "high"), ("a", "CVE-1", "high"), ("a", "CVE-2", "high")))
    assert len(ar.dedupe(f)) == 2


def test_unpinned_entries_warn(capsys):
    lock = json.dumps({"default": {"vcs": {"git": "x"}}})
    assert ar.pipfile_lock_to_requirements(lock) == ""
    assert "vcs not audited" in capsys.readouterr().err
