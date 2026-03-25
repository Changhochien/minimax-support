#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# minimax-support installer
#
# One-liner (no clone required):
#   curl -sL https://raw.githubusercontent.com/Changhochien/minimax-support/main/install.sh | bash -s -- --key YOUR_KEY
#
# Or clone first:
#   gh repo clone Changhochien/minimax-support && cd minimax-support
#   ./install.sh --key YOUR_KEY
#
# Options:
#   --key <KEY>        MiniMax API key (required)
#   --host global|cn   API region (default: global)
# ──────────────────────────────────────────────────────────────────────────────

set -e

echo "=== minimax-support installer ==="
echo ""

# Detect curl|bash invocation — clone to temp dir
if [[ ! -d "${BASH_SOURCE[0]%/*}/src" ]] && [[ "${BASH_SOURCE[0]}" == /* ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [[ ! -d "$(dirname "$0")/src" ]]; then
    echo "(Cloning repo to temp dir...)"
    TMPDIR=$(mktemp -d)
    git clone --depth 1 https://github.com/Changhochien/minimax-support "$TMPDIR"
    SCRIPT_DIR="$TMPDIR"
elif [[ "${BASH_SOURCE[0]}" == /* ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR="$(pwd)"
fi

# ── Check uv ─────────────────────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo "Error: uv is required. Install: https://github.com/astral-sh/uv"
    exit 1
fi

# ── Parse args ────────────────────────────────────────────────────────────────
API_KEY=""
HOST="global"
while [[ $# -gt 0 ]]; do
    case $1 in
        --key)        API_KEY="$2"; shift 2 ;;
        --key=*)      API_KEY="${1#*=}"; shift ;;
        --host)       HOST="$2"; shift 2 ;;
        --host=*)     HOST="${1#*=}"; shift ;;
        *)            echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ -z "$API_KEY" ]]; then
    echo "Error: --key is required"
    echo "Usage: $0 --key YOUR_KEY [--host global|cn]"
    exit 1
fi

if [[ "$HOST" != "global" ]] && [[ "$HOST" != "cn" ]]; then
    echo "Error: --host must be 'global' or 'cn'"
    exit 1
fi

# ── Install CLI ───────────────────────────────────────────────────────────────
echo "Installing minimax-support CLI..."
cd "$SCRIPT_DIR"
uv tool install --from . minimax-support

# ── Save credentials ──────────────────────────────────────────────────────────
CONFIG_DIR="$HOME/.config/minimax-support"
mkdir -p "$CONFIG_DIR"

if [[ "$HOST" == "cn" ]]; then
    API_HOST="https://api.minimaxi.com"
else
    API_HOST="https://api.minimax.io"
fi

cat > "$CONFIG_DIR/creds.toml" <<EOF
MINIMAX_API_KEY=$API_KEY
MINIMAX_API_HOST=$API_HOST
EOF

echo "Credentials saved to $CONFIG_DIR/creds.toml"

# ── Add to shell profile ──────────────────────────────────────────────────────
SHELL_RC=""
if [[ -n "$ZSH_VERSION" ]] && [[ -f "$HOME/.zshrc" ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ -f "$HOME/.bashrc" ]]; then
    SHELL_RC="$HOME/.bashrc"
elif [[ -f "$HOME/.bash_profile" ]]; then
    SHELL_RC="$HOME/.bash_profile"
fi

if [[ -n "$SHELL_RC" ]]; then
    if ! grep -q "MINIMAX_API_KEY" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# MiniMax Token Plan credentials" >> "$SHELL_RC"
        echo "export MINIMAX_API_KEY=\"$API_KEY\"" >> "$SHELL_RC"
        echo "export MINIMAX_API_HOST=\"$API_HOST\"" >> "$SHELL_RC"
        echo "Added credentials to $SHELL_RC"
    fi
fi

echo ""
echo "Done! Run:"
echo "  minimax-support search \"your query\""
echo "  minimax-support understand ./photo.jpg --prompt \"Describe this\""
