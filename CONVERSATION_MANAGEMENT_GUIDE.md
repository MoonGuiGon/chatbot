# 📚 대화 이력 관리 가이드

## 🎯 개요

대화 이력 관리 시스템은 사용자의 모든 대화를 저장하고, 편리하게 관리할 수 있는 기능을 제공합니다.

---

## ✨ 주요 기능

### 1. **자동 대화 생성 및 추가**
- 새 대화 버튼 클릭 시 자동으로 대화 생성
- 생성된 대화가 즉시 사이드바에 표시
- 기본 제목: "새 대화"

### 2. **자동 제목 생성**
- 첫 번째 메시지 전송 후 자동으로 제목 생성
- LLM이 대화 내용을 분석하여 의미있는 제목 생성
- 30자 이내로 간결하게 생성

### 3. **제목 수정**
- 각 대화의 제목을 언제든지 수정 가능
- ✏️ 편집 아이콘 클릭 → 제목 입력 → ✓ 저장
- Enter 키로 빠른 저장 가능

### 4. **대화 삭제**
- 🗑️ 삭제 아이콘으로 불필요한 대화 제거
- 확인 대화창으로 실수 방지
- 삭제된 대화는 복구 불가

### 5. **대화 이력 조회**
- 모든 대화가 시간순으로 정렬
- 대화 클릭으로 이전 대화 내용 불러오기
- 날짜 정보와 함께 표시

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 인터페이스                           │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  새 대화 버튼    │  │  대화 이력 목록  │                   │
│  │  - 대화 생성     │  │  - 제목 표시     │                   │
│  └─────────────────┘  │  - 편집 아이콘   │                   │
│                       │  - 삭제 아이콘   │                   │
│                       └─────────────────┘                   │
└───────────────────────────┬─────────────────────────────────┘
                            │ API 호출
┌───────────────────────────▼─────────────────────────────────┐
│                      Flask Backend                            │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │             대화 관리 엔드포인트                        │   │
│  │  - POST   /conversations         새 대화 생성         │   │
│  │  - GET    /conversations         대화 목록 조회       │   │
│  │  - DELETE /conversations/:id     대화 삭제           │   │
│  │  - PUT    /conversations/:id/title  제목 수정        │   │
│  │  - POST   /conversations/:id/generate-title          │   │
│  │           자동 제목 생성                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                  │
│  ┌──────────────────────────▼──────────────────────────┐    │
│  │            제목 생성 로직 (LLM)                       │    │
│  │  - 대화 내용 분석 (처음 3턴)                          │    │
│  │  - 핵심 키워드 추출                                   │    │
│  │  - 간결한 제목 생성 (30자 이내)                       │    │
│  └──────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      MongoDB                                  │
│                                                               │
│  conversations 컬렉션:                                         │
│  {                                                            │
│    conversation_id: "conv_abc123",                            │
│    user_id: "user_demo",                                      │
│    title: "부품 ABC-12345 재고 조회",                          │
│    messages: [                                                │
│      {role: "user", content: "...", timestamp: ...},          │
│      {role: "assistant", content: "...", timestamp: ...}      │
│    ],                                                         │
│    created_at: ISODate(),                                     │
│    updated_at: ISODate()                                      │
│  }                                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 제목 생성 로직 상세

### 제목 생성 전략

```python
def generate_title(messages: List[Dict]) -> str:
    """
    대화 내용 기반 제목 자동 생성

    전략:
    1. 첫 메시지가 30자 이내 → 그대로 사용
    2. 첫 메시지가 긴 경우 → LLM으로 요약
    3. 여러 메시지 분석 → 핵심 주제 추출
    """

    # 1단계: 첫 사용자 메시지 추출
    first_user_message = extract_first_user_message(messages)

    # 2단계: 간단한 경우 처리
    if len(first_user_message) <= 30:
        return first_user_message

    # 3단계: LLM으로 제목 생성
    context = create_context(messages[:6])  # 최대 3턴

    prompt = f"""
    다음 대화의 핵심 주제를 30자 이내의 간결한 제목으로 만들어주세요.

    대화 내용:
    {context}

    제목 생성 규칙:
    - 30자 이내로 간결하게
    - 핵심 키워드 포함 (부품 번호, 작업 내용 등)
    - 의문형이 아닌 명사형으로
    - 특수문자 사용 안함

    예시:
    - "부품 ABC-12345 재고 조회"
    - "라인 1 검사 이력 확인"
    - "출고 현황 분석"

    제목:
    """

    title = llm.invoke(prompt)
    return sanitize_title(title)
```

### 제목 생성 예시

| 대화 내용 | 생성된 제목 |
|----------|------------|
| "부품 ABC-12345의 재고는?" | "부품 ABC-12345 재고 조회" |
| "라인 1에서 사용하는 반도체 칩의 검사 이력을 확인하고 싶어" | "라인 1 반도체 칩 검사 이력" |
| "최근 한 달간 출고 현황을 표로 보여주고, 그래프도 만들어줘" | "최근 한달 출고 현황 분석" |
| "부품 검사 절차가 뭐야?" | "부품 검사 절차가 뭐야?" (30자 이내, 그대로 사용) |

### 제목 정제 규칙

```python
def sanitize_title(title: str) -> str:
    """제목 정제"""
    # 따옴표 제거
    title = title.replace('"', '').replace("'", '')

    # 양쪽 공백 제거
    title = title.strip()

    # 30자 제한
    if len(title) > 30:
        title = title[:27] + "..."

    return title
```

---

## 📡 API 엔드포인트

### 1. 새 대화 생성

```http
POST /api/conversations
Content-Type: application/json

{
  "user_id": "user_demo"
}
```

**응답:**
```json
{
  "success": true,
  "conversation_id": "conv_abc123xyz",
  "title": "새 대화"
}
```

### 2. 대화 목록 조회

```http
GET /api/conversations?user_id=user_demo
```

**응답:**
```json
{
  "success": true,
  "conversations": [
    {
      "conversation_id": "conv_001",
      "title": "부품 ABC-12345 재고 조회",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:35:00Z",
      "message_count": 6
    },
    ...
  ]
}
```

### 3. 대화 삭제

```http
DELETE /api/conversations/conv_abc123xyz
```

**응답:**
```json
{
  "success": true,
  "message": "대화가 삭제되었습니다."
}
```

### 4. 제목 수정

```http
PUT /api/conversations/conv_abc123xyz/title
Content-Type: application/json

{
  "title": "부품 재고 현황 확인"
}
```

**응답:**
```json
{
  "success": true,
  "title": "부품 재고 현황 확인"
}
```

### 5. 제목 자동 생성

```http
POST /api/conversations/conv_abc123xyz/generate-title
```

**응답:**
```json
{
  "success": true,
  "title": "부품 ABC-12345 재고 조회"
}
```

---

## 🎨 UI/UX 상세

### 사이드바 레이아웃

```
┌─────────────────────────────┐
│  [+] 새 대화                 │
├─────────────────────────────┤
│  대화 이력                   │
├─────────────────────────────┤
│  💬 부품 ABC-12345 재고... ✏️🗑️│
│     2024-01-15              │
├─────────────────────────────┤
│  💬 라인 1 검사 이력 확인   ✏️🗑️│
│     2024-01-14              │
├─────────────────────────────┤
│  💬 출고 현황 분석          ✏️🗑️│
│     2024-01-13              │
└─────────────────────────────┘
```

### 제목 편집 모드

```
┌─────────────────────────────┐
│  [입력창: 부품 재고 확인]  ✓  ✕│
│     2024-01-15              │
└─────────────────────────────┘
```

### 인터랙션

1. **대화 클릭**: 해당 대화 로드
2. **✏️ 편집**: 제목 편집 모드 활성화
3. **✓ 저장**: 새 제목 저장
4. **✕ 취소**: 편집 취소
5. **🗑️ 삭제**: 확인 후 대화 삭제
6. **Enter 키**: 제목 편집 중 Enter로 저장

---

## 🧪 테스트 시나리오

### 시나리오 1: 새 대화 생성 및 자동 제목

1. "새 대화" 버튼 클릭
2. ✅ 사이드바에 "새 대화" 항목 추가됨
3. "부품 ABC-12345의 재고는?" 질문
4. 봇 응답 후 제목 자동 업데이트
5. ✅ "부품 ABC-12345 재고 조회"로 제목 변경됨

### 시나리오 2: 제목 수동 수정

1. 대화 이력에서 ✏️ 편집 아이콘 클릭
2. 제목 입력창에 "재고 확인 - 긴급" 입력
3. ✓ 클릭 또는 Enter
4. ✅ 제목이 "재고 확인 - 긴급"으로 변경됨
5. ✅ 서버에 저장됨

### 시나리오 3: 대화 삭제

1. 대화 이력에서 🗑️ 삭제 아이콘 클릭
2. 확인 대화창: "이 대화를 삭제하시겠습니까?"
3. "확인" 클릭
4. ✅ 사이드바에서 항목 제거됨
5. ✅ DB에서 대화 삭제됨

### 시나리오 4: 대화 로드

1. 사이드바에서 이전 대화 클릭
2. ✅ 채팅 영역에 이전 메시지들 표시
3. ✅ 대화 이어서 진행 가능

### 시나리오 5: 제목 편집 취소

1. ✏️ 편집 아이콘 클릭
2. 제목 일부 수정
3. ✕ 취소 아이콘 클릭
4. ✅ 원래 제목으로 복원됨

---

## 🔍 주요 구현 포인트

### 1. 상태 관리

```javascript
// App.jsx
const [conversationHistory, setConversationHistory] = useState([]);
const [editingConvId, setEditingConvId] = useState(null);
const [editTitle, setEditTitle] = useState('');

// 대화 이력 업데이트
setConversationHistory(prev => [newConv, ...prev]);

// 제목 업데이트
setConversationHistory(prev =>
  prev.map(conv =>
    conv.id === convId ? { ...conv, title: newTitle } : conv
  )
);
```

### 2. 이벤트 전파 방지

```javascript
// 삭제/편집 버튼 클릭 시 대화 로드 방지
const handleDeleteConversation = async (convId, event) => {
  event.stopPropagation(); // 중요!
  // ... 삭제 로직
};
```

### 3. 자동 제목 생성 타이밍

```javascript
// 첫 메시지 후 자동 생성
if (len(messages) == 2 && conversation.get("title") == "새 대화"):
    title = generate_title(messages)
    mongodb.update_one(...)
```

### 4. 제목 입력 최적화

```javascript
// Enter 키로 저장
onKeyPress={(e) => {
  if (e.key === 'Enter') {
    handleSaveTitle(conversation.id, e);
  }
}}
```

---

## 📊 데이터베이스 스키마

### conversations 컬렉션

```json
{
  "_id": ObjectId("..."),
  "conversation_id": "conv_abc123xyz",
  "user_id": "user_demo",
  "title": "부품 ABC-12345 재고 조회",
  "messages": [
    {
      "role": "user",
      "content": "부품 ABC-12345의 재고는?",
      "timestamp": ISODate("2024-01-15T10:30:00Z")
    },
    {
      "role": "assistant",
      "content": "부품 ABC-12345의 현재 재고는...",
      "sources": [...],
      "confidence_score": 0.95,
      "timestamp": ISODate("2024-01-15T10:30:15Z")
    }
  ],
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "updated_at": ISODate("2024-01-15T10:35:00Z")
}
```

### 인덱스

```javascript
// 빠른 조회를 위한 인덱스
db.conversations.createIndex({ "user_id": 1, "updated_at": -1 });
db.conversations.createIndex({ "conversation_id": 1 });
```

---

## 🚨 에러 핸들링

### 1. 제목 생성 실패

```python
try:
    title = llm.invoke(prompt)
except Exception as e:
    print(f"제목 생성 오류: {e}")
    # 폴백: 첫 메시지 사용
    title = first_user_message[:27] + "..."
```

### 2. API 호출 실패

```javascript
try {
  const result = await chatAPI.deleteConversation(convId);
  if (result.success) {
    setConversationHistory(prev => prev.filter(conv => conv.id !== convId));
  }
} catch (error) {
  console.error('대화 삭제 오류:', error);
  alert('대화 삭제 중 오류가 발생했습니다.');
}
```

### 3. 빈 제목 방지

```javascript
if (!editTitle.trim()) {
  return; // 빈 제목은 저장 안함
}
```

---

## 💡 개선 아이디어

### 단기 개선

- [ ] 대화 검색 기능 (제목/내용)
- [ ] 대화 폴더/카테고리 분류
- [ ] 대화 즐겨찾기 (북마크)
- [ ] 대화 내보내기 (PDF, TXT)

### 중기 개선

- [ ] 대화 공유 링크 생성
- [ ] 대화 복사 (템플릿으로 활용)
- [ ] 대화 병합 기능
- [ ] 자동 태그 생성 (#재고 #검사 등)

### 장기 개선

- [ ] 대화 분석 대시보드
- [ ] 관련 대화 추천
- [ ] 대화 요약 자동 생성
- [ ] 시간대별 대화 통계

---

## 🎓 모범 사례

### DO ✅

- 제목은 명사형으로 간결하게
- 핵심 키워드 포함 (부품 번호, 작업 등)
- 30자 이내로 제한
- 의미있는 제목 사용

### DON'T ❌

- 의문형 제목 사용 ("재고가 얼마나 있나요?")
- 너무 긴 제목 (50자 이상)
- 특수문자 남용 (#!@$%)
- 모호한 제목 ("질문", "확인")

---

## 📚 관련 문서

- **ARCHITECTURE.md**: 전체 시스템 아키텍처
- **MEMORY_GUIDE.md**: 메모리 시스템 가이드
- **TESTING_GUIDE.md**: 테스트 가이드
- **API_REFERENCE.md**: API 레퍼런스

---

**대화 이력 관리로 더 효율적인 업무!** 📚✨
