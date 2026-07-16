#!/usr/bin/env python3
"""Render the configurable project showcase into the profile README."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "projects.json"
README_PATH = ROOT / "README.md"
START_MARKER = "<!-- PROJECTS:START -->"
END_MARKER = "<!-- PROJECTS:END -->"


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_card(project: dict[str, object], width: int) -> list[str]:
    emoji = escape(project.get("emoji", "📦"))
    name = escape(project["name"])
    url = escape(project["url"])
    description = escape(project.get("description", ""))
    tags = " ".join(
        f"<code>{escape(tag)}</code>" for tag in project.get("tags", [])
    )

    lines = [
        f'    <td width="{width}%" valign="top">',
        f'      <h3>{emoji} <a href="{url}">{name}</a></h3>',
    ]
    if description:
        lines.append(f"      <p>{description}</p>")
    if tags:
        lines.append(f"      <p>{tags}</p>")
    lines.extend(
        [
            f'      <a href="{url}">View repository →</a>',
            "    </td>",
        ]
    )
    return lines


def render(config: dict[str, object]) -> str:
    columns = int(config.get("columns", 2))
    if columns not in (1, 2, 3):
        raise ValueError("'columns' must be 1, 2, or 3")

    projects = config.get("projects", [])
    if not isinstance(projects, list):
        raise ValueError("'projects' must be a list")

    lines = [
        START_MARKER,
        "<!-- Edit projects.json, then run: python3 scripts/render_projects.py -->",
        "",
        f"## {escape(config.get('title', '🚀 Featured Projects'))}",
        "",
    ]

    if projects:
        width = 100 // columns
        lines.append("<table>")
        for index in range(0, len(projects), columns):
            lines.append("  <tr>")
            row = projects[index : index + columns]
            for project in row:
                if not isinstance(project, dict):
                    raise ValueError("Each project must be an object")
                renderable = project
                if "name" not in renderable or "url" not in renderable:
                    raise ValueError("Each project requires 'name' and 'url'")
                lines.extend(render_card(renderable, width))
            lines.append("  </tr>")
        lines.append("</table>")
    else:
        lines.append("_Projects coming soon._")

    all_projects_url = config.get("all_projects_url")
    if all_projects_url:
        link_text = escape(config.get("all_projects_text", "Explore all projects →"))
        lines.extend(
            [
                "",
                '<div align="right">',
                f'  <a href="{escape(all_projects_url)}">{link_text}</a>',
                "</div>",
            ]
        )

    lines.extend(["", END_MARKER])
    return "\n".join(lines)


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    readme = README_PATH.read_text(encoding="utf-8")

    try:
        before, remainder = readme.split(START_MARKER, 1)
        _, after = remainder.split(END_MARKER, 1)
    except ValueError as error:
        raise SystemExit("Project markers are missing or duplicated in README.md") from error

    output = before.rstrip() + "\n\n" + render(config) + "\n\n" + after.lstrip()
    README_PATH.write_text(output, encoding="utf-8")
    print("Updated README.md from projects.json")


if __name__ == "__main__":
    main()
