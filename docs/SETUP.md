# GitHub 프로필 관리 안내

이 저장소는 GitHub Overview와 별도 포트폴리오 웹페이지를 제공한다.

## 프로젝트 소개 관리

프로젝트 설명과 역할을 바꿀 때는 README·[주요 작업](CONTRIBUTIONS.md)·포트폴리오 웹페이지를 함께 갱신한다.

## 구성

- `README.md`: 인사·소개·Tech & Tools·수상·프로젝트 카드·기여 기록을 표시한다.
- `assets/profile-header.svg`: 손 인사와 AI 데이터 흐름을 표현한 모션 헤더다.
- `assets/profile-header-mobile.svg`: 작은 화면용 모션 헤더다.
- `assets/contact-*.svg`: 이메일·포트폴리오·GitHub 연락처 배지다.
- `assets/tech/*.svg`: 프로젝트에서 활용한 기술과 도구 16개의 정적 배지다. 밝은·어두운 테마를 지원한다.
- `index.html`: 자세한 프로젝트 설명을 제공하는 기존 포트폴리오 웹페이지다.
- `profile/snake*.svg`: 실제 GitHub 기여 기록으로 만든 잔디 애니메이션이다.
- `profile/stats*.svg`, `profile/top-langs*.svg`: 테마별 공개 활동·언어 카드다.
- `profile/activity*.svg`: 공개 커밋의 작성 시각을 한국 시간대로 집계한 개발 리듬 카드다. 밝은·어두운 테마와 모바일 배치를 제공한다.
- `scripts/update-activity.py`: GitHub API 조회·중복 제거·시간대 집계·SVG 생성을 담당한다.
- `profile-3d-contrib/`: 날짜별 기여 수를 높이로 나타내는 3D 잔디다.



## 모션과 표시

헤더는 JavaScript나 외부 이미지 요청 없이 SVG CSS 애니메이션으로 동작한다. 동작 줄이기 설정에서는 손 인사·데이터 이동·커서 애니메이션을 정지한다. 600px 이하 화면에서는 글자를 크게 배치한 모바일 헤더를 사용한다.

기여 잔디와 통계는 README 안의 추가 시각화다. GitHub 기본 Popular repositories·기여 달력·활동 내역의 배치는 변경하지 않는다.

## 자동 갱신

`.github/workflows/profile.yml`은 매일 한국 시간 03:17, 수동 실행, 관련 설정 변경 시 실행된다. GitHub 실행 대기 상황에 따라 시간이 달라질 수 있다. 기존 GitHub 토큰을 사용하며 선택적으로 설정된 `PROFILE_TOKEN`이 있으면 이를 사용한다. 토큰 값을 코드나 문서에 넣지 않는다.

잔디는 실제 계정 기여 기록으로 생성한다. 통계 카드는 공개 저장소 집계이며 GitHub 기본 기여 달력과 집계 범위가 다를 수 있다. 언어 비중은 코드 구성으로 숙련도 지표가 아니다. 외부 통계 서비스 장애 시 이전 정상 카드를 유지하고 잔디 갱신은 계속한다.

수동 실행 명령은 다음과 같다.

```sh
gh workflow run profile.yml --repo rokmc1893/rokmc1893 --ref main
```

`README.md` 변경 후 GitHub의 실제 표시를 확인한다. SVG·카드·링크와 밝은·어두운 테마를 확인하고, 생성 이미지에 오류 메시지가 없는지 점검한다.

## 시간대별 개발 리듬

최근 90일의 공개 저장소 커밋을 GitHub Commit Search API로 조회한다. 계정의 커밋 작성자 연결을 확인하고 SHA 중복을 제거한 뒤 `Asia/Seoul` 기준 아침(06–12시), 낮(12–18시), 저녁(18–24시), 새벽(00–06시)으로 집계한다. 커밋 작성 시각으로 개발 습관을 참고하는 표시이며 실제 작업 시간을 측정하지 않는다. 병합 커밋도 작성자가 일치하면 포함된다.

조회 상한은 API 제한에 맞춘 최신 1,000건이며 상한에 도달하면 카드에 범위를 표시한다. 비공개 저장소 커밋·봇 작성 커밋은 포함하지 않는다. 기본 브랜치 기여만 세는 GitHub 기여 달력이나 공개 저장소 언어 카드와는 집계 범위가 다르다. 코드를 복제한 저장소의 동일 SHA는 한 번만 센다. 검색 반영 지연에 따라 최신 커밋이 늦게 포함될 수 있다.

기존 일일 워크플로우에서 최소 권한의 `GITHUB_TOKEN`으로 갱신한다. 별도 토큰 발급이나 외부 통계 서비스가 필요 없다. API 오류·불완전한 검색 응답·페이지 조회 중 결과 수 변경 시 기존 정상 카드를 유지한다. 빈 결과는 0건으로 표시한다.

로컬에서는 인증된 `gh`의 토큰을 메모리에서만 사용하거나 환경의 `GITHUB_TOKEN`·`GH_TOKEN`을 사용한다.

```sh
python3 scripts/update-activity.py
```

집계 경계·시간대 변환·공개 범위·중복 제거·빈 결과·실패 시 자산 보존 검증은 `python3 -m unittest discover -s scripts -p 'test_*.py'`로 실행한다.

## 사용한 오픈소스

- [Platane/snk](https://github.com/Platane/snk): 잔디 애니메이션이다.
- [GitHub Profile 3D Contrib](https://github.com/yoshi389111/github-profile-3d-contrib): 3D 잔디다.
- [GitHub Readme Stats](https://github.com/anuraghazra/github-readme-stats): 통계 카드 형식이다.
- [GitHub Stats Extended](https://github.com/stats-organization/github-stats-extended): 공개 통계 카드 제공 API다.

## 기술 배지

기술은 소개 아래에 Languages, Frontend, Backend & Database, AI & LLM, Tools의 5개 항목으로 표시한다. 독립 구현 능력이나 숙련도 등급을 뜻하지 않는다. 기술 목록을 수정하면 README의 분류·이미지·대체 텍스트를 함께 확인한다.

브랜드 아이콘은 [Simple Icons](https://github.com/simple-icons/simple-icons)의 CC0 SVG 경로를 사용한다. React Native는 React 아이콘을 공유하며, OpenAI API와 Codex에는 직접 작성한 범용 API 연결·터미널 아이콘을 사용한다. 배지는 저장소에서 직접 제공하므로 프로필을 볼 때 외부 배지 서비스에 의존하지 않는다.
