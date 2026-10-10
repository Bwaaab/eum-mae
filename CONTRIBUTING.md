# 기여 가이드

음메(Eum-mae)는 음식 메뉴 추천 룰렛 뽑기 시뮬레이터입니다. 저장소는 [Bwaaab/eum-mae](https://github.com/Bwaaab/eum-mae)입니다.

품질 검사와 리뷰 기준은 다음 문서를 따른다.

- [팀 약속](docs/team-agreement.md)
- [CI 파이프라인](docs/ci-pipeline.md)
- [코드 품질 유지](docs/maintaining_code_quality.md)
- [라이선스](LICENSE)

---

## 1. 준비

1. Python 3.12 이상을 설치한다
2. 저장소를 클론한다
3. `pip install -r requirements.txt`
4. `streamlit run app.py`로 실행을 확인한다

---

## 2. 역할과 소통

| 이름 | 역할 | GitHub | 담당 기능 |
|---|---|---|---|
| 석혜인 | 팀장 | @bwaaab | 이펙트 |
| 장산 | 개발 리드 | @Banlru2 | 룰렛/카드, 공통 |
| 이규민 | 리뷰·품질 담당 | @schere02 | 리스트 |
| 김가연 | 문서 담당 | @yabi1 | 결과창 |

- 채널: 카카오톡 채팅방 '음메'
- 정기 회의: 매주 월요일 18:30~19:30, 온라인. 불참은 전날까지 알린다
- 응답: 채팅 24시간, 풀 리퀘스트 리뷰 48시간
- 작업 전 이슈를 등록하고, 하루 작업이 끝나면 본인 원격 브랜치에 Push한다

---

## 3. 브랜치

GitHub Flow로 운영한다. `main`은 항상 실행 가능한 상태를 유지하고, 직접 푸시하지 않는다. 브랜치는 작업 시작 전 최신 `main`에서 나누며, 수명은 1주 이내를 권장한다.

| 브랜치 | 용도 | 예 |
|---|---|---|
| `main` | 시연 가능한 안정 버전. `v1.0.0` 태그 | — |
| `feature/이슈번호-기능명` | 기능 개발 | `feature/3-menu-list`, `feature/5-draw-engine` |
| `fix/이슈번호-버그명` | 버그 수정 | `fix/12-empty-list` |
| `docs/이슈번호-문서명` | 회의록, 가이드 | `docs/1-team-agreement` |

브랜치와 커밋 타입을 맞춘다. `feature/…`의 커밋은 `feat`, `fix/…`는 `fix`, `docs/…`는 `docs`다.

`main.py`와 공유 코드를 바꿀 때는 이슈 댓글로 먼저 알린다.

---

## 4. 이슈

코딩과 문서 작업은 시작 전에 이슈를 등록한다. 빈 이슈는 열지 않는다. 템플릿은 `.github/ISSUE_TEMPLATE/`에 있고, 제목 접두사와 같은 라벨이 붙는다.

| 파일 | 제목 접두사 | 용도 |
|---|---|---|
| `enhancement.yml` | `[enhancement]:` | 새 기능 개발 및 UI/UX 개선 |
| `bug.yml` | `[bug]:` | 프로그램 실행 오류 및 예외 상황 수정 |
| `documentation.yml` | `[documentation]:` | 회의록, 안내서, README 등 문서화 작업 |
| `question.yml` | `[question]:` | 기술적 문제 및 팀원·교수님 질의 |
| `good-first-issue.yml` | `[good first issue]:` | 11주차 타 팀 기여용. 타 팀이 풀 수 있는 이슈를 2개 이상 남긴다 |

`question`은 PR을 열지 않고 이슈에서 답한다.

---

## 5. 풀 리퀘스트와 리뷰

PR은 `.github/pull_request_template.md` 하나다. 한 PR에는 한 가지 목적만 담는다.

채울 항목은 요약, 변경 종류, 관련 이슈, 변경 내용, 확인 방법, 테스트 계획, 리뷰어 참고다.

- 버그 이슈는 `Fixes #이슈번호`
- 기능 이슈는 `Closes #이슈번호`
- 화면이 바뀌면 스크린샷과 확인 절차를 남긴다
- 리뷰를 요청하기 전에 테스트 계획을 채운다. 린트·테스트가 있으면 통과시켜 둔다

작성자는 자신의 PR을 혼자 승인하지 않는다. 리뷰는 48시간 안에 응답한다.

리뷰·품질 담당이 확인하는 항목은 다음과 같다.

1. 관련 이슈가 `Fixes #` 또는 `Closes #`로 연결되어 있는가
2. 변경 종류가 실제 수정 내용과 맞는가
3. 확인 방법으로 제3자가 재현할 수 있는가
4. 인접 기능(리스트, 룰렛, 결과창, 이펙트)을 확인했는가
5. 공통 파일 변경 시 이슈에 사전 공유가 있는가
6. CI가 구성되어 있으면 통과했는가

리뷰어는 브랜치를 받아 `streamlit run app.py` 실행과 PEP 8을 확인한다. 빈 목록, 항목 1개, 새로고침처럼 빠지기 쉬운 경우도 본다. 로컬 경로나 비밀 값 없이도 실행되어야 한다.

CI가 실패하면 그 오류를 고친 뒤에 리뷰를 끝낸다. 검사 단계와 한계는 CI 파이프라인 문서를 따른다.

리뷰가 승인되고, CI가 있으면 그 검사까지 통과한 뒤에 개발 리드가 `main`에 병합한다.

---

## 6. 커밋 메시지

```
타입(범위): 변경 요약
```

커밋 하나에는 변경 하나만 담고, 한글로 적는다.

| 타입 | 의미 | 예 |
|---|---|---|
| `feat` | 새 기능 | `feat(list): 메뉴 삭제 추가` |
| `fix` | 버그 수정 | `fix(roulette): 빈 목록에서 크래시` |
| `refactor` | 동작은 같고 구조만 정리 | `refactor(result): 상태 분리` |
| `docs` | 문서만 | `docs: 기여 가이드 정리` |
| `test` | 테스트만 | `test(list): 중복 메뉴 케이스` |
| `chore` | 도구, 의존성, CI | `chore: lint 설정 추가` |

범위는 `list`, `roulette`, `result`, `effects`다. 공통 코드는 `common`을 쓰거나 범위를 생략한다.

---

## 7. 코드와 산출물

- PEP 8을 따른다
- 기능마다 파일 하나다. `modules/`에 두고, 한 사람이 한 파일을 맡는다
- 파일 입출력은 `encoding="utf-8"`을 사용한다
- 새 라이브러리는 `requirements.txt`에 추가한다
- 토큰, 비밀번호, 개인정보, 로컬 전용 경로는 올리지 않는다
- AI로 작성한 코드는 직접 실행해 확인한 것만 올리고, PR에 사용 여부를 적는다

| 경로 | 내용 |
|---|---|
| `app.py`, `requirements.txt` | 실행 진입점과 의존성 |
| `modules/` | 기능별 파이썬 파일 |
| `docs/team-agreement.md` | 팀 약속 |
| `docs/ci-pipeline.md` | CI 파이프라인 |
| `docs/maintaining_code_quality.md` | 코드 품질 유지 |
| `docs/meetings/YYYY-MM-DD.md` | 주간 회의록 |
| `LICENSE` | 라이선스 |

라이선스는 MIT다. 행동 수칙은 `CODE_OF_CONDUCT.md`를 따른다.

---

## 8. 외부 기여자 (11주차~)

1. `good first issue`에 댓글로 배정을 요청하고, 지정된 뒤에 시작한다
2. 이 저장소를 Fork한 뒤 브랜치를 만든다
3. base를 이 저장소의 `main`으로 PR을 연다
4. 이슈·PR 템플릿, 커밋 규칙, 리뷰 기한(48시간)은 팀원과 같다
