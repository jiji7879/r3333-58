#!/usr/bin/env bash
# Rebuild every CNF used in this report, deterministically.
# Run from .ultramath/smwrmwgf7/m10/ with ../../../ as the repository root.
set -euo pipefail
cd "$(dirname "$0")"
T=../../../artifacts/k15_link_Tminus_m5.col
K=../../../.scratch/satcheck/bin/kissat
mkdir -p cnf log wit

# word extension of the colour-0 design (needs log/design.blocks from make_design.sh)
python3 enc.py --out cnf/plain.cnf          --template $T --drop S,S2
python3 enc.py --out cnf/plain_k41.cnf      --template ../../../artifacts/k15_template_Tminus_aut2_m4.col --drop S,S2
python3 enc.py --out cnf/sixth.cnf          --template $T --drop S2
python3 enc.py --out cnf/sixth2.cnf         --template $T
python3 enc.py --out cnf/sixth_pin.cnf      --template $T --pin ../../../.ultramath/smwr8io45/m6/wit/pair58_Tminus.wit
python3 enc.py --out cnf/design_pin.cnf     --template $T --pin-design log/design.blocks
python3 enc.py --out cnf/design_pin_no2.cnf --template $T --pin-design log/design.blocks --drop S2
python3 enc.py --out cnf/design_plain.cnf   --template $T --pin-design log/design.blocks --drop S,S2
python3 enc_triple.py --out cnf/t3v2.cnf    --template $T --map cnf/t3v2.map.json
python3 enc_triple.py --out cnf/t3v2_pin.cnf --template $T --pin wit/t3_words.wit
python3 enc_design.py --out cnf/design.cnf  --map cnf/design.map.json 2>/dev/null || \
  python3 -c "
import sys, json; sys.path.insert(0,'.')
from enc_design import build
e = build(); e.write('cnf/design.cnf')
json.dump({str(k): v for k, v in e.meta.items()}, open('cnf/design.map.json', 'w'))
print('design.cnf rebuilt with map')"
echo "all CNFs rebuilt"
