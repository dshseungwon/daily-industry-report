# GitHub Actions로 옮기기 (처음 보는 분을 위한 설명 + 셋업)

## GitHub Actions가 뭔가요?

GitHub Actions는 **GitHub이 무료로 빌려주는 자동 실행 서버**입니다. 레포 안에
"이런 일이 생기면(트리거) 이 명령들을 순서대로 실행해라(워크플로우)"라는 설명서
하나(YAML 파일)를 넣어두면, GitHub이 알아서 깨끗한 리눅스 컴퓨터를 하나 띄워서
그 명령을 돌리고, 끝나면 그 컴퓨터를 버립니다. 내 노트북이 꺼져 있어도 됩니다.

핵심 단어 세 개만 알면 됩니다.

- **트리거(on):** 언제 돌릴지. 여기서는 매일 정해진 시각(`schedule`)과, 버튼을 눌러
  수동 실행(`workflow_dispatch`).
- **잡/스텝(jobs/steps):** 실제로 실행할 일들. 여기서는 (1) 레포 받기 (2) Node·Python
  설치 (3) Claude Code 설치 (4) Claude로 리포트 생성·팩트체크 (5) 커밋·푸시.
- **시크릿(secrets):** API 키 같은 비밀값. 코드에 안 적고 GitHub 금고에 넣어두면
  워크플로우가 실행될 때만 꺼내 씁니다.

## 지금 구조 vs 옮긴 뒤 구조

지금(Cowork 스케줄 작업): 백그라운드에서 작업이 돌고, GitHub 토큰(PAT)을 프롬프트에
직접 박아 clone·push. 두 번 겹쳐 실행되는 버그가 있었음.

옮긴 뒤(GitHub Actions): GitHub 서버가 매일 한 번만 실행. 푸시는 레포 자신의
기본 토큰으로 하므로 **PAT가 아예 필요 없습니다**(보안 개선). `concurrency` 설정으로
**중복 실행이 구조적으로 막힙니다**. 생성 로직도 레포에 버전 관리됩니다.

## 파일 두 개를 이 위치에 넣습니다

1. `daily-industry-report.yml`  ->  레포의 **`.github/workflows/daily-industry-report.yml`**
2. `daily-industry-report.prompt.md`  ->  레포의 **`prompts/daily-industry-report.md`**

(폴더 `.github/workflows/`와 `prompts/`가 없으면 새로 만들면 됩니다.)

## 직접 해주셔야 하는 셋업 (3단계)

### 1) API 키를 시크릿으로 등록 (이것만 제가 못 합니다)
레포 페이지에서 **Settings → Secrets and variables → Actions → New repository secret**.
- Name: `ANTHROPIC_API_KEY`
- Value: 본인 Anthropic API 키 (console.anthropic.com 에서 발급)

> 주의: API 키를 쓰면 구독요금이 아니라 **API 종량제 요금**으로 과금됩니다. 매일 7개
> 리포트 + 팩트체크는 토큰을 꽤 씁니다. 비용이 걱정되면 워크플로우의 `CLAUDE_MODEL`을
> `opus`에서 `sonnet`으로 바꾸세요. 한도가 걱정되면 콘솔에서 spend limit을 거세요.

### 2) 실행 시각 확인 (선택)
워크플로우의 `cron: "0 21 * * *"`는 **UTC 기준**입니다. 21:00 UTC = 한국시간
다음날 06:00. 다른 시각을 원하면 KST에서 9시간을 빼서 적으세요. 예) 오전 8시 KST =
`0 23 * * *`.

### 3) 두 파일을 레포에 커밋
위 두 경로에 파일을 올리고 main에 push하면 끝입니다. (원하시면 이 부분은 제가
대신 커밋해 드릴 수 있습니다. 단, 키 등록(1번)은 보안상 직접 하셔야 합니다.)

## 동작 확인하는 법

레포의 **Actions 탭 → Daily Industry Report → Run workflow** 버튼으로 즉시 한 번
돌려보세요(매일까지 안 기다려도 됩니다). 로그가 실시간으로 보이고, 끝나면 새 커밋과
`reports/<오늘날짜>/` 폴더가 생깁니다. 실패하면 빨간 X와 함께 어느 스텝에서 멈췄는지
로그에 그대로 나옵니다.

## 알아두면 좋은 함정

- **cron은 UTC.** 한국시간이 아닙니다.
- **시각이 칼같지 않습니다.** GitHub 부하에 따라 수 분~수십 분 밀릴 수 있습니다.
  "정확히 6:00"이 중요하면 외부 스케줄러로 트리거해야 하지만, 일일 리포트엔 무방합니다.
- **푸시 권한.** 워크플로우에 `permissions: contents: write`가 있어야 커밋이 푸시됩니다
  (이미 넣어뒀습니다).
- **`--dangerously-skip-permissions`** 는 일회용 격리 VM에서만 안전합니다. 내 컴퓨터의
  터미널에서 같은 플래그를 함부로 쓰면 안 됩니다.

## 옮겨도 안 바뀌는 것 (지난번 얘기)

런타임을 GitHub Actions로 옮겨도 "발행만 하고 안 본다"는 문제는 그대로입니다. 그건
배포(푸시·다이제스트) 문제라 별개입니다. 원하시면 매일 빌드 끝에 "오늘 7개 중 볼 1개 +
3줄 요약"을 메일이나 Slack으로 보내는 스텝을 이 워크플로우에 한 칸 더 붙일 수 있습니다.
