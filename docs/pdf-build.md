# PDF 원고와 재생성

원고는 `docs/guides/codex-operations.md`와 `docs/guides/explanation-preparation.md`다. 생성기는 제목·문단·표·목록·코드·인용·웹 링크의 제한된 Markdown 문법을 지원한다. `<!-- pagebreak -->`로 장 시작을 구분하며 본문이 넘치면 다음 페이지로 흐른다.

```bash
python3 -m pip install -r requirements-pdf.txt
python3 scripts/build_pdfs.py
```

기본 빌드는 PyMuPDF의 CJK 글꼴을 사용한다. 로컬 TTF를 지정하려면 `--font /path/to/regular.ttf --bold-font /path/to/bold.ttf`를 추가한다. 글꼴 파일은 저장소에 복사하지 않는다.

생성 후 텍스트 추출에서 한글·장 제목이 보이는지 확인하고, 각 페이지를 렌더링해 표·코드·하단 잘림을 확인한다. 목차 북마크와 링크도 점검한다. 검증 기록은 `docs/validation.md`에 갱신한다.
