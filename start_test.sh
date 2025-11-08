#!/bin/bash

echo "========================================="
echo "반도체 부품 챗봇 테스트 모드 시작"
echo "========================================="

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backend 실행
echo -e "${BLUE}[1/3] Backend 환경 설정...${NC}"
cd backend

# .env 파일 확인 및 생성
if [ ! -f ".env" ]; then
    echo "📝 .env 파일 생성 중..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env 파일이 생성되었습니다 (TEST_MODE=True)${NC}"
fi

# Python 가상환경 활성화 (있다면)
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "가상환경이 없습니다. 생성 중..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 의존성 설치
echo "📦 Python 패키지 설치 중..."
pip install -r requirements.txt > /dev/null 2>&1

# Backend 서버 백그라운드 실행
python run.py &
BACKEND_PID=$!

echo -e "${GREEN}✓ Backend 서버 시작됨 (PID: $BACKEND_PID)${NC}"

# Frontend 실행
cd ../frontend
echo -e "${BLUE}[2/3] Frontend 환경 설정...${NC}"

# npm 의존성 설치
if [ ! -d "node_modules" ]; then
    echo "📦 npm 패키지 설치 중..."
    npm install
fi

# Frontend 서버 백그라운드 실행
echo -e "${BLUE}[3/3] 서버 시작 중...${NC}"
npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}✓ Frontend 서버 시작됨 (PID: $FRONTEND_PID)${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}✓ 모든 서버가 시작되었습니다!${NC}"
echo "========================================="
echo ""
echo "📍 Backend:  http://localhost:5001"
echo "📍 Frontend: http://localhost:3000"
echo ""
echo "🧪 테스트 모드: Mock DB/LLM 사용 중"
echo ""
echo "💡 테스트 가이드: TESTING_GUIDE.md 참조"
echo ""
echo "⚠️  종료하려면: ./stop_test.sh 실행 또는 Ctrl+C"
echo "========================================="

# PID 저장
cd ..
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 브라우저 자동 열기 (macOS)
echo ""
echo "🌐 브라우저를 여는 중..."
sleep 3
open http://localhost:3000 2>/dev/null || echo "브라우저를 수동으로 열어주세요: http://localhost:3000"

# 대기
wait
