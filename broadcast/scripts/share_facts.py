"""The facts drawn on each share card, shared by build_share_images.py (Pillow) and verify.py (stdlib)."""
from __future__ import annotations

import hashlib
import json


def card_facts(team, program):
    if program == "FRC":
        return {"name": team["name"], "number": team["number"], "program": "FRC", "school": team["school"], "city": team["city"],
                "stats": [(f"{team['record']['wins']}-{team['record']['losses']}", "2026 record"), (f"#{team['district']['rank']}", "Indiana district rank"),
                          (str(team["district"]["points"]), "district points")],
                "honors": team["badges"][:3]}
    stats = [(f"{team['opr']:.1f}", "best OPR 2025–26"), (f"{team['regionalRank']}/{team['regionalCount']}", "rank at Indiana events")] if "opr" in team else []
    return {"name": team["name"], "number": team["number"], "program": "FTC", "school": team.get("school", ""), "city": team.get("city", ""),
            "stats": stats, "honors": [] if stats else ["New team for 2026–27"]}


def fingerprint(facts):
    return hashlib.sha256(json.dumps(facts, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def home_facts(data):
    s = data["seasonSummary"]
    return {"teams": s["teams"], "titles": s["eventTitles"], "worlds": len(s["worldsTeams"])}
