# minimax-support

**Token-efficient web search and image understanding for MiniMax Token Plan users.**

Unlike the official MCP server which ships full tool schemas into every model context, this CLI wraps the same `/v1/coding_plan/search` and `/v1/coding_plan/vlm` endpoints directly. Your agent sees a skill description once — no MCP framing overhead per call.

## What's included

| Command | Description |
|---|---|
| `minimax-support search <query>` | Web search via MiniMax |
| `minimax-support understand <image> --prompt <text>` | Analyze an image (URL or local file) |

## Install

### One-liner (no clone required)

```bash
curl -sL https://raw.githubusercontent.com/Changhochien/minimax-support/main/install.sh | bash -s -- --key=YOUR_KEY
```

For Mainland China API:

```bash
curl -sL https://raw.githubusercontent.com/Changhochien/minimax-support/main/install.sh | bash -s -- --key=YOUR_KEY --host=cn
```

### Or clone and run

```bash
gh repo clone Changhochien/minimax-support && cd minimax-support
./install.sh --key YOUR_KEY
```

### Requirements

- **uv** — fast Python package manager  
  `curl -LsSf https://astral.sh/uv/install.sh | sh`  
  (or `brew install uv` on macOS)
- **MiniMax API key** from [platform.minimax.io](https://platform.minimax.io/subscribe/token-plan)

## Usage

```bash
# Web search
minimax-support search "Python asyncio tutorial"
minimax-support search "latest iPhone 2026" --related

# Image understanding
minimax-support understand ./photo.jpg --prompt "Describe this image"
minimax-support understand "https://example.com/chart.png" --prompt "What does this chart show?"

# Raw JSON output
minimax-support search "query" --json
minimax-support understand ./img.png --prompt "?" --json
```

## Credentials

The installer saves your API key to `~/.config/minimax-support/creds.toml`.

Or set environment variables manually:

```bash
export MINIMAX_API_KEY=your_key_here
export MINIMAX_API_HOST=https://api.minimax.io   # or https://api.minimaxi.com for CN
```

## OpenClaw Skill

Add this to your OpenClaw workspace to use it as a skill:

```markdown
# minimax-support skill

Use the `minimax-support` CLI for web search and image understanding.

## Commands

Web search:
: `minimax-support search "<query>"`

Image understanding:
: `minimax-support understand "<image>" --prompt "<question>"`
```

## Uninstall

```bash
uv tool uninstall minimax-support
rm -rf ~/.config/minimax-support
# Also remove MINIMAX_API_KEY / MINIMAX_API_HOST from your shell profile
```
