#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || exit 1
echo "=================================================="
echo "   INICIANDO SERVIDOR LOCAL AZAR DASHBOARDS"
echo "=================================================="
echo "Directorio: $DIR"
echo ""
python3 "$DIR/servidor_dashboard.py"
