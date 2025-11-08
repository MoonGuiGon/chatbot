import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  Button,
  Chip,
  TextField,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Menu as MenuIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  Upload as UploadIcon,
  Chat as ChatIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import ChatArea from './components/Chat/ChatArea';
import ChatInput from './components/Chat/ChatInput';
import SettingsDialog from './components/Settings/SettingsDialog';
import DocumentUploadDialog from './components/Document/DocumentUploadDialog';
import useChatStore from './store/chatStore';
import { chatAPI } from './services/api';

const DRAWER_WIDTH = 280;

function App() {
  const {
    messages,
    isLoading,
    sidebarOpen,
    currentConversationId,
    toggleSidebar,
    addMessage,
    setMessages,
    setLoading,
    setProgress,
    addProgress,
    clearProgress,
    startNewConversation,
    settings
  } = useChatStore();

  const [userId] = useState('user_demo'); // 임시 사용자 ID
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [editingConvId, setEditingConvId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  const handleSendMessage = async (messageText) => {
    // 사용자 메시지 추가
    const userMessage = {
      role: 'user',
      content: messageText,
      query: messageText
    };
    addMessage(userMessage);

    // 로딩 시작
    setLoading(true);
    clearProgress();

    try {
      // 대화 ID가 없으면 생성
      let conversationId = currentConversationId;
      if (!conversationId) {
        const result = await chatAPI.createConversation(userId);
        conversationId = result.conversation_id;
      }

      // API 호출
      const result = await chatAPI.sendMessage({
        message: messageText,
        user_id: userId,
        conversation_id: conversationId,
        custom_prompt: settings.customPrompt,
        llm_config: {
          model: settings.model,
          temperature: settings.temperature,
          max_tokens: settings.maxTokens
        }
      });

      if (result.success) {
        // Assistant 응답 추가
        const assistantMessage = {
          role: 'assistant',
          content: result.content,
          sources: result.sources,
          confidenceScore: result.confidence_score,
          tableData: result.table_data,
          chartData: result.chart_data,
          warnings: result.warnings,
          conversationId
        };
        addMessage(assistantMessage);

        // 첫 메시지 후 자동 생성된 제목 업데이트
        if (result.conversation_title) {
          setConversationHistory(prev =>
            prev.map(conv =>
              conv.id === conversationId
                ? { ...conv, title: result.conversation_title }
                : conv
            )
          );
        }
      } else {
        // 에러 메시지
        addMessage({
          role: 'assistant',
          content: `오류: ${result.error}`,
          warnings: ['요청 처리 중 오류가 발생했습니다.']
        });
      }
    } catch (error) {
      console.error('Chat error:', error);
      addMessage({
        role: 'assistant',
        content: '죄송합니다. 서버와의 통신 중 오류가 발생했습니다.',
        warnings: [error.message]
      });
    } finally {
      setLoading(false);
      clearProgress();
    }
  };

  const handleNewConversation = async () => {
    try {
      // 새 대화 생성 API 호출
      const result = await chatAPI.createConversation(userId);

      if (result.success) {
        // 대화 이력에 추가
        const newConv = {
          id: result.conversation_id,
          title: result.title || '새 대화',
          date: new Date().toLocaleDateString('ko-KR'),
          messages: []
        };
        setConversationHistory(prev => [newConv, ...prev]);

        // 새 대화로 전환
        startNewConversation();
      }
    } catch (error) {
      console.error('새 대화 생성 오류:', error);
    }
  };

  const handleDeleteConversation = async (convId, event) => {
    event.stopPropagation(); // 대화 로드 방지

    if (!window.confirm('이 대화를 삭제하시겠습니까?')) {
      return;
    }

    try {
      const result = await chatAPI.deleteConversation(convId);
      if (result.success) {
        setConversationHistory(prev => prev.filter(conv => conv.id !== convId));
      }
    } catch (error) {
      console.error('대화 삭제 오류:', error);
    }
  };

  const handleStartEditTitle = (convId, currentTitle, event) => {
    event.stopPropagation(); // 대화 로드 방지
    setEditingConvId(convId);
    setEditTitle(currentTitle);
  };

  const handleSaveTitle = async (convId, event) => {
    event.stopPropagation();

    if (!editTitle.trim()) {
      return;
    }

    try {
      const result = await chatAPI.updateConversationTitle(convId, editTitle);
      if (result.success) {
        setConversationHistory(prev =>
          prev.map(conv =>
            conv.id === convId ? { ...conv, title: editTitle } : conv
          )
        );
        setEditingConvId(null);
        setEditTitle('');
      }
    } catch (error) {
      console.error('제목 수정 오류:', error);
    }
  };

  const handleCancelEdit = (event) => {
    event.stopPropagation();
    setEditingConvId(null);
    setEditTitle('');
  };

  const handleOpenSettings = () => {
    setSettingsOpen(true);
  };

  const handleCloseSettings = () => {
    setSettingsOpen(false);
  };

  const handleOpenUpload = () => {
    setUploadOpen(true);
  };

  const handleCloseUpload = () => {
    setUploadOpen(false);
  };

  const loadConversationHistory = (conversation) => {
    setMessages(conversation.messages);
  };

  // 예시 대화 이력 및 초기 메시지 초기화
  useEffect(() => {
    const exampleConversations = [
      {
        id: 'conv_001',
        title: '부품 ABC-12345 재고 조회',
        date: '2024-01-15',
        messages: [
          {
            role: 'user',
            content: '부품 ABC-12345의 재고는?'
          },
          {
            role: 'assistant',
            content: '부품 ABC-12345 (반도체 칩 A)의 현재 재고 정보를 안내드립니다:\n\n**재고 현황**\n- 총 재고: 1,000개\n- 가용 재고: 850개\n- 예약: 150개',
            sources: [
              { metadata: { file_name: '부품_재고_DB' } }
            ],
            confidenceScore: 0.95
          }
        ]
      },
      {
        id: 'conv_002',
        title: '2021-2023 출고 데이터 분석',
        date: '2024-01-14',
        messages: [
          {
            role: 'user',
            content: '최근 3년간 출고 데이터를 표와 그래프로 보여줘'
          },
          {
            role: 'assistant',
            content: `부품 ABC-12345의 최근 3년간(2021-2023) 출고 데이터를 분석했습니다.

## 📊 연도별 출고 현황 요약

### 총 출고량
- **2021년**: 12,450개
- **2022년**: 15,800개 (전년 대비 +26.9%)
- **2023년**: 18,200개 (전년 대비 +15.2%)

---

## 📅 월별 출고 이력 (2021-2023)

| 월 | 2021년 | 2022년 | 2023년 | 평균 |
|----|--------|--------|--------|------|
| 1월 | 950개 | 1,200개 | 1,450개 | 1,200개 |
| 2월 | 880개 | 1,150개 | 1,380개 | 1,137개 |
| 3월 | 1,020개 | 1,280개 | 1,520개 | 1,273개 |
| 4월 | 1,050개 | 1,320개 | 1,550개 | 1,307개 |
| 5월 | 1,100개 | 1,400개 | 1,620개 | 1,373개 |
| 6월 | 1,080개 | 1,380개 | 1,580개 | 1,347개 |
| 7월 | 990개 | 1,250개 | 1,480개 | 1,240개 |
| 8월 | 920개 | 1,180개 | 1,420개 | 1,173개 |
| 9월 | 1,040개 | 1,340개 | 1,590개 | 1,323개 |
| 10월 | 1,100개 | 1,420개 | 1,650개 | 1,390개 |
| 11월 | 1,150개 | 1,480개 | 1,710개 | 1,447개 |
| 12월 | 1,170개 | 1,400개 | 1,750개 | 1,440개 |
| **합계** | **12,450개** | **15,800개** | **18,200개** | **15,483개** |

---

## 📈 3년간 출고 추이 그래프

\`\`\`json
{
  "type": "line",
  "title": "월별 출고 추이 (2021-2023)",
  "data": {
    "labels": ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"],
    "datasets": [
      {
        "label": "2021년",
        "data": [950, 880, 1020, 1050, 1100, 1080, 990, 920, 1040, 1100, 1150, 1170],
        "borderColor": "rgba(75, 192, 192, 1)",
        "backgroundColor": "rgba(75, 192, 192, 0.2)",
        "tension": 0.4
      },
      {
        "label": "2022년",
        "data": [1200, 1150, 1280, 1320, 1400, 1380, 1250, 1180, 1340, 1420, 1480, 1400],
        "borderColor": "rgba(54, 162, 235, 1)",
        "backgroundColor": "rgba(54, 162, 235, 0.2)",
        "tension": 0.4
      },
      {
        "label": "2023년",
        "data": [1450, 1380, 1520, 1550, 1620, 1580, 1480, 1420, 1590, 1650, 1710, 1750],
        "borderColor": "rgba(255, 99, 132, 1)",
        "backgroundColor": "rgba(255, 99, 132, 0.2)",
        "tension": 0.4
      }
    ]
  }
}
\`\`\`

---

## 📊 연도별 총 출고량 비교

\`\`\`json
{
  "type": "bar",
  "title": "연도별 총 출고량",
  "data": {
    "labels": ["2021년", "2022년", "2023년"],
    "datasets": [{
      "label": "출고량 (개)",
      "data": [12450, 15800, 18200],
      "backgroundColor": [
        "rgba(75, 192, 192, 0.8)",
        "rgba(54, 162, 235, 0.8)",
        "rgba(255, 99, 132, 0.8)"
      ],
      "borderColor": [
        "rgba(75, 192, 192, 1)",
        "rgba(54, 162, 235, 1)",
        "rgba(255, 99, 132, 1)"
      ],
      "borderWidth": 2
    }]
  }
}
\`\`\`

---

## 💡 주요 인사이트

1. **지속적인 성장세**: 2021년 대비 2023년 46.2% 증가
2. **성수기**: 10-12월 출고량이 가장 많음 (평균 대비 +15%)
3. **비수기**: 2월, 8월 출고량 감소 경향 (설 연휴, 휴가 시즌)
4. **안정적 수요**: 매년 평균 12-15% 성장률 유지`,
            sources: [
              { metadata: { file_name: '출고_이력_DB' } },
              { metadata: { file_name: '2021-2023_생산_보고서.pdf' } }
            ],
            confidenceScore: 0.92
          }
        ]
      },
      {
        id: 'conv_003',
        title: '부품 검사 절차 문의',
        date: '2024-01-13',
        messages: [
          {
            role: 'user',
            content: '부품 입고 검사 절차가 뭐야?'
          },
          {
            role: 'assistant',
            content: '부품 입고 검사 절차는 다음과 같습니다:\n\n1. 외관 검사\n2. 전기적 검사\n3. 기능 검사',
            sources: [
              { metadata: { file_name: '검사_절차.pdf' } }
            ],
            confidenceScore: 0.88
          }
        ]
      }
    ];

    setConversationHistory(exampleConversations);

    // 초기 웰컴 메시지 (한 번만 표시)
    if (messages.length === 0) {
      setMessages([
        {
          role: 'assistant',
          content: `안녕하세요! 반도체 부품 챗봇입니다. 👋

**테스트 가능한 기능:**
1. 📦 부품 재고 조회
2. 📊 표와 그래프 생성
3. 👍👎 피드백 제공
4. ⚙️ 설정 변경
5. 📄 문서 업로드 (시뮬레이션)
6. 💬 대화 이력 보기

**예시 질문:**
- "부품 ABC-12345의 재고는?"
- "반도체 칩 A의 출고 이력을 표로 보여줘"
- "부품별 재고 현황을 그래프로 보여줘"
- "최근 3년간 출고 데이터를 표와 그래프로 보여줘" ⭐
- "부품 검사 절차가 뭐야?"

💡 **Tip**: 좌측 사이드바의 "2021-2023 출고 데이터 분석"을 클릭해보세요!

질문해주세요!`,
          sources: [],
          confidenceScore: 1.0
        }
      ]);
    }
  }, []);

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* AppBar */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={toggleSidebar}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            반도체 부품 챗봇
          </Typography>
          <IconButton color="inherit" onClick={handleOpenUpload} title="문서 업로드">
            <UploadIcon />
          </IconButton>
          <IconButton color="inherit" onClick={handleOpenSettings} title="설정">
            <SettingsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="persistent"
        open={sidebarOpen}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            mt: 8
          }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleNewConversation}
          >
            새 대화
          </Button>
        </Box>
        <Divider />
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            대화 이력 (예시)
          </Typography>
        </Box>
        <List dense>
          {conversationHistory.map((conversation) => (
            <ListItem key={conversation.id} disablePadding>
              <ListItemButton onClick={() => loadConversationHistory(conversation)}>
                <ListItemText
                  primary={
                    editingConvId === conversation.id ? (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <TextField
                          size="small"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          onClick={(e) => e.stopPropagation()}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              handleSaveTitle(conversation.id, e);
                            }
                          }}
                          sx={{ flexGrow: 1 }}
                        />
                        <IconButton
                          size="small"
                          onClick={(e) => handleSaveTitle(conversation.id, e)}
                        >
                          <CheckIcon fontSize="small" />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={handleCancelEdit}
                        >
                          <CloseIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    ) : (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <ChatIcon fontSize="small" />
                        <Typography variant="body2" noWrap sx={{ flexGrow: 1 }}>
                          {conversation.title}
                        </Typography>
                      </Box>
                    )
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {conversation.date}
                    </Typography>
                  }
                />
                {editingConvId !== conversation.id && (
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      size="small"
                      onClick={(e) => handleStartEditTitle(conversation.id, conversation.title, e)}
                      sx={{ mr: 0.5 }}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      edge="end"
                      size="small"
                      onClick={(e) => handleDeleteConversation(conversation.id, e)}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </ListItemSecondaryAction>
                )}
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          ml: sidebarOpen ? 0 : `-${DRAWER_WIDTH}px`,
          mt: 8,
          transition: (theme) =>
            theme.transitions.create(['margin'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen
            })
        }}
      >
        {/* Chat Area */}
        <ChatArea />

        {/* Chat Input */}
        <Box sx={{ p: 2 }}>
          <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </Box>
      </Box>

      {/* Settings Dialog */}
      <SettingsDialog open={settingsOpen} onClose={handleCloseSettings} />

      {/* Document Upload Dialog */}
      <DocumentUploadDialog open={uploadOpen} onClose={handleCloseUpload} />
    </Box>
  );
}

export default App;
