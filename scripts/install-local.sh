#!/bin/bash
# Install this checkout for the current user.
# Pass --restart to restart a running Guake afterwards (closes all its shells).

set -euo pipefail

RESTART=0
for arg in "$@"; do
    case "$arg" in
    --restart) RESTART=1 ;;
    *)
        echo "usage: $0 [--restart]" >&2
        exit 1
        ;;
    esac
done

PYTHON=${PYTHON:-python3}
cd "$(dirname "$0")/.."

pip_args=(install --user --upgrade .)
if "$PYTHON" -c 'import os, sys, sysconfig; sys.exit(not os.path.exists(os.path.join(sysconfig.get_path("stdlib"), "EXTERNALLY-MANAGED")))'; then
    pip_args+=(--break-system-packages)
fi
"$PYTHON" -m pip "${pip_args[@]}"

# Look the package up from outside the repo so the installed copy is found, not ./guake.
data_dir=$(cd / && "$PYTHON" -c 'import importlib.util, os; print(os.path.join(importlib.util.find_spec("guake").submodule_search_locations[0], "data"))')
glib-compile-schemas --strict "$data_dir"
echo "Compiled schemas in $data_dir"

guake_bin="$("$PYTHON" -m site --user-base)/bin/guake"

mapfile -t guake_pids < <(pgrep -u "$(id -u)" -f "$guake_bin" || true)

if [ "${#guake_pids[@]}" = 0 ]; then
    echo "Guake is not running, start it with: $guake_bin"
elif [ "$RESTART" = 1 ]; then
    # Detached so the restart survives when this script runs inside Guake itself.
    # shellcheck disable=SC2016
    setsid -f sh -c 'bin=$1; shift; "$bin" --quit; while kill -0 "$@" 2>/dev/null; do sleep 0.2; done; exec "$bin"' \
        sh "$guake_bin" "${guake_pids[@]}" </dev/null >/dev/null 2>&1
    echo "Restarting Guake"
else
    echo "Installed. Restart Guake to use it: $guake_bin --quit && $guake_bin &"
fi
