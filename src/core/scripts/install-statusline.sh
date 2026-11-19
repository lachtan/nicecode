#!/usr/bin/env bash

# Copies statusline.sh/.py/.ps1 into the target's .claude/scripts directory and wires
# the "statusLine" key in its settings.json. Mirrors install-rules.py's --scope /
# managed-by / version conventions, but tracks one version across the whole
# statusline.sh/.py/.ps1 bundle instead of per file.
set -euo pipefail

MANAGED_BY="https://github.com/lachtan/nicecode"
STATUSLINE_SUBDIR=".claude/scripts/plugins/nicecode/core"

usage() {
    echo "Usage: $0 [project_dir] --scope {project|user}" >&2
    exit 1
}

resolve_base_dir() {
    local scope="$1" project_dir="$2"
    if [[ "$scope" == "user" ]]; then
        echo "$HOME"
    elif [[ -n "$project_dir" ]]; then
        (cd "$project_dir" && pwd)
    else
        pwd
    fi
}

frontmatter_value() {
    local file="$1" key="$2"
    [[ -f "$file" ]] || return 0
    sed -n "s/^# ${key}: //p" "$file" | head -n1
}

install_statusline_files() {
    local script_dir="$1" target_dir="$2"
    local source_version target_managed_by target_version

    [[ -L "$target_dir" ]] && rm "$target_dir"

    source_version="$(frontmatter_value "$script_dir/statusline.sh" version)"

    if [[ ! -f "$target_dir/statusline.sh" ]]; then
        mkdir -p "$target_dir"
        cp -p "$script_dir/statusline.sh" "$script_dir/statusline.py" "$script_dir/statusline.ps1" "$target_dir/"
        echo "installed statusline (${source_version})"
        return
    fi

    target_managed_by="$(frontmatter_value "$target_dir/statusline.sh" managed-by)"
    if [[ "$target_managed_by" != "$MANAGED_BY" ]]; then
        echo "skipped statusline: not managed by this repo, not overwriting"
        return
    fi

    target_version="$(frontmatter_value "$target_dir/statusline.sh" version)"
    if [[ "$target_version" != "$source_version" ]]; then
        cp -p "$script_dir/statusline.sh" "$script_dir/statusline.py" "$script_dir/statusline.ps1" "$target_dir/"
        echo "updated statusline: ${target_version} -> ${source_version}"
        return
    fi

    echo "up to date statusline (${target_version})"
}

configure_status_line() {
    local settings_file="$1" desired_command="$2"
    local existing_command tmp_file

    mkdir -p "$(dirname "$settings_file")"
    [[ -f "$settings_file" ]] || echo "{}" > "$settings_file"

    existing_command="$(jq -r '.statusLine.command // ""' "$settings_file")"

    if [[ -n "$existing_command" && "$existing_command" != *"nicecode/core/statusline.sh" ]]; then
        echo "skipped statusLine: already set to '${existing_command}', not overwriting"
        return
    fi

    tmp_file="$(mktemp)"
    jq --arg cmd "$desired_command" '.statusLine = {"type": "command", "command": $cmd}' "$settings_file" > "$tmp_file"
    mv "$tmp_file" "$settings_file"

    if [[ -z "$existing_command" ]]; then
        echo "configured statusLine in ${settings_file}"
    else
        echo "up to date statusLine in ${settings_file}"
    fi
}

main() {
    local scope="" project_dir=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --scope)
                scope="${2:?--scope requires a value}"
                shift 2
                ;;
            -*)
                usage
                ;;
            *)
                [[ -z "$project_dir" ]] || usage
                project_dir="$1"
                shift
                ;;
        esac
    done
    [[ "$scope" == "project" || "$scope" == "user" ]] || usage

    local script_dir base_dir target_dir settings_file desired_command
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    base_dir="$(resolve_base_dir "$scope" "$project_dir")"
    target_dir="$base_dir/$STATUSLINE_SUBDIR"
    settings_file="$base_dir/.claude/settings.json"

    if [[ "$scope" == "user" ]]; then
        desired_command="$target_dir/statusline.sh"
    else
        desired_command="$STATUSLINE_SUBDIR/statusline.sh"
    fi

    install_statusline_files "$script_dir" "$target_dir"
    configure_status_line "$settings_file" "$desired_command"
}

main "$@"
