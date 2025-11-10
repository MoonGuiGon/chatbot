#!/bin/bash

echo "========================================="
echo "로컬 환경 실제 테스트 설정"
echo "========================================="
echo ""

# 색상 코드
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Docker 확인
echo -e "${BLUE}[1/5] Docker 확인...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker가 설치되어 있지 않습니다.${NC}"
    echo "Docker Desktop을 설치해주세요: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker가 실행 중이 아닙니다.${NC}"
    echo "Docker Desktop을 실행해주세요."
    exit 1
fi

echo -e "${GREEN}✓ Docker 확인 완료${NC}"
echo ""

# Step 2: Docker Compose 실행
echo -e "${BLUE}[2/5] MongoDB와 PostgreSQL 시작...${NC}"
docker-compose up -d

echo "데이터베이스 준비 대기 중... (10초)"
sleep 10

# 헬스체크
echo "MongoDB 연결 확인..."
if docker exec semiconductor_mongodb mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
    echo -e "${GREEN}✓ MongoDB 정상${NC}"
else
    echo -e "${RED}❌ MongoDB 연결 실패${NC}"
fi

echo "PostgreSQL 연결 확인..."
if docker exec semiconductor_postgres pg_isready -U postgres &> /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL 정상${NC}"
else
    echo -e "${RED}❌ PostgreSQL 연결 실패${NC}"
fi
echo ""

# Step 3: .env 파일 확인
echo -e "${BLUE}[3/5] Backend 환경 설정...${NC}"
cd backend

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다. .env.example을 복사합니다.${NC}"
    cp .env.example .env
    echo ""
    echo -e "${YELLOW}🔑 중요: backend/.env 파일을 열어서 다음을 수정하세요:${NC}"
    echo "  1. TEST_MODE=False (실제 모드로 변경)"
    echo "  2. LLM_API_KEY=your-openai-api-key (실제 OpenAI API Key 입력)"
    echo ""
    read -p "계속하려면 Enter를 누르세요..."
fi

# Python 가상환경
if [ ! -d "venv" ]; then
    echo "Python 가상환경 생성 중..."
    python3 -m venv venv
fi

echo "가상환경 활성화..."
source venv/bin/activate

echo "Python 패키지 설치 중..."
pip install -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✓ Backend 설정 완료${NC}"
echo ""

# Step 4: 샘플 데이터 생성 여부 확인
echo -e "${BLUE}[4/5] 샘플 데이터 생성${NC}"
read -p "MongoDB 샘플 데이터를 생성하시겠습니까? (y/N): " mongo_seed
if [ "$mongo_seed" = "y" ] || [ "$mongo_seed" = "Y" ]; then
    echo "MongoDB 샘플 데이터 생성 중..."
    python scripts/seed_mongodb.py
    echo -e "${GREEN}✓ MongoDB 데이터 생성 완료${NC}"
else
    echo "MongoDB 데이터 생성을 건너뜁니다."
fi
echo ""

read -p "pgvector 샘플 문서를 생성하시겠습니까? (OpenAI API 사용, 약 $0.01 비용) (y/N): " pg_seed
if [ "$pg_seed" = "y" ] || [ "$pg_seed" = "Y" ]; then
    echo "pgvector 샘플 문서 생성 중..."
    python scripts/seed_pgvector.py
    echo -e "${GREEN}✓ pgvector 데이터 생성 완료${NC}"
else
    echo "pgvector 데이터 생성을 건너뜁니다."
fi
echo ""

# Step 5: Frontend 설정
echo -e "${BLUE}[5/5] Frontend 환경 설정...${NC}"
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "npm 패키지 설치 중..."
    npm install
fi

echo -e "${GREEN}✓ Frontend 설정 완료${NC}"
echo ""

# 완료 메시지
cd ..
echo "========================================="
echo -e "${GREEN}✓ 로컬 환경 설정 완료!${NC}"
echo "========================================="
echo ""
echo "📍 실행 중인 서비스:"
echo "  - MongoDB:    http://localhost:27017"
echo "  - PostgreSQL: http://localhost:5432"
echo ""
echo "🚀 서버 실행 방법:"
echo ""
echo "  1. Backend 서버:"
echo "     cd backend"
echo "     source venv/bin/activate"
echo "     python run.py"
echo ""
echo "  2. Frontend 서버 (새 터미널):"
echo "     cd frontend"
echo "     npm run dev"
echo ""
echo "  3. 브라우저에서 접속:"
echo "     http://localhost:3000"
echo ""
echo "⚠️  주의사항:"
echo "  - backend/.env 파일에 실제 OpenAI API Key를 입력했는지 확인하세요!"
echo "  - TEST_MODE=False로 설정되어 있는지 확인하세요!"
echo ""
echo "📚 자세한 가이드: LOCAL_SETUP_GUIDE.md"
echo "========================================="
