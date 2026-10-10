#!/usr/bin/env bash
set -euo pipefail

readonly MAIN="z-main"
readonly TEX_BIN_DIR="/Library/TeX/texbin"
readonly BIBER_SYSTEM="${TEX_BIN_DIR}/biber"
readonly BIBER_ARM64="${HOME}/.local/bin/biber-arm64"

export PATH="${TEX_BIN_DIR}:${PATH}"
cd "$(dirname "$0")"

die() {
    echo "ERROR: $*" >&2
    exit 1
}

ensure_biber_arm64() {
    [[ -x "$BIBER_ARM64" ]] && return
    mkdir -p "$(dirname "$BIBER_ARM64")"
    lipo "$BIBER_SYSTEM" -thin arm64 -output "$BIBER_ARM64" \
        || die "no se pudo extraer la rebanada arm64 de biber desde ${BIBER_SYSTEM}"
    chmod +x "$BIBER_ARM64"
}

run_step() {
    local label="$1"
    shift
    local log
    log="$(mktemp)"
    if ! "$@" >"$log" 2>&1; then
        tail -n 40 "$log" >&2
        die "fallo en el paso '${label}' (salida completa en ${log})"
    fi
    rm -f "$log"
}

compile_document() {
    run_step "pdflatex 1" pdflatex -interaction=nonstopmode "${MAIN}.tex"
    run_step "biber" "$BIBER_ARM64" "$MAIN"
    run_step "pdflatex 2" pdflatex -interaction=nonstopmode "${MAIN}.tex"
    run_step "pdflatex 3" pdflatex -interaction=nonstopmode "${MAIN}.tex"
}

print_summary() {
    local pages undefined_lines unresolved_citations text
    text="$(pdftotext "${MAIN}.pdf" -)"
    pages="$(pdfinfo "${MAIN}.pdf" | awk '/^Pages:/ {print $2}')"
    undefined_lines="$(grep -ci "undefined" "${MAIN}.log" || true)"
    unresolved_citations="$(grep -cF "[?]" <<<"$text" || true)"
    echo "Páginas: ${pages}"
    echo "Líneas con 'undefined' en ${MAIN}.log: ${undefined_lines}"
    echo "Ocurrencias de '[?]' en el texto extraído: ${unresolved_citations}"
}

ensure_biber_arm64
compile_document
print_summary
