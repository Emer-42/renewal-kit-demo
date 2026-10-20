#!/usr/bin/env bash
# PreToolUse guard: accounts/ is source data. Blocks Edit/Write inside accounts/
# and Bash commands that would change something there. Reads stay allowed.
# Exit 2 = block (stderr goes back to Claude). Exit 0 = allow.
set -u

MSG="accounts/ is source data. Write to briefs/ instead."

if ! command -v jq >/dev/null 2>&1; then
  echo "guard-accounts: jq is required (brew install jq). Blocking to fail closed." >&2
  exit 2
fi

input=$(cat)
tool=$(printf '%s' "$input" | jq -r '.tool_name // empty')
root="${CLAUDE_PROJECT_DIR:-$PWD}"

block() { echo "$MSG" >&2; exit 2; }

case "$tool" in
  Edit|Write|MultiEdit|NotebookEdit)
    path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty')
    [ -z "$path" ] && exit 0
    rel="${path#"$root"/}"
    case "$rel" in
      accounts/*) block ;;
    esac
    case "$path" in
      */accounts/*) block ;;
    esac
    exit 0
    ;;
  Bash)
    cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')
    [ -z "$cmd" ] && exit 0
    # Only commands that mention accounts can change accounts.
    printf '%s' "$cmd" | grep -Eq '(^|[^A-Za-z0-9_./-])accounts(/|$|[^A-Za-z0-9_-])' || exit 0

    # Redirect, tee, dd, rsync, install or ln with an accounts/ target.
    printf '%s' "$cmd" | grep -Eq '>>?[[:space:]]*["'"'"']?[^[:space:];|&]*accounts' && block
    printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])(tee|dd|rsync|install|ln)([[:space:]]|$)[^;|&]*accounts' && block
    # In-place editors.
    printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])sed([[:space:]]+-[A-Za-z]*)*[[:space:]]+-[A-Za-z]*i' && block
    printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])perl[[:space:]]+-[A-Za-z]*[ip]' && block
    printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])(gawk|awk)[[:space:]].*-i[[:space:]]*inplace' && block
    printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])(ed|ex|vim?|nano)([[:space:]]|$)' && block
    # Destructive or moving commands anywhere near accounts.
    printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])(rm|rmdir|mv|truncate|shred|unlink|touch|mkdir|chmod|chown|patch)([[:space:]]|$)' && block
    printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])(xargs|find)[[:space:]].*(rm|mv|-delete|-exec)' && block
    # cp whose last argument is under accounts/.
    printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])cp([[:space:]]+[^;|&[:space:]]+)*[[:space:]]+[^;|&[:space:]]*accounts[^;|&[:space:]]*[[:space:]]*($|[;|&])' && block
    # git commands that rewrite the working tree.
    printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])git[[:space:]]+(checkout|restore|stash|apply|rm|mv|clean|reset)([[:space:]]|$)' && block
    # Scripted writes (python/node/ruby one-liners or heredocs).
    printf '%s' "$cmd" | grep -Eq "open\([^)]*['\"][waxr]*[wax+][waxrbt+]*['\"]" && block
    printf '%s' "$cmd" | grep -Eq 'write_text|write_bytes|writeFile|writelines|shutil\.(copy|move|rmtree)|os\.(remove|rename|replace|unlink|truncate)|\.unlink\(|\.rename\(|\.replace_?\(|File\.(write|open|delete)' && block
    exit 0
    ;;
esac
exit 0
