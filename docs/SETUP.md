# F1 GitHub 프로필 설정 가이드

계정: [rokmc1893](https://github.com/rokmc1893)  
프로필 저장소: [rokmc1893/rokmc1893](https://github.com/rokmc1893/rokmc1893)

## 1. 파일 구조

```text
README.md
assets/f1-racing.svg
.github/workflows/profile.yml
docs/SETUP.md
scripts/update-cards.py
profile-3d-contrib/
  profile-green.svg
  profile-night-green.svg
profile/
  stats.svg
  top-langs.svg
  pin-healthcare.svg
  pin-legal.svg
  pin-policy.svg
```

자동 생성 이미지에는 계정의 실제 데이터가 들어갑니다. 높이는 날짜별 GitHub 기여 수를 나타내므로 커밋 외 PR·이슈 등 기여도 포함될 수 있습니다. 공동 프로젝트의 본인 기여도 GitHub의 집계 조건에 따라 포함됩니다.

## 2. 3D 잔디와 카드 자동 갱신

아래 전체 내용을 `.github/workflows/profile.yml`에 저장합니다.
파일은 이미 설치돼 있습니다. 매일 한국 시간 **03:17**에 실행되며 GitHub 실행 대기 상황에 따라 늦어질 수 있습니다.
`main` 브랜치에서 실행됩니다. 순차 실행으로 그래프와 카드의 저장 시점이 충돌하지 않도록 구성했습니다.

```yaml
name: Update racing profile

on:
  schedule:
    - cron: "17 18 * * *" # 매일 03:17 KST (UTC+9)
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - ".github/workflows/profile.yml"
      - "scripts/update-cards.py"

permissions:
  contents: write

concurrency:
  group: racing-profile-${{ github.ref }}
  cancel-in-progress: false

jobs:
  telemetry:
    name: Generate 3D grass and racing telemetry
    runs-on: ubuntu-latest
    timeout-minutes: 20
    env:
      HAS_PROFILE_TOKEN: ${{ secrets.PROFILE_TOKEN != '' }}
    steps:
      - name: Checkout profile
        uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5

      - name: Generate actual 3D contributions
        uses: yoshi389111/github-profile-3d-contrib@7d95e7d4cdc028dd1e1cbd957d65f35efb12ae39 # latest verified 2026-10-07
        env:
          GITHUB_TOKEN: ${{ secrets.PROFILE_TOKEN || secrets.GITHUB_TOKEN }}
          USERNAME: ${{ github.repository_owner }}

      - name: Render stats.svg
        if: env.HAS_PROFILE_TOKEN == 'true'
        uses: stats-organization/github-readme-stats-action@2c498845f71017821efaad14293ebc736156ef21 # v2.1.0
        with:
          card: stats
          options: username=${{ github.repository_owner }}&theme=radical&bg_color=0D1117&title_color=FF3535&icon_color=FF3535&text_color=C9D1D9&border_color=30363D&show_icons=true&include_all_commits=true&hide_rank=true&custom_title=Season%20Telemetry&card_width=495
          path: profile/stats.svg
          token: ${{ secrets.PROFILE_TOKEN || secrets.GITHUB_TOKEN }}
          core_version: "2.1.3"
          fail_on_error: "true"

      - name: Render top-langs.svg
        if: env.HAS_PROFILE_TOKEN == 'true'
        uses: stats-organization/github-readme-stats-action@2c498845f71017821efaad14293ebc736156ef21 # v2.1.0
        with:
          card: top-langs
          options: username=${{ github.repository_owner }}&theme=radical&bg_color=0D1117&title_color=FF3535&icon_color=FF3535&text_color=C9D1D9&border_color=30363D&layout=compact&langs_count=6&card_width=495&custom_title=Power%20Unit%20Languages
          path: profile/top-langs.svg
          token: ${{ secrets.PROFILE_TOKEN || secrets.GITHUB_TOKEN }}
          core_version: "2.1.3"
          fail_on_error: "true"

      - name: Render pin-healthcare.svg
        if: env.HAS_PROFILE_TOKEN == 'true'
        uses: stats-organization/github-readme-stats-action@2c498845f71017821efaad14293ebc736156ef21 # v2.1.0
        with:
          card: pin
          options: username=${{ github.repository_owner }}&theme=radical&bg_color=0D1117&title_color=FF3535&icon_color=FF3535&text_color=C9D1D9&border_color=30363D&repo=Capstone-Design
          path: profile/pin-healthcare.svg
          token: ${{ secrets.PROFILE_TOKEN || secrets.GITHUB_TOKEN }}
          core_version: "2.1.3"
          fail_on_error: "true"

      - name: Render pin-legal.svg
        if: env.HAS_PROFILE_TOKEN == 'true'
        uses: stats-organization/github-readme-stats-action@2c498845f71017821efaad14293ebc736156ef21 # v2.1.0
        with:
          card: pin
          options: username=${{ github.repository_owner }}&theme=radical&bg_color=0D1117&title_color=FF3535&icon_color=FF3535&text_color=C9D1D9&border_color=30363D&repo=Google_AI_Agent
          path: profile/pin-legal.svg
          token: ${{ secrets.PROFILE_TOKEN || secrets.GITHUB_TOKEN }}
          core_version: "2.1.3"
          fail_on_error: "true"

      - name: Render pin-policy.svg
        if: env.HAS_PROFILE_TOKEN == 'true'
        uses: stats-organization/github-readme-stats-action@2c498845f71017821efaad14293ebc736156ef21 # v2.1.0
        with:
          card: pin
          options: username=${{ github.repository_owner }}&theme=radical&bg_color=0D1117&title_color=FF3535&icon_color=FF3535&text_color=C9D1D9&border_color=30363D&repo=INU-X-UOU
          path: profile/pin-policy.svg
          token: ${{ secrets.PROFILE_TOKEN || secrets.GITHUB_TOKEN }}
          core_version: "2.1.3"
          fail_on_error: "true"

      - name: Fetch public telemetry without a PAT
        if: env.HAS_PROFILE_TOKEN != 'true'
        env:
          PROFILE_OWNER: ${{ github.repository_owner }}
        run: python3 scripts/update-cards.py

      - name: Validate generated assets
        run: |
          python3 - <<'PY'
          from pathlib import Path
          import xml.etree.ElementTree as ET
          paths = [
              Path("profile-3d-contrib/profile-green.svg"),
              Path("profile-3d-contrib/profile-night-green.svg"),
              *sorted(Path("profile").glob("*.svg")),
          ]
          if len(paths) != 7:
              raise SystemExit("Expected 2 contribution graphs and 5 cards")
          for path in paths:
              if not path.is_file() or path.stat().st_size < 100:
                  raise SystemExit(f"Missing or empty asset: {path}")
              ET.parse(path)
          PY

      - name: Save telemetry when data changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add profile-3d-contrib/profile-green.svg profile-3d-contrib/profile-night-green.svg profile/*.svg
          if git diff --cached --quiet; then
            echo "Telemetry is already up to date."
            exit 0
          fi
          git commit -m "chore: refresh racing profile telemetry"
          git push origin HEAD:main
```

3D 그래프는 `yoshi389111/github-profile-3d-contrib`를 사용합니다.
밝은 화면에는 `profile-green.svg`, 어두운 화면에는 `profile-night-green.svg`가 표시됩니다.
액션이 생성하는 여러 변형 중 README에서 쓰는 두 파일만 저장합니다.

통계·언어·핀 카드는 원본 `anuraghazra/github-readme-stats`가 안내하는 후속
`stats-organization/github-stats-extended`의 공개 API로 받아 저장합니다.
PAT를 설정하면 `stats-organization/github-readme-stats-action`의 직접 생성 방식으로 자동 전환됩니다.
기본 GitHub 토큰은 다른 저장소의 통계 조회에 제한이 있어 카드에는 공개 API를 사용합니다.
`radical`을 기반으로 배경·제목·아이콘 색을 카본 블랙·레드에 맞췄습니다.
카드는 저장소 자체에서 제공됩니다. 매일 갱신할 때는 공개 API에 의존하지만, 페이지를 볼 때는 마지막 정상 이미지를 사용합니다.
`scripts/update-cards.py`가 오류 카드를 검사하고 재시도합니다. 갱신 실패 시 이전 커밋의 정상 이미지가 유지됩니다.

공개 카드 다운로드 스크립트의 전체 코드는 [scripts/update-cards.py](../scripts/update-cards.py)에 있습니다.

## 3. 기본 Token 설정: 발급할 필요 없음

현재 설정은 GitHub가 실행마다 자동 제공하는 `secrets.GITHUB_TOKEN`을 사용합니다.
3D 잔디는 기본 토큰으로, 통계 카드는 공개 API로 계정의 공개 데이터를 조회합니다. 별도 토큰을 복사하거나 Secrets를 만들 필요가 없습니다.
워크플로우의 `permissions: contents: write`는 생성된 이미지를 이 프로필 저장소에 커밋하는 데 사용됩니다.

첫 실행 또는 수동 갱신:

1. 저장소의 **Actions** 탭을 엽니다.
2. **Update racing profile**을 선택합니다.
3. **Run workflow**에서 브랜치 `main`을 선택하고 실행합니다.
4. **Generate actual 3D contributions**와 카드 렌더링 단계의 완료를 확인합니다.
5. 성공한 실행 뒤 `profile/`과 `profile-3d-contrib/`에 SVG가 저장됩니다.
6. 프로필을 새로고침합니다. GitHub 이미지 캐시 때문에 표시가 늦게 바뀔 수 있습니다.

CLI로 실행하려면:

```bash
gh workflow run profile.yml --repo rokmc1893/rokmc1893 --ref main
gh run list --repo rokmc1893/rokmc1893 --workflow profile.yml --limit 5
```

## 4. 선택 사항: 비공개 기여와 PAT

현재 적용은 공개 데이터 기준입니다. 비공개 프로젝트 정보를 추가 표시하려는 경우에만 이 단계를 진행하세요.
개인 프로필 잔디에는 GitHub의 **Contribution settings → Private contributions**를 켜서 비공개 기여 수를 표시할 수도 있습니다.
이 설정과 외부 카드가 비공개 저장소를 읽을 권한은 서로 다른 문제입니다.

여러 비공개 저장소의 통계를 포함하는 액션 문서는 classic PAT의 `repo`와 `read:user` 권한을 안내합니다.
`repo`는 넓은 권한이므로 공개 통계만 필요하다면 기본 토큰을 유지하세요.

1. GitHub **Settings → Developer settings → Personal access tokens → Tokens (classic)**을 엽니다.
2. **Generate new token (classic)**을 선택합니다.
3. 이름을 `Profile telemetry`처럼 정하고 30일 또는 90일의 만료 기간을 지정합니다.
4. 필요한 경우 `repo`와 `read:user`를 선택합니다. 기본 실행에는 PAT가 필요하지 않습니다.
5. 토큰을 생성합니다. 값을 README·커밋·채팅에 넣지 마세요.
6. 프로필 저장소에서 **Settings → Secrets and variables → Actions → New repository secret**을 엽니다.
7. 이름은 `PROFILE_TOKEN`, 값은 생성한 토큰으로 저장합니다.
8. 조직 저장소라면 조직 정책과 SSO 승인이 필요한지 확인합니다.
9. **Run workflow**를 다시 실행합니다.
10. 토큰이 만료되면 새 토큰으로 같은 Secret 값을 교체합니다.

3D 액션에는 `secrets.PROFILE_TOKEN || secrets.GITHUB_TOKEN`을 사용합니다.
Secret 추가 시 통계 카드는 공개 API 대신 Stats Action으로 생성하므로 YAML 수정이 필요 없습니다.
이미지 커밋은 checkout의 기본 GitHub 토큰으로 수행합니다.
비공개 통계 표시를 켜면 생성된 이미지가 공개 프로필에 저장되므로 공개할 범위를 먼저 정하세요.
최소 범위로 접근 가능한 fine-grained PAT는 GitHub가 권장하지만, 다중 조직·외부 협업 저장소 접근에는 제한이 있으며 이 통계 액션의 안내와 실제 쿼리 권한을 함께 확인해야 합니다.

## 5. 프로필 문구·연락처 수정

- 이름, 소개, 관심 분야: `README.md`의 **Driver Briefing**을 편집합니다.
- **Currently learning**은 요청대로 비워 뒀습니다. 해당 HTML 주석 옆에 나중에 기술을 적으면 됩니다.
- `Currently working on`은 진행 프로젝트의 상세 일정 확인 없이 기존 관심 분야에 맞춘 소개 문구입니다. 실제 진행 프로젝트가 정해지면 링크로 교체할 수 있습니다.
- LinkedIn은 전달받은 개인 프로필 주소입니다.
- 블로그 배지는 주소가 생기면 Email·LinkedIn 옆에 추가합니다.

예시 템플릿의 `YOUR_BLOG_URL`은 실제 주소로 바꾼 후 사용하세요:

```html
<a href="YOUR_BLOG_URL">
  <img alt="Blog" src="https://img.shields.io/badge/BLOG-171C26?style=for-the-badge&amp;logo=rss&amp;logoColor=FF3535">
</a>
```

타이핑 SVG 문구는 `lines=` 값에서 변경합니다. 문구 사이에는 세미콜론, 공백에는 `+`, 특수문자에는 URL 인코딩을 사용합니다.
현재 타이핑 효과와 배지·카운터는 외부 이미지 서비스를 사용합니다.
방문 카운터는 순 방문자 수가 아닌 이미지 요청 기반 조회 카운터이며, 캐시·재조회 영향을 받습니다.

## 6. 오류 확인

- **403 / push 실패**: 실행 로그와 저장소 Actions 정책·브랜치 보호를 확인합니다. `contents: write`가 허용돼야 합니다. 보호 규칙이 있으면 생성 파일을 PR로 반영하는 방식으로 조정합니다.
- **API 제한·통계 조회 실패**: 공개 카드 스크립트는 오류 카드 저장을 막고, PAT 실행은 `fail_on_error: true`로 설정했습니다. 잠시 후 수동 실행하고 필요할 때 PAT 사용을 검토합니다.
- **잔디 누락**: 커밋 이메일이 계정에 연결됐는지, 기본 브랜치에 반영됐는지 확인합니다. GitHub 자체 집계에 최대 24시간이 걸릴 수 있습니다.
- **자동 실행 중단**: 공개 저장소의 예약 워크플로우는 60일간 활동이 없으면 비활성화될 수 있습니다. Actions에서 다시 활성화합니다.
- **폰·좁은 화면**: 통계 이미지는 각각 49% 너비입니다. 큰 화면에서는 나란히 보이고, 좁은 화면에서 글자가 작다면 너비를 100%로 변경해 세로 배치하세요.
- **애니메이션**: 헤더는 스크립트 없는 SVG CSS 애니메이션입니다. 동작 줄이기 설정을 쓰는 브라우저에서는 헤더 애니메이션이 정지합니다.

## 사용한 프로젝트와 공식 문서

- [3D Contribution Graph](https://github.com/yoshi389111/github-profile-3d-contrib)
- [Readme Typing SVG](https://github.com/DenverCoder1/readme-typing-svg)
- [GitHub Readme Stats 원본 안내](https://github.com/anuraghazra/github-readme-stats)
- [GitHub Readme Stats Action](https://github.com/stats-organization/github-readme-stats-action)
- [조회 카운터](https://github.com/antonkomarev/github-profile-views-counter)
- [GitHub PAT 발급](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- [기여 기록 누락](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-missing-contributions)
