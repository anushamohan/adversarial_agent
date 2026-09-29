import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cotabreak.agentdojo_qwen import normalize_quantization_config


class QuantizationConfigTest(unittest.TestCase):
    def test_accepts_registered_nf4_configuration(self) -> None:
        config = {
            "load_in_4bit": True,
            "bnb_4bit_quant_type": "nf4",
            "bnb_4bit_use_double_quant": True,
            "bnb_4bit_compute_dtype": "bfloat16",
        }
        self.assertEqual(normalize_quantization_config(config), config)

    def test_preserves_unquantized_legacy_runs(self) -> None:
        self.assertIsNone(normalize_quantization_config(None))

    def test_rejects_unregistered_quantization(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported quantization"):
            normalize_quantization_config({"load_in_8bit": True})


if __name__ == "__main__":
    unittest.main()
