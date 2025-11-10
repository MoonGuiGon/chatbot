# 🌊 Server-Sent Events (SSE) 스트리밍 구현 가이드

LLM 응답을 실시간으로 스트리밍하는 방법을 Backend와 Frontend 모두에서 완벽하게 구현하는 가이드입니다.

---

## 📋 목차

1. [개요](#개요)
2. [Backend 구현 (Flask + SSE)](#backend-구현)
3. [Frontend 구현 (React + EventSource)](#frontend-구현)
4. [예외 처리](#예외-처리)
5. [테스트 방법](#테스트-방법)
6. [문제 해결](#문제-해결)

---

## 개요

### 왜 스트리밍인가?

**기존 방식 (동기)**:
```
User → [질문] → Backend → [처리 중... 30초] → Response → User
                            ↑ 사용자는 기다림
```

**스트리밍 방식**:
```
User → [질문] → Backend → [단계1] → User (즉시 표시)
                        → [단계2] → User (즉시 표시)
                        → [단계3] → User (즉시 표시)
                        → [완료] → User
                            ↑ 실시간 피드백
```

### SSE vs WebSocket

| 특징 | SSE | WebSocket |
|------|-----|-----------|
| 방향 | 서버 → 클라이언트 (단방향) | 양방향 |
| 프로토콜 | HTTP | WebSocket 프로토콜 |
| 재연결 | 자동 | 수동 구현 필요 |
| 복잡도 | 낮음 | 높음 |
| 용도 | **LLM 스트리밍**, 알림 | 채팅, 게임 |

**결론**: LLM 스트리밍에는 SSE가 최적! ✅

---

## Backend 구현

### 1. Flask Route 설정

**파일**: `backend/app/routes/chat.py`

```python
from flask import Blueprint, request, Response
import json

bp = Blueprint("chat", __name__)

@bp.route("/chat/stream", methods=["POST"])
def chat_stream():
    """
    채팅 메시지 스트리밍 처리
    Server-Sent Events (SSE) 방식
    """
    data = request.get_json()

    message = data.get("message")
    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")
    custom_prompt = data.get("custom_prompt")
    llm_config = data.get("llm_config")

    # 필수 파라미터 검증
    if not message:
        return jsonify({
            "success": False,
            "error": "메시지가 필요합니다."
        }), 400

    def generate():
        """SSE 이벤트 스트림 생성"""
        try:
            agent = get_chatbot_agent()

            # LangGraph 에이전트 스트리밍
            for event in agent.stream(
                query=message,
                user_id=user_id,
                conversation_id=conversation_id,
                custom_prompt=custom_prompt,
                llm_config=llm_config
            ):
                # SSE 형식으로 이벤트 전송
                # 형식: "data: {JSON}\n\n"
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        except Exception as e:
            # 에러 이벤트 전송
            error_event = {
                "type": "error",
                "data": {
                    "error": str(e),
                    "message": "처리 중 오류가 발생했습니다."
                }
            }
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

    # SSE Response 반환
    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Nginx 버퍼링 비활성화
        }
    )
```

### 2. LangGraph Agent 스트리밍

**파일**: `backend/app/agents/chatbot_agent.py`

```python
from typing import Iterator, Dict, Any

class ChatbotAgent:
    def stream(
        self,
        query: str,
        user_id: str = None,
        conversation_id: str = None,
        custom_prompt: str = None,
        llm_config: Dict = None
    ) -> Iterator[Dict[str, Any]]:
        """
        스트리밍 방식으로 LangGraph 실행

        Yields:
            dict: 이벤트 데이터
            {
                "type": "progress|final|error",
                "data": { ... }
            }
        """
        try:
            # 초기 상태
            initial_state = {
                "query": query,
                "user_id": user_id or "default_user",
                "conversation_id": conversation_id,
                "custom_prompt": custom_prompt,
                "llm_config": llm_config or {},
                "messages": [],
                "retrieved_documents": [],
                "response": None,
                "progress": []
            }

            # LangGraph 스트리밍 실행
            for output in self.graph.stream(initial_state):
                # 각 노드의 실행 결과를 yield
                for node_name, node_output in output.items():
                    # 진행 상황 이벤트
                    if "progress" in node_output:
                        for progress_item in node_output["progress"]:
                            yield {
                                "type": "progress",
                                "data": {
                                    "node": node_name,
                                    "stage": progress_item.get("stage"),
                                    "status": progress_item.get("status"),
                                    "message": progress_item.get("message")
                                }
                            }

                    # 최종 응답
                    if "response" in node_output and node_output["response"]:
                        response = node_output["response"]
                        yield {
                            "type": "final",
                            "data": {
                                "content": response.content,
                                "sources": response.sources,
                                "confidence_score": response.confidence_score,
                                "table_data": response.table_data,
                                "chart_data": response.chart_data
                            }
                        }

        except Exception as e:
            # 에러 이벤트
            yield {
                "type": "error",
                "data": {
                    "error": str(e),
                    "message": "처리 중 오류가 발생했습니다."
                }
            }
```

### 3. 이벤트 타입

```python
# 이벤트 타입 정의
EVENT_TYPES = {
    "progress": {
        "description": "진행 상황 업데이트",
        "example": {
            "type": "progress",
            "data": {
                "node": "query_analysis",
                "stage": "analyzing",
                "status": "in_progress",
                "message": "질문 분석 중..."
            }
        }
    },
    "final": {
        "description": "최종 응답",
        "example": {
            "type": "final",
            "data": {
                "content": "응답 내용...",
                "sources": [...],
                "confidence_score": 0.85
            }
        }
    },
    "error": {
        "description": "오류 발생",
        "example": {
            "type": "error",
            "data": {
                "error": "ConnectionError",
                "message": "데이터베이스 연결 실패"
            }
        }
    }
}
```

---

## Frontend 구현

### 1. API Service Layer

**파일**: `frontend/src/services/api.js`

```javascript
const API_BASE_URL = '/api';

export const chatAPI = {
  /**
   * 메시지 전송 (스트리밍)
   *
   * @param {Object} data - 메시지 데이터
   * @param {Function} onProgress - 진행 상황 콜백
   * @param {Function} onComplete - 완료 콜백
   * @param {Function} onError - 에러 콜백
   * @returns {EventSource} EventSource 객체 (연결 종료용)
   */
  sendMessageStream: (data, onProgress, onComplete, onError) => {
    // 1. EventSource 생성 (SSE 클라이언트)
    const url = new URL(`${API_BASE_URL}/chat/stream`, window.location.origin);

    // GET 방식으로 파라미터 전달 (EventSource는 POST 미지원)
    // 또는 POST 데이터를 서버에서 읽도록 수정 필요
    const eventSource = new EventSource(url);

    // 2. 메시지 수신 핸들러
    eventSource.onmessage = (event) => {
      try {
        const eventData = JSON.parse(event.data);

        // 이벤트 타입별 처리
        switch (eventData.type) {
          case 'progress':
            // 진행 상황 업데이트
            onProgress && onProgress(eventData.data);
            break;

          case 'final':
            // 최종 응답
            onComplete && onComplete(eventData.data);
            eventSource.close();  // 연결 종료
            break;

          case 'error':
            // 에러 발생
            onError && onError(eventData.data);
            eventSource.close();
            break;

          default:
            console.warn('Unknown event type:', eventData.type);
        }
      } catch (error) {
        console.error('Stream parsing error:', error);
        onError && onError({
          error: 'ParseError',
          message: '응답 파싱 실패'
        });
      }
    };

    // 3. 에러 핸들러
    eventSource.onerror = (error) => {
      console.error('EventSource error:', error);
      onError && onError({
        error: 'ConnectionError',
        message: '서버 연결 실패'
      });
      eventSource.close();
    };

    // 4. EventSource 반환 (수동 종료 가능)
    return eventSource;
  },

  /**
   * 메시지 전송 (동기)
   *
   * @param {Object} data - 메시지 데이터
   * @returns {Promise} 응답 Promise
   */
  sendMessage: async (data) => {
    const response = await axios.post('/api/chat', data);
    return response.data;
  }
};
```

### 2. React 컴포넌트 통합

**파일**: `frontend/src/App.jsx` 또는 `ChatInterface.jsx`

```javascript
import { useState, useEffect } from 'react';
import { chatAPI } from './services/api';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState([]);
  const [currentStream, setCurrentStream] = useState(null);

  const handleSendMessage = async (userMessage) => {
    // 1. 사용자 메시지 추가
    const userMsg = {
      role: 'user',
      content: userMessage
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    setProgress([]);

    // 2. 스트리밍 시작
    const eventSource = chatAPI.sendMessageStream(
      {
        message: userMessage,
        user_id: 'user123',
        conversation_id: 'conv-xyz'
      },

      // onProgress: 진행 상황 업데이트
      (progressData) => {
        console.log('Progress:', progressData);
        setProgress(prev => [...prev, {
          stage: progressData.stage,
          message: progressData.message,
          status: progressData.status
        }]);
      },

      // onComplete: 최종 응답
      (finalData) => {
        console.log('Complete:', finalData);

        // 봇 응답 추가
        const botMsg = {
          role: 'assistant',
          content: finalData.content,
          sources: finalData.sources,
          confidenceScore: finalData.confidence_score
        };
        setMessages(prev => [...prev, botMsg]);

        setLoading(false);
        setProgress([]);
        setCurrentStream(null);
      },

      // onError: 에러 처리
      (errorData) => {
        console.error('Error:', errorData);

        // 에러 메시지 표시
        const errorMsg = {
          role: 'assistant',
          content: errorData.message || '오류가 발생했습니다.',
          error: true
        };
        setMessages(prev => [...prev, errorMsg]);

        setLoading(false);
        setProgress([]);
        setCurrentStream(null);
      }
    );

    // 3. EventSource 저장 (취소 가능하도록)
    setCurrentStream(eventSource);
  };

  // 4. 스트리밍 취소 함수
  const handleCancelStream = () => {
    if (currentStream) {
      currentStream.close();
      setCurrentStream(null);
      setLoading(false);
      setProgress([]);
    }
  };

  // 5. 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (currentStream) {
        currentStream.close();
      }
    };
  }, [currentStream]);

  return (
    <div>
      {/* 메시지 목록 */}
      <div className="messages">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}
      </div>

      {/* 진행 상황 표시 */}
      {loading && (
        <div className="progress-indicator">
          {progress.map((item, idx) => (
            <div key={idx} className="progress-item">
              {item.message}
            </div>
          ))}
          <button onClick={handleCancelStream}>
            취소
          </button>
        </div>
      )}

      {/* 입력 폼 */}
      <form onSubmit={(e) => {
        e.preventDefault();
        handleSendMessage(e.target.message.value);
        e.target.reset();
      }}>
        <input
          name="message"
          placeholder="메시지를 입력하세요..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          전송
        </button>
      </form>
    </div>
  );
}
```

### 3. 진행 상황 표시 컴포넌트

```javascript
function ProgressIndicator({ progress }) {
  const stages = {
    'query_analysis': '질문 분석 중...',
    'data_retrieval': '데이터 검색 중...',
    'response_generation': '응답 생성 중...'
  };

  return (
    <div className="progress-container">
      {progress.map((item, idx) => (
        <div
          key={idx}
          className={`progress-item ${item.status}`}
        >
          <div className="stage-icon">
            {item.status === 'completed' ? '✅' : '⏳'}
          </div>
          <div className="stage-text">
            {stages[item.stage] || item.message}
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## 예외 처리

### 1. Backend 예외 처리

```python
@bp.route("/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json()

    def generate():
        try:
            # 타임아웃 설정
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Request timeout")

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(60)  # 60초 타임아웃

            agent = get_chatbot_agent()

            for event in agent.stream(...):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

            signal.alarm(0)  # 타임아웃 해제

        except TimeoutError:
            yield f"data: {json.dumps({
                'type': 'error',
                'data': {
                    'error': 'Timeout',
                    'message': '요청 시간이 초과되었습니다.'
                }
            }, ensure_ascii=False)}\n\n"

        except ConnectionError as e:
            yield f"data: {json.dumps({
                'type': 'error',
                'data': {
                    'error': 'ConnectionError',
                    'message': '데이터베이스 연결 실패'
                }
            }, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({
                'type': 'error',
                'data': {
                    'error': type(e).__name__,
                    'message': str(e)
                }
            }, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype="text/event-stream")
```

### 2. Frontend 예외 처리

```javascript
sendMessageStream: (data, onProgress, onComplete, onError) => {
  // 타임아웃 설정 (60초)
  const timeoutId = setTimeout(() => {
    eventSource.close();
    onError && onError({
      error: 'Timeout',
      message: '요청 시간이 초과되었습니다.'
    });
  }, 60000);

  const eventSource = new EventSource(url);

  eventSource.onmessage = (event) => {
    try {
      clearTimeout(timeoutId);  // 타임아웃 해제

      const eventData = JSON.parse(event.data);

      // ... 이벤트 처리

      if (eventData.type === 'final') {
        clearTimeout(timeoutId);
        onComplete && onComplete(eventData.data);
        eventSource.close();
      }
    } catch (error) {
      clearTimeout(timeoutId);
      onError && onError({
        error: 'ParseError',
        message: '응답 파싱 실패: ' + error.message
      });
      eventSource.close();
    }
  };

  eventSource.onerror = (error) => {
    clearTimeout(timeoutId);

    // 연결 상태 확인
    if (eventSource.readyState === EventSource.CLOSED) {
      onError && onError({
        error: 'ConnectionClosed',
        message: '서버 연결이 종료되었습니다.'
      });
    } else {
      onError && onError({
        error: 'ConnectionError',
        message: '서버 연결에 실패했습니다.'
      });
    }

    eventSource.close();
  };

  return eventSource;
};
```

### 3. 재연결 로직

```javascript
function createReconnectingEventSource(url, maxRetries = 3) {
  let retryCount = 0;
  let eventSource;

  function connect() {
    eventSource = new EventSource(url);

    eventSource.onerror = () => {
      eventSource.close();

      if (retryCount < maxRetries) {
        retryCount++;
        console.log(`재연결 시도 ${retryCount}/${maxRetries}...`);

        // 지수 백오프 (1초, 2초, 4초...)
        setTimeout(() => {
          connect();
        }, Math.pow(2, retryCount) * 1000);
      } else {
        console.error('최대 재연결 시도 횟수 초과');
      }
    };

    eventSource.onopen = () => {
      console.log('연결 성공');
      retryCount = 0;  // 재연결 카운트 초기화
    };

    return eventSource;
  }

  return connect();
}
```

---

## 테스트 방법

### 1. Backend 테스트 (curl)

```bash
# 스트리밍 엔드포인트 테스트
curl -N -X POST http://localhost:5001/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ABC-12345 부품의 재고는?",
    "user_id": "test_user"
  }'

# 예상 출력:
# data: {"type":"progress","data":{"stage":"query_analysis","message":"질문 분석 중..."}}
#
# data: {"type":"progress","data":{"stage":"data_retrieval","message":"데이터 검색 중..."}}
#
# data: {"type":"final","data":{"content":"재고는 1000개입니다..."}}
```

### 2. Frontend 테스트

```javascript
// 개발자 도구 콘솔에서 테스트
chatAPI.sendMessageStream(
  { message: "테스트 질문", user_id: "test" },
  (progress) => console.log('Progress:', progress),
  (final) => console.log('Complete:', final),
  (error) => console.error('Error:', error)
);
```

### 3. 브라우저 네트워크 탭

1. F12 → Network 탭 열기
2. "stream" 필터 적용
3. `/chat/stream` 요청 확인
4. Type: `eventsource` 확인
5. Preview 탭에서 이벤트 스트림 확인

---

## 문제 해결

### 문제 1: "EventSource는 POST를 지원하지 않습니다"

**원인**: EventSource API는 GET 방식만 지원

**해결 방법 1**: URL 파라미터 사용
```javascript
const params = new URLSearchParams({
  message: data.message,
  user_id: data.user_id
});
const eventSource = new EventSource(`${API_BASE_URL}/chat/stream?${params}`);
```

**해결 방법 2**: 초기 POST로 세션 생성, 이후 GET으로 스트리밍
```javascript
// 1. POST로 스트리밍 세션 생성
const session = await api.post('/chat/stream/init', data);

// 2. GET으로 스트리밍 구독
const eventSource = new EventSource(`/chat/stream/${session.id}`);
```

### 문제 2: "응답이 버퍼링되어 지연됩니다"

**원인**: Nginx나 프록시가 응답을 버퍼링

**해결**: Nginx 설정
```nginx
location /api/chat/stream {
    proxy_pass http://backend;
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding off;
}
```

**Flask 헤더 추가**:
```python
return Response(
    generate(),
    mimetype="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no"  # Nginx 버퍼링 비활성화
    }
)
```

### 문제 3: "연결이 자주 끊깁니다"

**원인**: 타임아웃 또는 네트워크 불안정

**해결**: Heartbeat 메시지
```python
def generate():
    import time
    last_heartbeat = time.time()

    for event in agent.stream(...):
        yield f"data: {json.dumps(event)}\n\n"

        # 30초마다 heartbeat 전송
        if time.time() - last_heartbeat > 30:
            yield f": heartbeat\n\n"
            last_heartbeat = time.time()
```

### 문제 4: "한글이 깨집니다"

**원인**: UTF-8 인코딩 문제

**해결**:
```python
# ensure_ascii=False 사용
yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

# Flask 응답 인코딩 명시
return Response(
    generate(),
    mimetype="text/event-stream; charset=utf-8"
)
```

---

## 성능 최적화

### 1. 청크 크기 조절

```python
# 작은 청크: 더 빠른 피드백, 더 많은 오버헤드
# 큰 청크: 더 적은 오버헤드, 더 느린 피드백

def generate():
    buffer = []
    buffer_size = 5  # 5개 이벤트마다 전송

    for event in agent.stream(...):
        buffer.append(event)

        if len(buffer) >= buffer_size:
            for e in buffer:
                yield f"data: {json.dumps(e)}\n\n"
            buffer = []

    # 남은 이벤트 전송
    for e in buffer:
        yield f"data: {json.dumps(e)}\n\n"
```

### 2. 압축

```python
import gzip

def generate():
    for event in agent.stream(...):
        data = json.dumps(event, ensure_ascii=False)

        # 큰 응답만 압축
        if len(data) > 1024:
            compressed = gzip.compress(data.encode('utf-8'))
            yield f"data: {compressed.hex()}\n\n"
        else:
            yield f"data: {data}\n\n"
```

---

## 요약

### Backend 체크리스트
- [ ] Flask Route에 `/chat/stream` 추가
- [ ] `Response(generate(), mimetype="text/event-stream")` 반환
- [ ] `data: {JSON}\n\n` 형식으로 이벤트 전송
- [ ] 예외 처리 및 에러 이벤트 전송
- [ ] 타임아웃 설정
- [ ] Nginx 버퍼링 비활성화

### Frontend 체크리스트
- [ ] EventSource API 사용
- [ ] `onmessage`, `onerror` 핸들러 구현
- [ ] 이벤트 타입별 처리 (progress/final/error)
- [ ] 연결 종료 (`eventSource.close()`)
- [ ] 컴포넌트 언마운트 시 정리
- [ ] 타임아웃 및 재연결 로직

### 테스트 체크리스트
- [ ] curl로 Backend 테스트
- [ ] 브라우저 Network 탭에서 확인
- [ ] 진행 상황이 실시간으로 표시되는지 확인
- [ ] 에러 처리가 정상 동작하는지 확인
- [ ] 취소 기능이 작동하는지 확인

**모든 구현 완료!** 🎉
