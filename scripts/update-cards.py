"""공개 저장소 통계 카드를 밝은·어두운 테마로 함께 갱신한다."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
import os
import subprocess
import xml.etree.ElementTree as ET

OWNER = os.environ.get('PROFILE_OWNER', 'rokmc1893')
OUTPUT = Path('profile')
CARDS = []
for suffix, ink, accent, border in [
    ('', '334155', '0969DA', 'D0D7DE'),
    ('-dark', 'B8C9DB', '2DD4BF', '303D4D'),
]:
    common = dict(username=OWNER, theme='transparent', bg_color='00000000',
                  title_color=accent, icon_color=accent, text_color=ink,
                  border_color=border, border_radius='12', locale='kr')
    CARDS.extend([
        (f'stats{suffix}.svg', '', {**common, 'show_icons': 'true',
         'hide_rank': 'true', 'custom_title': '공개 활동', 'card_width': '495'}),
        (f'top-langs{suffix}.svg', '/top-langs', {**common, 'layout': 'compact',
         'langs_count': '6', 'card_width': '495', 'custom_title': '공개 저장소의 언어'}),
    ])


def fetch_card(card):
    filename, route, options = card
    url = 'https://github-stats-extended.vercel.app/api' + route + '?' + urlencode(options)
    result = subprocess.run(
        ['curl', '--fail', '--silent', '--show-error', '--location',
         '--max-time', '25', '--retry', '2', '--retry-delay', '2', url],
        check=True, capture_output=True,
    )
    root = ET.fromstring(result.stdout)
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError(f'{filename}: SVG 응답이 아니다.')
    visible = ' '.join(' '.join(n.itertext()) for n in root.iter()
                       if n.tag.rsplit('}', 1)[-1] in ('title', 'desc', 'text')).lower()
    if any(error in visible for error in (
        'something went wrong', 'could not resolve', 'rate limit exceeded',
        'please deploy your own', 'invalid username', 'retry in',
    )):
        raise ValueError(f'{filename}: 통계 서비스의 오류 카드다.')
    print(f'{filename}: SVG 검증 완료')
    return filename, result.stdout


def main():
    # 모든 카드가 정상일 때만 저장해 갱신 실패 시 기존 이미지를 보존한다.
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending = list(pool.map(fetch_card, CARDS))
    OUTPUT.mkdir(exist_ok=True)
    for filename, data in pending:
        temporary = OUTPUT / (filename + '.tmp')
        temporary.write_bytes(data)
        temporary.replace(OUTPUT / filename)


if __name__ == '__main__':
    main()
