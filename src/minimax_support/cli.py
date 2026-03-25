#!/usr/bin/env python3
"""MiniMax Support CLI — web search and image understanding."""
from __future__ import annotations

import json
import sys
import typer
from typing import Annotated
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from minimax_support.client import (
    web_search,
    understand_image,
    MinimaxSupportError,
    MinimaxAPIError,
)

__version__ = "0.1.0"

app = typer.Typer(
    name="minimax-support",
    help="MiniMax Token Plan CLI — web search and image understanding.",
    add_completion=False,
)
console = Console()


def version_callback(version: bool):
    if version:
        console.print(f"minimax-support {__version__}")
        raise typer.Exit(0)


# ── Search ────────────────────────────────────────────────────────────────────

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output raw JSON"),
    related: bool = typer.Option(False, "--related", "-r", help="Show related searches"),
):
    """Perform a web search."""
    try:
        result = web_search(query)

        if json_output:
            console.print(json.dumps(result, indent=2, ensure_ascii=False))
            return

        organic = result.get("organic", [])
        if not organic:
            console.print("[yellow]No results found.[/yellow]")
            return

        table = Table(title=f"Search results for: {query}", show_header=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="cyan")
        table.add_column("URL")
        table.add_column("Snippet", style="white")

        for i, item in enumerate(organic, 1):
            title = item.get("title", "")
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            date = item.get("date", "")
            table.add_row(str(i), title, link, snippet)
            if date:
                console.print(f"  [dim]Date: {date}[/dim]")

        console.print(table)

        if related:
            related_list = result.get("related_searches", [])
            if related_list:
                queries = ", ".join(r.get("query", "") for r in related_list[:5])
                console.print(f"\n[dim]Related:[/dim] {queries}")

    except MinimaxAPIError as e:
        print(f"API error: {e}", file=sys.stderr)
        raise typer.Exit(1)
    except MinimaxSupportError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(1)


# ── Image Understanding ───────────────────────────────────────────────────────

@app.command()
def understand(
    image: str = typer.Argument(..., help="Image URL or local file path"),
    prompt: str = typer.Option(..., "--prompt", "-p", help="Question/prompt about the image"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output raw JSON"),
):
    """Analyze an image and get an AI description."""
    if not prompt:
        print("[red]--prompt/-p is required[/red]", file=sys.stderr)
        raise typer.Exit(1)

    try:
        result = understand_image(prompt, image)

        if json_output:
            console.print(json.dumps({"content": result}, indent=2))
        else:
            console.print(Panel(result, title="Image Analysis", border_style="cyan"))

    except MinimaxAPIError as e:
        print(f"[red]API error: {e}[/red]", file=sys.stderr)
        raise typer.Exit(1)
    except MinimaxSupportError as e:
        print(f"[red]Error: {e}[/red]", file=sys.stderr)
        raise typer.Exit(1)


# ── Main ───────────────────────────────────────────────────────────────────────

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", callback=version_callback),
):
    """MiniMax Support CLI — web search and image understanding."""
    if ctx.invoked_subcommand is None:
        console.print(f"[dim]minimax-support v{__version__}[/dim]")
        console.print("Use --help to see available commands.")
