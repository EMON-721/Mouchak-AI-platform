"""Prove opt-out is established before ONNX Runtime can initialize."""

import os, subprocess, sys


def test_package_disables_runtime_telemetry_before_model_import():
    script = """
import os,sys
os.environ['ORT_DISABLE_TELEMETRY']='0'
os.environ['HF_HUB_DISABLE_TELEMETRY']='0'
import services.model_worker
assert os.environ['ORT_DISABLE_TELEMETRY']=='1'
assert os.environ['HF_HUB_DISABLE_TELEMETRY']=='1'
assert 'onnxruntime' not in sys.modules
assert 'huggingface_hub' not in sys.modules
print('pre-import privacy configuration verified')
"""
    r = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    )
    assert "pre-import privacy configuration verified" in r.stdout
