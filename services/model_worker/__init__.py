"""Private inference must opt out before any model runtime initializes."""

import os

# The full ONNX opt-out is required before import: the later Python API alone
# can allow an initialization event. No user consent for telemetry is assumed.
os.environ["ORT_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
