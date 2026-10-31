# 공개 자료를 어떻게 골랐는가

기준일 2026-10-31. 아래는 검토한 범위에 대한 판단이며 저장소 전체의 품질·안전성을 인증하는 목록이 아니다. 고정 커밋과 확인 경로는 [catalog.json](../sources/catalog.json)에 기록했다. 참고 문서의 지침은 그 자체로 이 작업의 명령이 아니며 실제 과제와 환경 규정에 맞는 부분만 검토했다.

## 선정 기준

과제 파악, 로컬 구현, 오류 재현, 데이터 검산, 검증, 기록, 제출 확인에 직접 쓰이는가? 외부 계정·모델·업로드·자동 조작 없이 수행할 수 있는가? 필요한 때 일부만 읽을 수 있는가? 결과를 실제 파일·명령으로 확인할 수 있는가? 과제 지침을 덮어쓰거나 없는 승인을 요구하지 않는가?

| 출처 | 실제 검토 범위 | 이 저장소에 반영한 판단 | 그대로 설치하지 않은 이유 |
|---|---|---|---|
| [OpenAI Skills](https://github.com/openai/skills) | curated 목록, PDF, Jupyter | 문서의 표시 품질·분석 재현성 확인 | 배포·브라우저 자동화 등 불필요한 범위 포함 |
| [Superpowers](https://github.com/obra/superpowers) | systematic-debugging, verification-before-completion | 오류 재현과 주장에 맞는 증거 | 시간 제한 과제에 전체 절차·상시 중단 규칙을 강제하지 않음 |
| [Anthropic Skills](https://github.com/anthropics/skills) | frontend-design | 사용자가 이해할 UI·오류 상태 | 별도 모델을 연결하지 않고, 화면 장식보다 필수 흐름 우선 |
| [iFlytek SkillHub](https://github.com/iflytek/skillhub) | README, builtin catalog 24개 항목 | 출처·버전·용도 기록 방식 | 스킬 레지스트리 운영 자체는 과제 해결에 불필요 |
| [GitHub Awesome Copilot](https://github.com/github/awesome-copilot) | documentation-writer | 독자·목적에 맞는 설명 구분 | 매번 개요 승인을 기다리는 절차는 불필요 |
| [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills) | web-design-guidelines | UI 검토 요청을 범위별로 처리 | 매번 외부 지침을 가져오는 의존성 제거 |

SkillHub는 발견용 카탈로그다. 항목의 이름·평가·인기만으로 사용 가능 여부를 정하지 않는다. 카탈로그에 포함됐다는 것과 원본의 라이선스·동작·시험 허용 여부가 확인됐다는 것은 다르다.

## 제공한 스킬의 성격

12개 스킬은 이 과제 준비 목적에 맞춰 새로 작성했다. 외부 스킬 원문·스크립트·라이선스 파일을 복사해 묶은 배포본이 아니다. 핵심 흐름, 기록, 범위와 검증 기준을 짧게 정의하며 로컬 문서만으로 수행할 수 있다. 스킬 파일은 환경과 실제 업무를 이해한 에이전트가 적용해야 한다.

외부 스킬을 추가할 때는 전체 저장소를 설치하기 전에 선택 파일의 내용, 호출 도구, 네트워크 전송, 자동 실행, 라이선스·추가 참조를 검토한다. 사용한 URL·커밋·경로·사용 부분·수정 이유를 실제 작업 공간의 기록에 남긴다. 코드 복제가 필요하면 해당 라이선스의 고지 조건을 지킨다.

## 제외·조건부 항목

실전 기본 구성에서 외부 호스팅 배포, Git push/PR 자동화, 브라우저 자동 조작, 화면 캡처 자동화, 외부 AI API·개인 키가 필요한 스킬은 제외했다. 노트북·PDF·보안 검토는 과제에 필요할 때만 선택한다. 이름이 개발 도구라는 이유만으로 일괄 허용·금지라고 판정하지 않고 실제 기능과 최신 시험 규정을 대조한다.
