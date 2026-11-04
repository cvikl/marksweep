#!/usr/bin/env bash
# Run the four demo photos through the live pipeline and record each as a replayable fixture.
set -euo pipefail
cd "$(dirname "$0")/.."
for d in lego-shop lv-stall lv-seizure lv-control; do
  client=$(python3 -c "import json;print(json.load(open('fixtures/demos/$d/demo.json'))['client'])")
  goods=$(python3 -c "import json;print(json.load(open('fixtures/demos/$d/demo.json'))['goods'])")
  juris=$(python3 -c "import json;print(json.load(open('fixtures/demos/$d/demo.json'))['jurisdictions'])")
  notes=$(python3 -c "import json;print(json.load(open('fixtures/demos/$d/demo.json'))['notes'])")
  echo "=== $d ($client)"
  env -u PYTHONPATH .venv/bin/marksweep sweep "fixtures/demos/$d/photo.jpg" --client "$client" --goods "$goods" --jurisdictions "$juris" --notes "$notes" --save-fixture "$d"
done
