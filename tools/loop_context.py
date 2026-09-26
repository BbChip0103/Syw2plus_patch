#!/usr/bin/env python3
"""Read-only INBOX view: preserve directives, link lap history and question topics."""
import argparse
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HISTORY = re.compile(r'^ {6,}→ \(lap [0-9]')
HEADING = re.compile(r'^(#{1,6}) ')
ENTRY = re.compile(r'^- \[(.)\] ')
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})')


def markdown_structure(lines):
    """Do not treat examples inside Markdown fences as document structure."""
    headings = {}
    fenced = set()
    fence = None
    for index, line in enumerate(lines):
        if fence is not None:
            fenced.add(index)
        match = FENCE.match(line)
        if match:
            fenced.add(index)
            marker = match[1]
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None and (match := HEADING.match(line)):
            headings[index] = len(match[1])
    return headings, fenced


def render_context(data, source):
    lines = data.decode('utf-8').splitlines(keepends=True)
    headings, fenced = markdown_structure(lines)
    entries = {i for i, line in enumerate(lines) if i not in fenced and ENTRY.match(line)}
    output = [
        '# INBOX 읽기 색인 (원문을 수정하지 않음)\n',
        f'Source: `{source}`; SHA-256: `{hashlib.sha256(data).hexdigest()}`\n\n',
        '지시 본문·우선순위는 아래 그대로 읽는다. 체크 완료는 상시 규칙 폐기가 아니다.\n',
        '생략한 lap 기록과 되물음은 해결 여부를 추정하지 않는다. 작업할 항목·관련 질문의\n',
        '원문 범위를 먼저 열어 남은 조건과 최신 증거를 확인한다. 원문이 바뀌면 다시 생성한다.\n\n',
    ]

    def reference(start, end):
        return f'[{source}:{start + 1}–{end}]({source}#L{start + 1}-L{end})'

    index = 0
    while index < len(lines):
        if headings.get(index) == 2 and lines[index].strip() == '## 되물음':
            end = next((i for i in headings if i > index and headings[i] <= 2), len(lines))
            topics = [i for i in headings if index < i < end and headings[i] == 3]
            # Unknown question formatting is not safe to summarize: retain it.
            if topics:
                output.extend(lines[index:topics[0]])
                for start, stop in zip(topics, topics[1:] + [end]):
                    output.append(lines[start])
                    output.append(f'원문 전체 (상태 판정 없음): {reference(start, stop)}\n\n')
                index = end
                continue
        if index in entries:
            end = next((i for i in range(index + 1, len(lines))
                        if i in entries or (i in headings and headings[i] <= 3)), len(lines))
            output.append(f'지시 원문 전체: {reference(index, end)}\n')
        if index not in fenced and HISTORY.match(lines[index]):
            end = index + 1
            while end < len(lines) and (not lines[end].strip() or lines[end].startswith('      ')):
                end += 1
            # Leave separator lines in the visible source rather than swallowing them.
            while end > index + 1 and not lines[end - 1].strip():
                end -= 1
            latest = next((i for i in range(end - 1, index, -1) if HISTORY.match(lines[i])), index)
            excerpt = lines[latest].strip()
            if len(excerpt) > 140:
                excerpt = excerpt[:140] + '…'
            output.append(f'> 최근 작업기록 발췌 (완료 판정 아님): {excerpt}\n')
            output.append(f'> 생략한 기록 원문: {reference(index, end)}\n')
            index = end
            continue
        output.append(lines[index])
        index += 1
    return ''.join(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inbox', type=Path, default=ROOT / 'docs/feedback/INBOX.md')
    args = parser.parse_args()
    try:
        source = args.inbox.resolve()
        label = str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source)
        print(render_context(source.read_bytes(), label), end='')
    except (OSError, UnicodeError) as error:
        parser.exit(1, f'INBOX 읽기 실패; 원문을 직접 확인: {error}\n')


if __name__ == '__main__':
    main()
