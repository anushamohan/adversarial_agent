import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cotabreak.tool_calling import parse_tool_call


class ToolCallingTest(unittest.TestCase):
    def test_parses_one_valid_call(self) -> None:
        parsed = parse_tool_call(
            'Reasoning <function=send_email>{"to": "a@example.com"}</function>'
        )
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.function, "send_email")
        self.assertEqual(parsed.arguments, {"to": "a@example.com"})

    def test_rejects_invalid_json(self) -> None:
        self.assertIsNone(parse_tool_call("<function=f>{not-json}</function>"))

    def test_parses_qwen_native_tool_call(self) -> None:
        parsed = parse_tool_call(
            '<tool_call>\n{"name": "lookup", "arguments": {"query": "x"}}\n'
            "</tool_call>"
        )
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.function, "lookup")
        self.assertEqual(parsed.arguments, {"query": "x"})

    def test_parses_qwen_string_arguments(self) -> None:
        parsed = parse_tool_call(
            '<tool_call>{"name": "lookup", '
            '"arguments": "{\\"query\\": \\"x\\"}"}</tool_call>'
        )
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.arguments, {"query": "x"})

    def test_rejects_non_object_arguments(self) -> None:
        self.assertIsNone(parse_tool_call("<function=f>[]</function>"))

    def test_rejects_multiple_tool_calls(self) -> None:
        text = (
            '<tool_call>{"name": "lookup", "arguments": {}}</tool_call>'
            '<tool_call>{"name": "lookup", "arguments": {}}</tool_call>'
        )
        self.assertIsNone(parse_tool_call(text))

    def test_plain_answer_has_no_call(self) -> None:
        self.assertIsNone(parse_tool_call("The answer is 42."))

if __name__ == "__main__":
    unittest.main()
