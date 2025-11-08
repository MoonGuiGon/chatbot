import axios from 'axios';

const API_BASE_URL = '/api';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Chat API
export const chatAPI = {
  // 메시지 전송 (동기)
  sendMessage: async (data) => {
    const response = await api.post('/chat', data);
    return response.data;
  },

  // 메시지 전송 (스트리밍)
  sendMessageStream: (data, onProgress, onComplete, onError) => {
    const eventSource = new EventSource(
      `${API_BASE_URL}/chat/stream?${new URLSearchParams(data)}`
    );

    eventSource.onmessage = (event) => {
      try {
        const eventData = JSON.parse(event.data);

        if (eventData.type === 'progress') {
          onProgress && onProgress(eventData.data);
        } else if (eventData.type === 'final') {
          onComplete && onComplete(eventData.data);
          eventSource.close();
        } else if (eventData.type === 'error') {
          onError && onError(eventData.data);
          eventSource.close();
        }
      } catch (error) {
        console.error('Stream parsing error:', error);
      }
    };

    eventSource.onerror = (error) => {
      onError && onError(error);
      eventSource.close();
    };

    return eventSource;
  },

  // 대화 목록 조회
  getConversations: async (userId) => {
    const response = await api.get('/conversations', {
      params: { user_id: userId }
    });
    return response.data;
  },

  // 특정 대화 조회
  getConversation: async (conversationId) => {
    const response = await api.get(`/conversations/${conversationId}`);
    return response.data;
  },

  // 새 대화 생성
  createConversation: async (userId) => {
    const response = await api.post('/conversations', { user_id: userId });
    return response.data;
  },

  // 대화 삭제
  deleteConversation: async (conversationId) => {
    const response = await api.delete(`/conversations/${conversationId}`);
    return response.data;
  },

  // 대화 제목 수정
  updateConversationTitle: async (conversationId, title) => {
    const response = await api.put(`/conversations/${conversationId}/title`, { title });
    return response.data;
  },

  // 대화 제목 자동 생성
  generateConversationTitle: async (conversationId) => {
    const response = await api.post(`/conversations/${conversationId}/generate-title`);
    return response.data;
  }
};

// Document API
export const documentAPI = {
  // 문서 업로드
  uploadDocument: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: onProgress
    });
    return response.data;
  },

  // 문서 승인
  approveDocument: async (documentId, chunks) => {
    const response = await api.post(`/documents/${documentId}/approve`, {
      chunks
    });
    return response.data;
  },

  // 문서 거부
  rejectDocument: async (documentId) => {
    const response = await api.delete(`/documents/${documentId}/reject`);
    return response.data;
  },

  // 문서 목록 조회
  listDocuments: async () => {
    const response = await api.get('/documents');
    return response.data;
  },

  // 문서 삭제
  deleteDocument: async (documentId) => {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
  }
};

// Settings API
export const settingsAPI = {
  // 설정 조회
  getSettings: async () => {
    const response = await api.get('/settings');
    return response.data;
  },

  // LLM 설정 업데이트
  updateLLMSettings: async (settings) => {
    const response = await api.post('/settings/llm', settings);
    return response.data;
  },

  // 사용 가능한 모델 목록
  getAvailableModels: async () => {
    const response = await api.get('/settings/models');
    return response.data;
  }
};

// Feedback API
export const feedbackAPI = {
  // 피드백 제출
  submitFeedback: async (feedbackData) => {
    const response = await api.post('/feedback', feedbackData);
    return response.data;
  },

  // 피드백 통계
  getFeedbackStats: async () => {
    const response = await api.get('/feedback/stats');
    return response.data;
  },

  // 최근 피드백
  getRecentFeedback: async (limit = 20) => {
    const response = await api.get('/feedback/recent', {
      params: { limit }
    });
    return response.data;
  },

  // 개선 제안
  getImprovements: async () => {
    const response = await api.get('/feedback/improvements');
    return response.data;
  }
};

export default api;
