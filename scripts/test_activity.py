"""개발 리듬 카드의 집계 범위와 실패 시 자산 보존을 검증한다."""
from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch
import json
import xml.etree.ElementTree as ET

spec = spec_from_file_location('activity', Path(__file__).with_name('update-activity.py'))
activity = module_from_spec(spec)
spec.loader.exec_module(activity)


class ActivityTest(TestCase):
    def setUp(self):
        self.start = datetime(2026, 11, 9, tzinfo=timezone.utc)
        self.end = self.start + timedelta(days=2)

    @staticmethod
    def commit(number, date='2026-11-10T12:00:00+09:00',
               author='rokmc1893', private=False):
        return {'sha': f'{number:040x}', 'author': {'login': author},
                'repository': {'private': private},
                'commit': {'author': {'date': date}}}

    def aggregate(self, commits):
        return activity.aggregate(commits, 'rokmc1893', self.start, self.end)

    def test_phase_boundaries(self):
        commits = [self.commit(i, f'2026-11-10T{hour:02d}:00:00+09:00')
                   for i, hour in enumerate((0, 5, 6, 11, 12, 17, 18, 23))]
        self.assertEqual(self.aggregate(commits)[1], [2, 2, 2, 2])

    def test_utc_converts_to_korean_time(self):
        hours, counts = self.aggregate([self.commit(1, '2026-11-09T21:00:00Z')])
        self.assertEqual(dict(hours), {6: 1})
        self.assertEqual(counts, [1, 0, 0, 0])

    def test_private_unconfirmed_visibility_and_other_authors_are_excluded(self):
        commits = [self.commit(1, private=True), self.commit(2, author='someone'),
                   self.commit(3, private=None), self.commit(4, author='ROKMC1893')]
        self.assertEqual(self.aggregate(commits)[1], [0, 1, 0, 0])

    def test_duplicate_sha_and_outside_period_are_excluded(self):
        commit = self.commit(1)
        commits = [commit, dict(commit),
                   self.commit(2, '2026-11-08T12:00:00Z'),
                   self.commit(3, '2026-11-12T12:00:00Z')]
        self.assertEqual(self.aggregate(commits)[1], [0, 1, 0, 0])

    def test_empty_data_renders_four_valid_variants(self):
        hours, counts = self.aggregate([])
        for mobile in (False, True):
            for dark in (False, True):
                with self.subTest(mobile=mobile, dark=dark):
                    svg = activity.render(hours, counts, self.start, self.end,
                                          dark=dark, mobile=mobile)
                    root = ET.fromstring(svg)
                    self.assertEqual(root.tag, '{http://www.w3.org/2000/svg}svg')
                    self.assertIn('0건', svg)
                    self.assertIn('새로운 기록을 기다리는 중', svg)
                    self.assertNotIn('nan', svg.lower())

    def test_incomplete_api_response_is_rejected(self):
        response = BytesIO(json.dumps({'incomplete_results': True,
                                       'total_count': 0, 'items': []}).encode())
        with patch.object(activity, 'api_token', return_value='test-only'), \
                patch.object(activity, 'urlopen', return_value=response):
            with self.assertRaisesRegex(ValueError, '검색이 완료되지 않아'):
                activity.fetch_commits('rokmc1893', self.start, self.end)

    def test_api_failure_preserves_existing_assets(self):
        with TemporaryDirectory() as temporary:
            output = Path(temporary)
            existing = {output / name: f'이전 정상 카드 {name}'.encode()
                        for name in ('activity.svg', 'activity-dark.svg',
                                     'activity-mobile.svg', 'activity-mobile-dark.svg')}
            for path, data in existing.items():
                path.write_bytes(data)
            with patch.object(activity, 'OUTPUT', output), \
                    patch.object(activity, 'fetch_commits', side_effect=OSError('API 실패')):
                with self.assertRaises(OSError):
                    activity.main()
            self.assertEqual({p: p.read_bytes() for p in output.iterdir()}, existing)


if __name__ == '__main__':
    main()
