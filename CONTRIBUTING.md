# 기여 가이드

음메(Eum-mae) 저장소에 코드를 넣는 방법을 안내합니다. 음식 메뉴 추천 룰렛 뽑기 시뮬레이터이며, 저장소는 [Bwaaab/eum-mae](https://github.com/Bwaaab/eum-mae)입니다.

상세 정의는 다음 문서를 함께 봅니다.

- [팀 약속](docs/00_team-agreement.md)
- [CI 파이프라인](docs/01_ci-pipeline.md)
- [코드 품질 유지](docs/02_maintaining_code_quality.md)

---

## 1. 준비

1. Python 3.12 이상을 설치합니다
2. 저장소를 클론합니다
3. `pip install -r requirements.txt`
4. `streamlit run app.py`로 실행을 확인합니다

---

## 2. 역할과 소통

| 이름 | 역할 | GitHub | 담당 기능 |
|---|---|---|---|
| 석혜인 | 팀장 | @bwaaab | 이펙트 |
| 장산 | 개발 리드 | @Banlru2 | 룰렛/카드 + 공통 |
| 이규민 | 리뷰·품질 담당 | @schere02 | 리스트 |
| 김가연 | 문서 담당 | @yabi1 | 결과창 |

- 채널: 카카오톡 채팅방 '음메'
- 정기 회의: 매주 월요일 18:30, 온라인
- 이슈·프로젝트: GitHub Issues
- 응답: 채팅 24시간, 풀 리퀘스트 리뷰 48시간
- 작업 전 이슈 등록, 하루 작업 끝에 본인 브랜치에 Push

---

## 3. 작업 흐름

GitHub Flow를 쓰며, 한 사람이 한 브랜치를 맡습니다. `main`에는 직접 푸시하지 않습니다. (9주차부터 브랜치 보호 적용)

1. 작업 시작 전 이슈를 등록합니다. 빈 이슈는 열지 않습니다
2. 최신 `main`에서 브랜치를 만듭니다. 브랜치 수명은 1주 이내를 권장합니다
3. 브랜치에서 구현하고 `streamlit run app.py`로 확인합니다
4. 이슈 하나당 PR 하나를 엽니다. 단일 PR 템플릿을 채우고 `Closes #이슈번호`를 적습니다
5. 작성자 외 팀원 1명 이상을 리뷰어로 지정합니다
6. 승인 1개 이상이고 충돌이 없으면 작성자가 `Merge pull request`를 실행합니다

공통 모듈을 바꿀 때는 이슈 댓글로 먼저 알립니다.

### 브랜치 이름

| 종류 | 형식 | 예 |
|---|---|---|
| 기능 | `feature/#이슈번호-기능명` | `feature/#3-menu-list` |
| 버그 | `fix/#이슈번호-버그명` | `fix/#12-empty-list` |
| 문서 | `docs/#이슈번호-문서명` | `docs/#1-team-agreement` |

기능별 브랜치 예: 리스트 `feature/#-menu-list`, 추첨 `feature/#-gacha-engine`, 이펙트 `feature/#-visual-effects`, 결과창 `feature/#-result-save`, 초기 구조 `feature/#-init-setup`

---

## 4. 이슈

모든 코딩·문서 작업은 시작 전 이슈를 등록합니다. 각자 주 1회 이상을 권장합니다.

이슈 템플릿은 `.github/ISSUE_TEMPLATE/`에 있습니다. `config.yml`에서 빈 이슈를 막습니다.

| 템플릿 | 제목 접두사 | 자동 라벨 | 용도 |
|---|---|---|---|
| `bug-report.yml` | `[버그]:` | `버그` | 오류. 운영체제, 재현, 기대·실제 동작 |
| `feature-template.yml` | `[기능]:` | `기능` | 기능 제안. 맥락, 제안, 대안 |
| `qua-report.yml` | `[질문]:` | `질문` | 버그·기능이 아닌 질문 |

추가로 쓰는 라벨:

- `documentation`: 회의록, 안내서, README
- `good first issue`: 11주차 타 팀 기여용. 쉬운 이슈를 2개 이상 남겨 둡니다

질문은 PR을 열지 않고 이슈에서 답합니다.

---

## 5. 풀 리퀘스트와 리뷰

PR은 `.github/pull_request_template.md` 하나를 사용합니다. 버그·기능·문서 모두 같은 칸을 채웁니다.

- 요약, 변경 종류, 관련 이슈, 변경 내용, 확인 방법, 테스트 계획
- 관련 이슈: `Closes #이슈번호` (버그는 `Fixes #`도 가능)
- 1 이슈 = 1 PR

### 리뷰

- 기한: 등록 후 48시간 이내
- 작성자는 자신의 PR을 단독 승인하지 않습니다
- 리뷰어는 로컬에서 코드를 받아 `streamlit run app.py` 실행과 PEP 8을 확인한 뒤 승인합니다
- 리스트·룰렛·결과창·이펙트가 서로 깨지지 않는지, 빈 목록·항목 1개 같은 경우를 봅니다
- 이슈 라벨은 GitHub Actions(`issue-labels.yml`)가 제목 접두사에 맞춰 붙입니다

---

## 6. 커밋 메시지

```
type: 작업 내용 요약 (#이슈번호)
```

커밋 하나에는 의미 있는 변경 하나만 넣고, 한글로 적습니다. 하루 일과가 끝나면 미완성이어도 원격 브랜치에 푸시합니다.

| 타입 | 의미 | 예 |
|---|---|---|
| `feat` | 새 기능 | `feat: 메뉴 추가 입력창 UI 구현 (#3)` |
| `fix` | 버그 수정 | `fix: 빈 메뉴 목록 추첨 시 예외 처리 (#12)` |
| `docs` | 문서 | `docs: 기여 가이드 정리 (#1)` |
| `refactor` | 동작은 같고 구조만 정리 | `refactor: 추첨 모듈 분리 (#5)` |
| `test` | 테스트 | `test: 빈 목록 추첨 케이스 (#12)` |
| `chore` | 도구, 의존성, 설정 | `chore: requirements.txt 갱신` |

브랜치 종류와 커밋 타입을 맞춥니다. `feature/…` → `feat`, `fix/…` → `fix`, `docs/…` → `docs`.

---

## 7. 코드와 산출물 위치

- PEP 8, 기능마다 파일 1개(`modules/`에 1인 1파일), 파일 입출력은 `encoding="utf-8"`
- 새 라이브러리는 `requirements.txt`에 추가합니다
- 토큰, 비밀번호, 개인정보, 로컬 전용 경로는 올리지 않습니다
- AI 도구는 사용할 수 있습니다. 직접 실행해 확인한 코드만 올리고, PR에 사용 여부를 적습니다

| 경로 | 내용 |
|---|---|
| `app.py`, `requirements.txt` | 루트. 실행 진입점과 의존성 |
| `modules/` | 기능별 파이썬 모듈 |
| `docs/00_team-agreement.md` | 팀 약속 |
| `docs/01_ci-pipeline.md`, `docs/02_maintaining_code_quality.md` | QA·품질 규칙 |
| `docs/meetings/YYYY-MM-DD.md` | 주간 회의록 |

라이선스는 MIT입니다. 행동 수칙은 `CODE_OF_CONDUCT.md`(Contributor Covenant)를 따릅니다.

---

## 8. 외부 기여자 (11주차~)

1. `good first issue`에 댓글로 배정을 요청하고, 지정된 뒤 시작합니다
2. 저장소를 Fork한 뒤 브랜치에서 작업합니다
3. 이 저장소 `main`을 base로 PR을 엽니다
4. 팀원과 같은 이슈·PR 템플릿, 커밋 규칙, 리뷰 기한(48시간)을 따릅니다
