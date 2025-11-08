# 🔧 빠른 문제 해결 가이드

## 🚨 현재 문제

1. **예시 대화에 표와 그래프가 안 보임** → ✅ 수정 완료!
2. **"최근 3년간 출고 데이터..." 질문 시 403 오류** → 서버 시작 필요

---

## ✅ 해결 방법

### 1. 서버 재시작 (필수!)

기존 서버를 종료하고 다시 시작하세요:

```bash
# 1. 기존 서버 종료
./stop_test.sh

# 2. 서버 재시작
./start_test.sh
```

**또는 모든 프로세스를 직접 종료:**

```bash
# Flask 서버 종료
pkill -f "python.*run.py"
pkill -f flask

# npm 서버 종료
pkill -f "vite"
pkill -f "node.*vite"

# 그 다음 재시작
./start_test.sh
```

### 2. 브라우저 새로고침

서버가 시작된 후:
- **Cmd + Shift + R** (Mac)
- **Ctrl + Shift + R** (Windows/Linux)

---

## 📊 표와 그래프 확인 방법

### 방법 1: 예시 대화 클릭 (가장 빠름!)

1. 왼쪽 사이드바 열기 (햄버거 메뉴 ☰)
2. **"2021-2023 출고 데이터 분석"** 클릭
3. 즉시 표와 그래프 확인!

**이제 다음이 표시됩니다:**
- ✅ 12개월 x 3년 데이터 표
- ✅ Line 그래프 (3개 연도 비교)
- ✅ Bar 그래프 (연도별 총량)
- ✅ 주요 인사이트

### 방법 2: 직접 질문

채팅창에 입력:
```
최근 3년간 출고 데이터를 표와 그래프로 보여줘
```

**주의**: 서버가 실행 중이어야 합니다!

---

## 🔍 서버 상태 확인

### Backend 서버 확인

```bash
# Backend 프로세스 확인
ps aux | grep "python.*run.py"

# 포트 5000 사용 확인
lsof -i :5000
```

정상이면 이렇게 표시됩니다:
```
python run.py
tcp4  *:5000  (LISTEN)
```

### Frontend 서버 확인

```bash
# Frontend 프로세스 확인
ps aux | grep vite

# 포트 3000 사용 확인
lsof -i :3000
```

정상이면 이렇게 표시됩니다:
```
node vite
tcp4  *:3000  (LISTEN)
```

---

## 🐛 403 오류 원인

### 가능한 원인들:

1. **Backend 서버가 실행되지 않음**
   - 해결: `./start_test.sh` 실행

2. **포트 충돌**
   - 확인: `lsof -i :5000`
   - 해결: 충돌 프로세스 종료 후 재시작

3. **CORS 설정 문제**
   - 이미 수정됨 (Flask-CORS 설정 완료)

4. **가상환경 활성화 안됨**
   - `start_test.sh`가 자동으로 처리

---

## 📋 완벽한 테스트 절차

### Step 1: 완전히 초기화
```bash
# 모든 프로세스 종료
./stop_test.sh
pkill -f python
pkill -f node
pkill -f vite

# PID 파일 삭제
rm -f .backend.pid .frontend.pid
```

### Step 2: 서버 시작
```bash
./start_test.sh
```

**기다리세요**: 약 5-10초 후 자동으로 브라우저가 열립니다.

### Step 3: 확인
1. 브라우저가 http://localhost:3000 으로 열림
2. 왼쪽 사이드바 열기
3. "2021-2023 출고 데이터 분석" 클릭
4. 표와 그래프가 즉시 표시됨!

---

## 🎯 예상 결과

### 표시되어야 할 것들:

#### 1. 큰 표 (12행 x 4열)
```
| 월  | 2021년 | 2022년 | 2023년 | 평균   |
|-----|--------|--------|--------|--------|
| 1월 | 950개  | 1,200개| 1,450개| 1,200개|
| ... | ...    | ...    | ...    | ...    |
```

#### 2. Line 그래프
- 제목: "월별 출고 추이 (2021-2023)"
- 3개 선 (청록색/파란색/빨간색)
- X축: 1월~12월
- Y축: 출고량

#### 3. Bar 그래프
- 제목: "연도별 총 출고량"
- 3개 막대 (2021/2022/2023)
- 각각 다른 색상

#### 4. 인사이트 섹션
- 5개 주요 분석 포인트
- 아이콘과 함께 표시

---

## 💡 여전히 문제가 있다면

### 1. 로그 확인

**Backend 로그:**
```bash
# 터미널에서 직접 실행해서 에러 확인
cd backend
source venv/bin/activate
python run.py
```

**Frontend 로그:**
```bash
# 다른 터미널에서
cd frontend
npm run dev
```

### 2. 브라우저 콘솔 확인

1. F12 키 (개발자 도구)
2. Console 탭
3. 빨간색 에러 메시지 확인

**흔한 에러들:**
- `ERR_CONNECTION_REFUSED` → Backend 서버 안 돌아감
- `403 Forbidden` → Backend 서버는 돌지만 요청 거부
- `404 Not Found` → API 경로 문제

### 3. 의존성 재설치

```bash
# Backend
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Frontend
cd ../frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 🔥 긴급 해결 (완전 초기화)

모든 것이 안 되면:

```bash
# 1. 모든 프로세스 강제 종료
killall python3
killall node

# 2. 가상환경 재생성
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Frontend 재설치
cd ../frontend
rm -rf node_modules
npm install

# 4. 재시작
cd ..
./start_test.sh
```

---

## ✅ 성공 확인

다음이 모두 보이면 성공!

- ☑️ 사이드바에 3개 대화 이력
- ☑️ "2021-2023 출고 데이터 분석" 클릭하면
- ☑️ 큰 표 (12개월 x 3년)
- ☑️ Line 그래프 (월별 추이)
- ☑️ Bar 그래프 (연도별 비교)
- ☑️ 인사이트 섹션

---

**문제가 계속되면 에러 메시지를 캡처해서 알려주세요!** 🚀
