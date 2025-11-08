# 📊 Markdown 표 및 차트 렌더링 가이드

## ✅ 완료된 개선사항

### 1. Markdown 표 렌더링 개선

**문제**: Markdown 표가 텍스트로 표시되어 읽기 어려움

**해결**:
- `remark-gfm` 플러그인 추가: GitHub Flavored Markdown 지원
- `rehype-raw` 플러그인 추가: HTML 태그 지원
- MUI Table 컴포넌트로 자동 변환

**설치된 패키지**:
```bash
npm install remark-gfm rehype-raw
```

**적용된 코드** (`frontend/src/components/Chat/MessageBubble.jsx`):
```javascript
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

<ReactMarkdown
  remarkPlugins={[remarkGfm]}
  rehypePlugins={[rehypeRaw]}
  components={{
    table: ({ node, ...props }) => (
      <TableContainer component={Paper} sx={{ my: 2, maxWidth: '100%', overflowX: 'auto' }}>
        <Table size="small" {...props} />
      </TableContainer>
    ),
    thead: ({ node, ...props }) => <TableHead {...props} />,
    tbody: ({ node, ...props }) => <TableBody {...props} />,
    tr: ({ node, ...props }) => <TableRow {...props} />,
    th: ({ node, ...props }) => (
      <TableCell
        sx={{
          fontWeight: 'bold',
          bgcolor: 'action.hover',
          borderBottom: '2px solid',
          borderColor: 'divider'
        }}
        {...props}
      />
    ),
    td: ({ node, ...props }) => (
      <TableCell
        sx={{
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
        {...props}
      />
    ),
  }}
>
  {contentWithoutJsonBlocks}
</ReactMarkdown>
```

**결과**:
- ✅ Markdown 표가 MUI Table로 자동 변환
- ✅ 헤더 행 강조 (배경색, 굵은 글씨)
- ✅ 깔끔한 테두리
- ✅ 반응형 (작은 화면에서 가로 스크롤)
- ✅ 이쁜 디자인

### 2. 실제 LLM이 표와 차트를 생성하도록 시스템 프롬프트 개선

**변경 파일**: `backend/app/agents/nodes.py`

**개선된 시스템 프롬프트**:
```python
system_prompt = """
당신은 반도체 부품 전문 챗봇입니다.

중요 규칙:
1. 반드시 제공된 문서와 데이터만 참조하여 답변하세요.
2. 확실하지 않으면 "정보가 부족합니다"라고 답변하세요.
3. 모든 답변에 출처를 명시하세요.
4. 표나 그래프로 표현할 수 있는 내용은 반드시 다음 형식을 사용하세요:

   **표 (Markdown Table):**
   | 컬럼1 | 컬럼2 | 컬럼3 |
   |-------|-------|-------|
   | 값1   | 값2   | 값3   |

   **그래프 (JSON Code Block):**
   ```json
   {
     "type": "line" 또는 "bar" 또는 "pie",
     "title": "그래프 제목",
     "data": {
       "labels": ["라벨1", "라벨2", ...],
       "datasets": [{
         "label": "데이터셋 이름",
         "data": [값1, 값2, ...],
         "borderColor": "rgba(75, 192, 192, 1)",
         "backgroundColor": "rgba(75, 192, 192, 0.2)"
       }]
     }
   }
   ```

5. 시계열 데이터나 추이는 Line Chart로, 비교는 Bar Chart로, 비율/구성은 Pie Chart로 표현하세요.
6. Hallucination을 절대 하지 마세요.

예시 답변:

부품 ABC-12345의 최근 3개월 출고 현황은 다음과 같습니다.

| 월 | 출고량 | 누적 출고량 |
|----|--------|-------------|
| 1월 | 120개 | 120개 |
| 2월 | 150개 | 270개 |
| 3월 | 180개 | 450개 |

```json
{
  "type": "line",
  "title": "월별 출고 추이",
  "data": {
    "labels": ["1월", "2월", "3월"],
    "datasets": [{
      "label": "출고량 (개)",
      "data": [120, 150, 180],
      "borderColor": "rgba(75, 192, 192, 1)",
      "backgroundColor": "rgba(75, 192, 192, 0.2)",
      "tension": 0.4
    }]
  }
}
```

총 450개가 출고되었으며, 매월 증가 추세를 보이고 있습니다.

**출처**: [부품 관리 시스템 - 출고 이력 DB]
"""
```

### 3. 포트 변경 (macOS AirPlay Receiver 충돌 해결)

**변경된 포트**:
- Backend: 5000 → **5001**
- Frontend: 3000 (유지)

**변경된 파일**:
1. `backend/.env`: `FLASK_PORT=5001`
2. `frontend/vite.config.js`: `target: 'http://localhost:5001'`
3. `start_test.sh`: 출력 메시지 업데이트

---

## 🎯 LLM이 표와 차트를 그리는 방법

### 범용성 여부

**Yes, 완전히 범용적입니다!**

이 방식은 다음과 같은 이유로 범용적으로 사용됩니다:

1. **업계 표준 포맷**:
   - Markdown 표: GitHub, Slack, Discord 등 모든 플랫폼에서 지원
   - JSON 차트 데이터: Chart.js, Recharts, D3.js 등 모든 차트 라이브러리와 호환

2. **LLM 친화적**:
   - OpenAI GPT-4, Claude, Llama 등 모든 주요 LLM이 Markdown과 JSON을 자연스럽게 생성
   - 구조화된 출력(Structured Output)을 쉽게 생성

3. **확장 가능성**:
   - 새로운 차트 타입 추가 용이
   - 커스텀 스타일링 가능
   - 다양한 데이터 형식 지원

### 실제 LLM이 표와 차트를 생성하는 과정

#### Step 1: 사용자 질문
```
"최근 3개월 출고 데이터를 표와 그래프로 보여줘"
```

#### Step 2: LLM이 시스템 프롬프트를 참고하여 응답 생성

시스템 프롬프트에 명시된 형식대로 답변:

```markdown
부품 ABC-12345의 최근 3개월 출고 현황입니다.

| 월 | 출고량 | 전월 대비 |
|----|--------|-----------|
| 1월 | 120개 | - |
| 2월 | 150개 | +25% |
| 3월 | 180개 | +20% |

\`\`\`json
{
  "type": "line",
  "title": "월별 출고 추이",
  "data": {
    "labels": ["1월", "2월", "3월"],
    "datasets": [{
      "label": "출고량 (개)",
      "data": [120, 150, 180],
      "borderColor": "rgba(75, 192, 192, 1)",
      "backgroundColor": "rgba(75, 192, 192, 0.2)",
      "tension": 0.4
    }]
  }
}
\`\`\`

총 450개가 출고되었으며, 지속적인 증가 추세입니다.

**출처**: [출고 이력 DB - 2024년 1-3월]
```

#### Step 3: 프론트엔드 파싱 및 렌더링

`MessageBubble.jsx`에서:

1. **JSON 블록 추출**:
```javascript
const jsonBlockRegex = /```json\s*\n([\s\S]*?)\n```/g;
while ((match = jsonBlockRegex.exec(message.content)) !== null) {
  const jsonData = JSON.parse(match[1]);
  if (jsonData.type && jsonData.data) {
    charts.push(jsonData);
  }
}
```

2. **Markdown 표 렌더링**:
```javascript
<ReactMarkdown
  remarkPlugins={[remarkGfm]}
  components={{
    table: ({ node, ...props }) => (
      <TableContainer component={Paper}>
        <Table {...props} />
      </TableContainer>
    ),
    // ... th, td 등
  }}
>
  {contentWithoutJsonBlocks}
</ReactMarkdown>
```

3. **차트 렌더링**:
```javascript
{parsedCharts.map((chart, idx) => (
  <ResponsiveContainer width="100%" height={350}>
    <LineChart data={chartDataFormatted}>
      {/* ... */}
    </LineChart>
  </ResponsiveContainer>
))}
```

---

## 📊 지원되는 차트 타입

### 1. Line Chart (선 그래프)
**용도**: 시계열 데이터, 추이, 트렌드

```json
{
  "type": "line",
  "title": "월별 출고 추이",
  "data": {
    "labels": ["1월", "2월", "3월", "4월"],
    "datasets": [{
      "label": "2024년",
      "data": [120, 150, 180, 200],
      "borderColor": "rgba(75, 192, 192, 1)",
      "backgroundColor": "rgba(75, 192, 192, 0.2)",
      "tension": 0.4
    }]
  }
}
```

### 2. Bar Chart (막대 그래프)
**용도**: 비교, 순위, 카테고리별 데이터

```json
{
  "type": "bar",
  "title": "라인별 생산량 비교",
  "data": {
    "labels": ["라인 1", "라인 2", "라인 3"],
    "datasets": [{
      "label": "생산량 (개)",
      "data": [500, 450, 380],
      "backgroundColor": [
        "rgba(255, 99, 132, 0.6)",
        "rgba(54, 162, 235, 0.6)",
        "rgba(255, 206, 86, 0.6)"
      ]
    }]
  }
}
```

### 3. Pie Chart (파이 차트)
**용도**: 비율, 구성, 분포

```json
{
  "type": "pie",
  "title": "불량 유형별 비율",
  "data": {
    "labels": ["스크래치", "불량 접착", "오염", "기타"],
    "datasets": [{
      "data": [40, 30, 20, 10],
      "backgroundColor": [
        "#FF6384",
        "#36A2EB",
        "#FFCE56",
        "#4BC0C0"
      ]
    }]
  }
}
```

### 4. 다중 데이터셋 지원

```json
{
  "type": "line",
  "title": "연도별 출고 추이 비교",
  "data": {
    "labels": ["1월", "2월", "3월", "4월"],
    "datasets": [
      {
        "label": "2023년",
        "data": [100, 120, 140, 160],
        "borderColor": "rgba(75, 192, 192, 1)"
      },
      {
        "label": "2024년",
        "data": [120, 150, 180, 200],
        "borderColor": "rgba(255, 99, 132, 1)"
      }
    ]
  }
}
```

---

## 🎨 스타일 커스터마이징

### 표 스타일

```javascript
components={{
  th: ({ node, ...props }) => (
    <TableCell
      sx={{
        fontWeight: 'bold',
        bgcolor: 'action.hover',      // 헤더 배경색
        borderBottom: '2px solid',     // 두꺼운 하단 테두리
        borderColor: 'divider',
        fontSize: '0.9rem',            // 글자 크기
        padding: '12px 16px'           // 여백
      }}
      {...props}
    />
  ),
}}
```

### 차트 스타일

```javascript
<Box sx={{
  my: 3,                              // 상하 여백
  p: 2,                               // 내부 여백
  bgcolor: 'background.default',      // 배경색
  borderRadius: 2                     // 둥근 모서리
}}>
  <Typography variant="h6" gutterBottom sx={{
    fontWeight: 'bold',
    color: 'primary.main'             // 제목 색상
  }}>
    {title}
  </Typography>
  <ResponsiveContainer width="100%" height={350}>
    {/* Chart Component */}
  </ResponsiveContainer>
</Box>
```

---

## 🚀 테스트 방법

### 1. 서버 실행
```bash
./start_test.sh
```

### 2. 브라우저에서 테스트

**URL**: http://localhost:3000

**테스트 질문**:
```
최근 3개월 출고 데이터를 표와 그래프로 보여줘
```

**예상 결과**:
- ✅ 깔끔한 MUI 표로 렌더링
- ✅ 반응형 Line 차트
- ✅ JSON 텍스트는 표시되지 않음

### 3. 예시 대화 확인

사이드바에서 **"2021-2023 출고 데이터 분석"** 클릭:
- ✅ 12개월 x 3년 데이터 표
- ✅ Line 차트 (월별 추이)
- ✅ Bar 차트 (연도별 총량)
- ✅ Pie 차트 (라인별 비율)

---

## 💡 실제 환경에서 사용하기

### OpenAI API와 함께 사용

**TEST_MODE=False**로 설정하면 실제 LLM 사용:

```bash
# backend/.env
TEST_MODE=False
LLM_CHAT_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=sk-your-api-key
LLM_CHAT_MODEL=gpt-4
```

**LLM이 자동으로 다음과 같이 응답**:
1. 데이터베이스에서 정보 검색
2. Markdown 표 형식으로 정리
3. JSON 차트 데이터 생성
4. 텍스트 설명 추가

### 다른 LLM과 함께 사용

**Claude, Llama, 사내 LLM 등 모두 지원**:

```python
# backend/app/services/llm_service.py
class RealChatLLM:
    def __init__(self, model: str, temperature: float = 0.1):
        self.llm = ChatOpenAI(
            base_url=config.llm.chat_url,  # 사내 LLM URL
            api_key=config.llm.api_key,
            model=model,
            temperature=temperature
        )
```

---

## 🔍 문제 해결

### 표가 여전히 이쁘지 않은 경우

1. **브라우저 캐시 삭제**:
   - Cmd + Shift + R (Mac)
   - Ctrl + Shift + R (Windows/Linux)

2. **의존성 재설치**:
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

3. **패키지 확인**:
```bash
npm list remark-gfm rehype-raw
```

### 차트가 표시되지 않는 경우

1. **JSON 형식 확인**: 브라우저 콘솔(F12)에서 파싱 오류 확인
2. **차트 타입 확인**: "line", "bar", "pie" 중 하나여야 함
3. **데이터 형식 확인**: labels와 datasets 배열이 올바른지 확인

---

## 📚 관련 문서

- **CHART_FIX_SUMMARY.md**: 차트 렌더링 수정 내역
- **VISUALIZATION_DEMO_GUIDE.md**: 시각화 데모 가이드
- **CHART_RENDERING_STATUS.md**: 전체 상태 요약
- **TESTING_GUIDE.md**: 종합 테스트 가이드

---

## ✨ 정리

### 질문 1: Markdown 표가 이쁘지 않은 문제
**답변**: ✅ **해결 완료!**
- `remark-gfm` 플러그인 추가
- MUI Table 컴포넌트로 자동 변환
- 깔끔한 헤더 스타일, 테두리, 반응형 지원

### 질문 2: JSON을 차트로 만드는 기능이 범용적인가?
**답변**: ✅ **Yes, 완전히 범용적!**
- 모든 주요 LLM이 Markdown과 JSON을 자연스럽게 생성
- Chart.js, Recharts, D3.js 등 모든 차트 라이브러리와 호환
- 업계 표준 포맷 사용

### 질문 3: 실제 LLM이 Mock처럼 표와 차트를 그릴 수 있나?
**답변**: ✅ **Yes, 가능!**
- 시스템 프롬프트에 형식과 예시 제공
- LLM이 프롬프트를 따라 Markdown 표와 JSON 차트 생성
- OpenAI GPT-4, Claude, Llama 등 모든 LLM 지원
- 실제 데이터베이스 쿼리 결과를 기반으로 자동 생성

**모든 준비 완료!** 🎉
