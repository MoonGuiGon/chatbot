#!/bin/bash

echo "========================================="
echo "서버 종료 중..."
echo "========================================="

# PID 파일에서 프로세스 ID 읽기
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null
    echo "✓ Backend 서버 종료됨 (PID: $BACKEND_PID)"
    rm .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null
    echo "✓ Frontend 서버 종료됨 (PID: $FRONTEND_PID)"
    rm .frontend.pid
fi

# 포트에서 실행 중인 프로세스 강제 종료 (fallback)
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "========================================="
echo "✓ 모든 서버가 종료되었습니다"
echo "========================================="
