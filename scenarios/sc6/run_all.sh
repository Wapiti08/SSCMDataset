#!/usr/bin/env bash
# run_all.sh — Orchestrate all test stages sequentially.
# Corrected order based on user request:
#   1) start_vweb
#   2) collect_leak
#   3) malicious_build
#   4) package_artifact
#   5) publish
#   6) downstream
#
set -Eeuo pipefail

# Load .env if present
if [[ -f ".env" ]]; then
  set -a
  source .env
  set +a
fi

# always run from repo root
cd "$(dirname "$0")"

mkdir -p logs

log() { printf "[%s] %s\n" "$(date +"%Y-%m-%d %H:%M:%S")" "$*"; }
die() { log "ERROR: $*"; exit 1; }

FROM_STAGE=""
TO_STAGE=""
DRY_RUN="${DRY_RUN:-0}"
SKIP_FAIL="${SKIP_FAIL:-0}"
LIST_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in 
    --list) LIST_ONLY=1; shift ;;
    --from) FROM_STAGE="$2"; shift 2 ;;
    --to) TO_STAGE="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) die "Unknown arg: $1" ;;
  esac
done

# -------- stage definitions --------
STAGES=(
  "start_vweb|sh|scripts/start_vweb.sh|Start the vweb service"
  "collect_leak|sh|scripts/collect_leak_from_vweb.sh|Collect possible leak from vweb"
  "malicious_build|py|scripts/malicious_build.py|Run malicious_build.py (if present)"
  "package_artifact|sh|scripts/package_artifact.sh|Package the build artifact"
  "publish|sh|scripts/publish_to_repo.sh|Publish package to repository"
  "downstream|sh|scripts/downstream_consume.sh|Downstream consumption test"
)


list_stages() {
  printf "Stages (in order):\\n"
  for s in "${STAGES[@]}"; do
    IFS='|' read -r name typ path desc <<<"$s"
    printf "  - %-16s : %s [%s]\\n" "$name" "$desc" "$path"
  done
}

stage_index() {
  local target="$1"; local idx=0
  for s in "${STAGES[@]}"; do
    IFS='|' read -r name typ path desc <<<"$s"
    if [[ "$name" == "$target" ]]; then echo "$idx"; return 0; fi
    ((idx++))
  done
  echo "-1"
}

START_IDX=0
END_IDX=$((${#STAGES[@]} - 1))

if [[ -n "$FROM_STAGE" ]]; then
  idx=$(stage_index "$FROM_STAGE")
  [[ "$idx" -ge 0 ]] || die "Unknown --from stage '$FROM_STAGE'"
  START_IDX="$idx"
fi
if [[ -n "$TO_STAGE" ]]; then
  idx=$(stage_index "$TO_STAGE")
  [[ "$idx" -ge 0 ]] || die "Unknown --to stage '$TO_STAGE'"
  END_IDX="$idx"
fi
(( START_IDX <= END_IDX )) || die "--from comes after --to"


ensure_exec() {
  local f="$1"
  if [[ -f "$f" && ! -x "$f" ]]; then
    chmod +x "$f" || return 1
  fi
}

run_stage() {
  local name="$1" typ="$2" path="$3" desc="$4"
  log "==> Stage '$name' — $desc"

  if [[ ! -f "$path" ]]; then
    log "SKIP '$name' — missing $path"
    return 0
  fi

  local cmd=""
  case "$typ" in
    sh) ensure_exec "$path"; cmd="./$path" ;;
    py) cmd="python3 $path" ;;
    *) die "Unknown type '$typ' for $name" ;;
  esac

  log "Running: $cmd"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "DRY-RUN: not executing '$name'."
    return 0
  fi

  if bash -lc "$cmd"; then
    log "OK  '$name'"
  else
    rc=$?
    log "FAIL '$name' (exit $rc)"
    if [[ "$SKIP_FAIL" -eq 1 ]]; then
      log "Continuing because SKIP_FAIL=1"
      return 0
    else
      return "$rc"
    fi
  fi
}

log "Starting pipeline (from $(($START_IDX+1)) to $(($END_IDX+1))) — DRY_RUN=$DRY_RUN SKIP_FAIL=$SKIP_FAIL"
i=0
for entry in "${STAGES[@]}"; do
  if (( i < START_IDX || i > END_IDX )); then ((i++)); continue; fi
  IFS='|' read -r name typ path desc <<<"$entry"
  if ! run_stage "$name" "$typ" "$path" "$desc"; then
    die "Stopping pipeline due to failure in stage '$name'."
  fi
  ((i++))
done
log "Pipeline finished."