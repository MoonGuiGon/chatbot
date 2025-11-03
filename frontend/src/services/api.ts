/**
 * API Service
 */
import axios from 'axios'
import type {
  Conversation,
  Message,
  UserSettings,
  Feedback,
  MaterialData,
  StreamEvent
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Chat API
export const chatApi = {
  async sendQuery(query: string, userId: number = 1, conversationId?: number) {
    const response = await api.post('/api/chat/query', {
      query,
      user_id: userId,
      conversation_id: conversationId,
    })
    return response.data
  },

  streamQuery(
    query: string,
    userId: number = 1,
    conversationId?: number,
    onEvent: (event: StreamEvent) => void
  ) {
    const eventSource = new EventSource(
      `${API_BASE_URL}/api/chat/query/stream?query=${encodeURIComponent(query)}&user_id=${userId}${
        conversationId ? `&conversation_id=${conversationId}` : ''
      }`
    )

    // For POST with streaming, we need a different approach
    // Using fetch API with streaming
    return fetch(`${API_BASE_URL}/api/chat/query/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        user_id: userId,
        conversation_id: conversationId,
      }),
    }).then(async (response) => {
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) throw new Error('No reader available')

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              onEvent(data)
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }
    })
  },
}

// Conversation API
export const conversationApi = {
  async getConversations(userId: number = 1): Promise<{ conversations: Conversation[] }> {
    const response = await api.get('/api/conversations/', {
      params: { user_id: userId },
    })
    return response.data
  },

  async getConversation(conversationId: number): Promise<Conversation> {
    const response = await api.get(`/api/conversations/${conversationId}`)
    return response.data
  },

  async createConversation(userId: number = 1, title: string = 'New Conversation') {
    const response = await api.post('/api/conversations/', {
      user_id: userId,
      title,
    })
    return response.data
  },

  async updateConversation(conversationId: number, title: string) {
    const response = await api.put(`/api/conversations/${conversationId}`, {
      title,
    })
    return response.data
  },

  async deleteConversation(conversationId: number) {
    const response = await api.delete(`/api/conversations/${conversationId}`)
    return response.data
  },
}

// Settings API
export const settingsApi = {
  async getSettings(userId: number = 1): Promise<UserSettings> {
    const response = await api.get(`/api/settings/${userId}`)
    return response.data
  },

  async updateSettings(
    userId: number = 1,
    settings: { custom_prompts?: string[]; preferences?: Record<string, any> }
  ) {
    const response = await api.put(`/api/settings/${userId}`, settings)
    return response.data
  },

  async addCustomPrompt(userId: number = 1, prompt: string) {
    const response = await api.post(`/api/settings/${userId}/prompts`, { prompt })
    return response.data
  },

  async deleteCustomPrompt(userId: number = 1, index: number) {
    const response = await api.delete(`/api/settings/${userId}/prompts/${index}`)
    return response.data
  },
}

// Feedback API
export const feedbackApi = {
  async submitFeedback(userId: number = 1, feedback: Feedback) {
    const response = await api.post('/api/feedback/', {
      user_id: userId,
      ...feedback,
    })
    return response.data
  },

  async getFeedbackStats(userId?: number) {
    const response = await api.get('/api/feedback/stats', {
      params: userId ? { user_id: userId } : {},
    })
    return response.data
  },

  async getKnowledgeEntries(limit: number = 50) {
    const response = await api.get('/api/feedback/knowledge', {
      params: { limit },
    })
    return response.data
  },
}

// Export API
export const exportApi = {
  async exportMaterialData(materials: MaterialData[]) {
    const response = await api.post(
      '/api/export/material',
      { materials },
      { responseType: 'blob' }
    )
    return response.data
  },

  async exportConversation(conversationId: number) {
    const response = await api.get(`/api/export/conversation/${conversationId}`, {
      responseType: 'blob',
    })
    return response.data
  },

  async downloadDocument(source: string, type: string = 'pdf') {
    const response = await api.post('/api/export/document', { source, type })
    return response.data
  },
}

export default api
