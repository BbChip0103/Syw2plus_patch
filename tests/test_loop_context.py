#!/usr/bin/env python3
"""The loop's compact inbox is a read-only index, never a replacement source."""
import hashlib
import re
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('loop_context', ROOT / 'tools/loop_context.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SOURCE = '''# INBOX\n\n> New instructions win.\n\n## 처리 대기\n\n### Priority — newest first\n\nAlways follow this policy.\n\n- [x] Completed task; its policy still applies.\n  Keep this continuation.\n\n      → (lap 1) Old result\n      Evidence and an unresolved warning.\n\n- [ ] Pending task\n  Full pending instruction.\n\n      → (lap 2) More investigation\n      not completed\n\nA new unindented instruction after the history.\n\n  → Unknown indentation stays verbatim.\n\n## 처리 완료\n\n- [x] Preserve this directive too.\n\n## 되물음\n\n### Q2 unresolved\n\nQuestion body.\n```md\n### Not a topic\n```\n\n### Q1 resolved\n\nHistorical answer.\n'''.encode()


class LoopContextTest(unittest.TestCase):
    def test_representative_render_is_exact(self):
        self.assertEqual(MODULE.render_context(SOURCE, 'INBOX.md'), '''# INBOX 읽기 색인 (원문을 수정하지 않음)
Source: `INBOX.md`; SHA-256: `cfdf5ae3ed19618139701b350137ab578829f608ec4763d572f6d4b97cb85840`

지시 본문·우선순위는 아래 그대로 읽는다. 체크 완료는 상시 규칙 폐기가 아니다.
생략한 lap 기록과 되물음은 해결 여부를 추정하지 않는다. 작업할 항목·관련 질문의
원문 범위를 먼저 열어 남은 조건과 최신 증거를 확인한다. 원문이 바뀌면 다시 생성한다.

# INBOX

> New instructions win.

## 처리 대기

### Priority — newest first

Always follow this policy.

지시 원문 전체: [INBOX.md:11–16](INBOX.md#L11-L16)
- [x] Completed task; its policy still applies.
  Keep this continuation.

> 최근 작업기록 발췌 (완료 판정 아님): → (lap 1) Old result
> 생략한 기록 원문: [INBOX.md:14–15](INBOX.md#L14-L15)

지시 원문 전체: [INBOX.md:17–26](INBOX.md#L17-L26)
- [ ] Pending task
  Full pending instruction.

> 최근 작업기록 발췌 (완료 판정 아님): → (lap 2) More investigation
> 생략한 기록 원문: [INBOX.md:20–21](INBOX.md#L20-L21)

A new unindented instruction after the history.

  → Unknown indentation stays verbatim.

## 처리 완료

지시 원문 전체: [INBOX.md:29–30](INBOX.md#L29-L30)
- [x] Preserve this directive too.

## 되물음

### Q2 unresolved
원문 전체 (상태 판정 없음): [INBOX.md:33–39](INBOX.md#L33-L39)

### Q1 resolved
원문 전체 (상태 판정 없음): [INBOX.md:40–42](INBOX.md#L40-L42)

''')

    def test_preserves_directives_and_indexes_only_explicit_history(self):
        result = MODULE.render_context(SOURCE, 'INBOX.md')
        for text in ['> New instructions win.', '### Priority — newest first',
                     'Always follow this policy.',
                     '- [x] Completed task; its policy still applies.\n  Keep this continuation.',
                     '- [ ] Pending task\n  Full pending instruction.',
                     'A new unindented instruction after the history.',
                     '  → Unknown indentation stays verbatim.',
                     '- [x] Preserve this directive too.']:
            self.assertIn(text, result)
        self.assertIn('INBOX.md#L14-L15', result)
        self.assertIn('INBOX.md#L17-L26', result)
        self.assertIn('INBOX.md#L20-L21', result)
        self.assertNotIn('      Evidence and an unresolved warning.', result)
        self.assertIn(hashlib.sha256(SOURCE).hexdigest(), result)

    def test_all_questions_have_exact_source_ranges_without_status_guessing(self):
        result = MODULE.render_context(SOURCE, 'INBOX.md')
        self.assertIn('### Q2 unresolved', result)
        self.assertIn('INBOX.md#L33-L39', result)
        self.assertIn('### Q1 resolved', result)
        self.assertIn('INBOX.md#L40-L42', result)
        self.assertNotIn('### Not a topic', result)
        self.assertNotIn('Question body.', result)

    def test_fenced_history_is_preserved(self):
        source = b'# INBOX\n```text\n      -> literal\n```\n'
        source = source.replace(b'->', '→ (lap 1)'.encode())
        self.assertIn(source.decode(), MODULE.render_context(source, 'INBOX.md'))

    def test_history_excerpt_uses_latest_record(self):
        source = ('# INBOX\n      → (lap 1) Old\n      old body\n\n'
                  '      → (lap 2) Latest\n      new body\n').encode()
        result = MODULE.render_context(source, 'INBOX.md')
        self.assertIn('→ (lap 2) Latest', result)
        self.assertNotIn('→ (lap 1) Old', result)
        self.assertIn('INBOX.md#L2-L6', result)

    def test_history_excerpt_is_bounded(self):
        source = ('# INBOX\n      → (lap 3) ' + 'x' * 1000 + '\n      body\n').encode()
        result = MODULE.render_context(source, 'INBOX.md')
        self.assertLess(len(result), 1000)
        self.assertIn('INBOX.md#L2-L3', result)

    def test_unknown_question_layout_is_not_silently_hidden(self):
        source = b'# INBOX\n\n## other\n### Anything\nDo not drop me.\n'
        self.assertIn(source.decode(), MODULE.render_context(source, 'INBOX.md'))

    def test_repository_source_is_preserved_or_exactly_referenced(self):
        path = ROOT / 'docs/feedback/INBOX.md'
        original = path.read_bytes()
        result = MODULE.render_context(original, 'INBOX.md')
        hidden = set()
        for start, end in re.findall(
                r'(?:생략한 기록 원문|원문 전체 \(상태 판정 없음\)):[^\n]*#L(\d+)-L(\d+)', result):
            hidden.update(range(int(start), int(end) + 1))
        position = 0
        for number, line in enumerate(original.decode().splitlines(keepends=True), 1):
            if number not in hidden:
                found = result.find(line, position)
                self.assertNotEqual(found, -1, f'unreferenced source line {number}: {line}')
                position = found + len(line)
        self.assertEqual(path.read_bytes(), original)

    def test_cli_preserves_original_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'INBOX.md'
            original = SOURCE.replace(b'\n', b'\r\n')
            path.write_bytes(original)
            result = subprocess.run(['python3', str(ROOT / 'tools/loop_context.py'),
                                     '--inbox', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(path.read_bytes(), original)
            self.assertIn(hashlib.sha256(original).hexdigest(), result.stdout)


if __name__ == '__main__':
    unittest.main()
