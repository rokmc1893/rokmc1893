"""공개 커밋의 작성 시각을 한국 시간으로 집계하고 프로필 카드를 생성한다."""
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET

OUTPUT = Path(__file__).resolve().parents[1] / 'profile'
KST = ZoneInfo('Asia/Seoul')
LIMIT = 1000
PERIOD = 90
PHASES = [('아침', '06–12시', 6), ('낮', '12–18시', 12),
          ('저녁', '18–24시', 18), ('새벽', '00–06시', 0)]


def api_token():
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        return token
    # 로컬 실행에서도 토큰을 파일이나 로그에 기록하지 않는다.
    result = subprocess.run(['gh', 'auth', 'token'], check=True,
                            capture_output=True, text=True)
    return result.stdout.strip()


def fetch_commits(owner, start, end):
    token = api_token()
    items = []
    query = (f'author:{owner} is:public '
             f'author-date:{start.isoformat()}..{end.isoformat()}')
    total = None
    for page in range(1, LIMIT // 100 + 1):
        params = urlencode(dict(q=query, sort='author-date', order='desc',
                                per_page=100, page=page))
        request = Request('https://api.github.com/search/commits?' + params,
                          headers={'Accept': 'application/vnd.github+json',
                                   'Authorization': f'Bearer {token}',
                                   'X-GitHub-Api-Version': '2022-11-28',
                                   'User-Agent': 'github-profile-activity'})
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
        if payload.get('incomplete_results') is not False:
            raise ValueError('GitHub 검색이 완료되지 않아 기존 카드를 유지한다.')
        batch = payload.get('items')
        if not isinstance(batch, list) or not isinstance(payload.get('total_count'), int):
            raise ValueError('GitHub 검색 응답 형식이 올바르지 않다.')
        if total is None:
            total = payload['total_count']
        elif total != payload['total_count']:
            raise ValueError('페이지 조회 중 검색 결과가 바뀌어 기존 카드를 유지한다.')
        items.extend(batch)
        if len(items) >= min(total, LIMIT):
            break
        if len(batch) < 100:
            raise ValueError('검색 결과 일부가 누락되어 기존 카드를 유지한다.')
    return items[:LIMIT], total > LIMIT


def aggregate(items, owner, start, end):
    hours = Counter()
    seen = set()
    for item in items:
        if item.get('repository', {}).get('private') is not False:
            continue
        author = item.get('author') or {}
        if str(author.get('login', '')).casefold() != owner.casefold():
            continue
        sha = item.get('sha', '')
        if not re.fullmatch(r'[0-9a-fA-F]{40,64}', sha):
            raise ValueError('커밋 식별자가 올바르지 않다.')
        sha = sha.lower()
        if sha in seen:
            continue
        date = datetime.fromisoformat(item['commit']['author']['date'].replace('Z', '+00:00'))
        if date.tzinfo is None:
            raise ValueError('커밋 작성 시각에 시간대가 없다.')
        if not start <= date <= end:
            continue
        seen.add(sha)
        hours[date.astimezone(KST).hour] += 1
    phases = [sum(hours[h] for h in range(begin, begin + 6)) for _, _, begin in PHASES]
    return hours, phases


def icon(index, x, y, color):
    sun = ('<circle cx="0" cy="0" r="6"/>'
           '<path d="M0-12v3M0 9v3M-12 0h3M9 0h3M-8-8l2 2M6 6l2 2M-8 8l2-2M6-6l2-2"/>')
    shapes = [sun,
              '<circle cx="0" cy="0" r="7"/><path d="M0-14v3M0 11v3M-14 0h3M11 0h3M-10-10l2 2M8 8l2 2M-10 10l2-2M8-8l2-2"/>',
              '<path d="M-13 7h26M-9 3a9 9 0 0 1 18 0M0-13v4M-12-8l3 3M12-8l-3 3"/>',
              '<path d="M4-12a12 12 0 1 0 9 17A11 11 0 0 1 4-12Z"/>']
    return f'<g transform="translate({x} {y})" stroke="{color}" stroke-width="1.7" fill="none" stroke-linecap="round" stroke-linejoin="round">{shapes[index]}</g>'


def render(hours, counts, start, end, capped=False, dark=False, mobile=False):
    total = sum(counts)
    width, height = (480, 568) if mobile else (1000, 314)
    palette = dict(bg='#101c2d', panel='#16273a', ink='#eff6fc', muted='#9ab2c9',
                   border='#2b4056', accent='#82e7dc', track='#23394f') if dark else dict(
                   bg='#f8fbff', panel='#ffffff', ink='#17334d', muted='#5b7288',
                   border='#d7e5ef', accent='#087f8c', track='#e7f0f6')
    p = palette
    colors = ['#f4b655', '#38bdf8', '#2dd4bf', '#9f9af4'] if dark else ['#b77513', '#0979b2', '#087f8c', '#7660bb']
    peaks = [PHASES[i][0] for i, count in enumerate(counts) if count == max(counts)]
    headline = ('새로운 기록을 기다리는 중' if not total else
                f'가장 많이 기록한 시간 · {peaks[0]}' if len(peaks) == 1 else
                '시간대마다 쌓이는 기록')
    dates = f'{start.astimezone(KST):%Y.%m.%d}–{end.astimezone(KST):%m.%d}'
    scope = f'최근 {PERIOD}일 공개 커밋 · {"최신 1,000건 중 " if capped else ""}{total:,}건'
    description = f'{scope}. {dates}. Asia/Seoul 기준 커밋 작성 시각. ' + ', '.join(
        f'{label} {count}건' for (label, _, _), count in zip(PHASES, counts))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">나의 개발 리듬</title>', f'<desc id="desc">{escape(description)}</desc>',
             '<style>text{font-family:"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif}.num{font-variant-numeric:tabular-nums}</style>',
             f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="18" fill="{p["bg"]}" stroke="{p["border"]}"/>',
             f'<path d="M25 32h4m5 0h4m5 0h4" stroke="{p["accent"]}" stroke-width="4" stroke-linecap="round"/>',
             f'<text x="60" y="39" font-size="22" font-weight="700" fill="{p["ink"]}">나의 개발 리듬</text>']
    if mobile:
        parts += [f'<text x="26" y="74" font-size="16" fill="{p["muted"]}">{escape(headline)}</text>']
        card_w, card_h, gap, top = 205, 155, 18, 98
    else:
        parts += [f'<text x="974" y="38" text-anchor="end" font-size="15" fill="{p["muted"]}">{escape(headline)}</text>']
        card_w, card_h, gap, top = 224, 150, 18, 61
    for i, ((label, clock, _), count) in enumerate(zip(PHASES, counts)):
        x = 26 + (i % 2 if mobile else i) * (card_w + gap)
        y = top + (i // 2 * (card_h + gap) if mobile else 0)
        percentage = count / total * 100 if total else 0
        parts += [f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="12" fill="{p["panel"]}" stroke="{p["border"]}"/>',
                  icon(i, x+29, y+31, colors[i]),
                  f'<text x="{x+51}" y="{y+36}" fill="{p["ink"]}" font-size="17" font-weight="600">{label}</text>',
                  f'<text x="{x+18}" y="{y+88}" fill="{p["ink"]}" font-size="32" font-weight="700" class="num">{percentage:.1f}<tspan font-size="17" fill="{p["muted"]}">%</tspan></text>',
                  f'<text x="{x+card_w-18}" y="{y+86}" text-anchor="end" fill="{p["muted"]}" font-size="15" class="num">{count:,}건</text>',
                  f'<rect x="{x+18}" y="{y+105}" width="{card_w-36}" height="5" rx="2.5" fill="{p["track"]}"/>']
        if count:
            parts += [f'<rect x="{x+18}" y="{y+105}" width="{(card_w-36)*count/total:.2f}" height="5" rx="2.5" fill="{colors[i]}"/>']
        parts += [f'<text x="{x+18}" y="{y+132}" fill="{p["muted"]}" font-size="13">{clock}</text>']
    graph_y = 490 if mobile else 250
    graph_x = 26 if mobile else 740
    for hour in range(24):
        bar_h = 3 + (hours.get(hour, 0) / max(max(hours.values(), default=0), 1) * 21)
        parts += [f'<rect x="{graph_x+hour*9}" y="{graph_y-bar_h:.2f}" width="5" height="{bar_h:.2f}" rx="2" fill="{p["accent"]}" opacity="{1 if hours.get(hour, 0) else .18}"/>']
    if mobile:
        lines = [(26, 449, scope), (26, 520, '한국 시간 · 커밋 작성 시각 기준'), (26, 547, dates)]
    else:
        lines = [(26, 244, scope), (26, 280, f'한국 시간 · 커밋 작성 시각 기준    {dates}')]
    parts += [f'<text x="{x}" y="{y}" fill="{p["muted"]}" font-size="14">{escape(text)}</text>' for x, y, text in lines]
    parts += ['</svg>']
    svg = '\n'.join(parts) + '\n'
    ET.fromstring(svg)
    return svg


def main():
    owner = os.environ.get('PROFILE_OWNER', 'rokmc1893')
    if not re.fullmatch(r'[A-Za-z0-9-]{1,39}', owner):
        raise ValueError('GitHub 사용자 이름이 올바르지 않다.')
    end = datetime.now(timezone.utc).replace(microsecond=0)
    start = end - timedelta(days=PERIOD)
    items, capped = fetch_commits(owner, start, end)
    hours, counts = aggregate(items, owner, start, end)
    # 네 가지 변형이 모두 정상 생성된 다음 기존 이미지를 교체한다.
    generated = {}
    for mobile in (False, True):
        for dark in (False, True):
            name = 'activity' + ('-mobile' if mobile else '') + ('-dark' if dark else '') + '.svg'
            generated[name] = render(hours, counts, start, end, capped, dark, mobile)
    OUTPUT.mkdir(exist_ok=True)
    for name, svg in generated.items():
        temporary = OUTPUT / (name + '.tmp')
        temporary.write_text(svg, encoding='utf-8')
        temporary.replace(OUTPUT / name)
    print(f'공개 커밋 {sum(counts):,}건으로 활동 카드 4개를 갱신했다.')


if __name__ == '__main__':
    main()
