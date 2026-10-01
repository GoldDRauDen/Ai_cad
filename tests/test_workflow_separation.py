"""Production CAD and MCP research workflows must stay separated."""
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
CAD_WF=ROOT/".github/workflows/dxf-export-tests.yml"
MCP_WF=ROOT/".github/workflows/mcp-research.yml"

def test_cad_workflow_excludes_mcp():
    text=CAD_WF.read_text(encoding="utf-8")
    data=yaml.safe_load(text)
    assert "services/trainaicad-mcp/**" not in text
    assert "MCP Inspector" not in text
    assert "mcp" not in data.get("jobs", {})
    assert set(data.get("jobs", {})) == {"serializer"}

def test_mcp_research_workflow_isolated():
    text=MCP_WF.read_text(encoding="utf-8")
    data=yaml.safe_load(text)
    assert "services/trainaicad-mcp/**" in text
    assert "MCP Inspector e2e" in text
    assert "mcp-research" in data.get("jobs", {})
    assert "serializer" not in data.get("jobs", {})

def test_entrypoint_declares_repo_direct_default():
    entry=(ROOT/"AI_ENTRYPOINT.md").read_text(encoding="utf-8")
    assert "MCP is research-only and is NOT part of the production CAD pipeline" in entry
    assert "Default CAD behavior remains repo-direct" in entry
    assert "Do not route through MCP" in entry
