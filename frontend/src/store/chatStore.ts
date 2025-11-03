/**
 * Chat Store using Zustand
 */
import { create } from 'zustand'
import type {
  Conversation,
  Message,
  ProgressStep,
  UserSettings,
  MaterialData,
  Source,
} from '../types'
import {
  chatApi,
  conversationApi,
  settingsApi,
  feedbackApi,
  exportApi,
} from '../services/api'
import { saveAs } from 'file-saver'

interface ChatState {
  // User
  userId: number

  // Conversations
  conversations: Conversation[]
  currentConversation: Conversation | null
  messages: Message[]

  // Chat state
  isLoading: boolean
  isStreaming: boolean
  currentProgress: ProgressStep[]
  currentResponse: string
  currentSources: Source[]
  currentMaterialData: MaterialData[]

  // Settings
  userSettings: UserSettings | null

  // UI state
  sidebarOpen: boolean
  settingsOpen: boolean

  // Actions
  loadConversations: () => Promise<void>
  selectConversation: (conversationId: number) => Promise<void>
  createNewConversation: () => Promise<void>
  deleteConversation: (conversationId: number) => Promise<void>
  updateConversationTitle: (conversationId: number, title: string) => Promise<void>

  sendMessage: (query: string) => Promise<void>
  sendMessageStream: (query: string) => Promise<void>

  loadSettings: () => Promise<void>
  updateSettings: (settings: Partial<UserSettings>) => Promise<void>
  addCustomPrompt: (prompt: string) => Promise<void>
  deleteCustomPrompt: (index: number) => Promise<void>

  submitFeedback: (messageId: number, rating: number, comment?: string) => Promise<void>

  exportMaterialData: (materials: MaterialData[]) => Promise<void>
  exportConversation: (conversationId: number) => Promise<void>

  toggleSidebar: () => void
  toggleSettings: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  userId: 1,
  conversations: [],
  currentConversation: null,
  messages: [],
  isLoading: false,
  isStreaming: false,
  currentProgress: [],
  currentResponse: '',
  currentSources: [],
  currentMaterialData: [],
  userSettings: null,
  sidebarOpen: true,
  settingsOpen: false,

  // Load conversations
  loadConversations: async () => {
    try {
      const data = await conversationApi.getConversations(get().userId)
      set({ conversations: data.conversations })
    } catch (error) {
      console.error('Failed to load conversations:', error)
    }
  },

  // Select conversation
  selectConversation: async (conversationId: number) => {
    try {
      set({ isLoading: true })
      const conversation = await conversationApi.getConversation(conversationId)
      set({
        currentConversation: conversation,
        messages: conversation.messages || [],
        isLoading: false,
      })
    } catch (error) {
      console.error('Failed to load conversation:', error)
      set({ isLoading: false })
    }
  },

  // Create new conversation
  createNewConversation: async () => {
    try {
      const data = await conversationApi.createConversation(get().userId)
      const newConv: Conversation = {
        id: data.id,
        user_id: get().userId,
        title: data.title,
        created_at: data.created_at,
        updated_at: data.created_at,
      }
      set({
        conversations: [newConv, ...get().conversations],
        currentConversation: newConv,
        messages: [],
      })
    } catch (error) {
      console.error('Failed to create conversation:', error)
    }
  },

  // Delete conversation
  deleteConversation: async (conversationId: number) => {
    try {
      await conversationApi.deleteConversation(conversationId)
      set({
        conversations: get().conversations.filter((c) => c.id !== conversationId),
      })
      if (get().currentConversation?.id === conversationId) {
        set({ currentConversation: null, messages: [] })
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
  },

  // Update conversation title
  updateConversationTitle: async (conversationId: number, title: string) => {
    try {
      await conversationApi.updateConversation(conversationId, title)
      set({
        conversations: get().conversations.map((c) =>
          c.id === conversationId ? { ...c, title } : c
        ),
      })
      if (get().currentConversation?.id === conversationId) {
        set({
          currentConversation: { ...get().currentConversation!, title },
        })
      }
    } catch (error) {
      console.error('Failed to update conversation title:', error)
    }
  },

  // Send message (non-streaming)
  sendMessage: async (query: string) => {
    try {
      set({ isLoading: true })

      const conversationId = get().currentConversation?.id

      const result = await chatApi.sendQuery(query, get().userId, conversationId)

      // Add user message
      const userMessage: Message = {
        id: Date.now(),
        role: 'user',
        content: query,
        created_at: new Date().toISOString(),
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: result.response,
        metadata: {
          sources: result.sources,
          query_intent: result.query_intent,
        },
        created_at: new Date().toISOString(),
      }

      set({
        messages: [...get().messages, userMessage, assistantMessage],
        isLoading: false,
        currentConversation: result.conversation_id
          ? { ...get().currentConversation!, id: result.conversation_id }
          : get().currentConversation,
      })

      // Reload conversations to update list
      await get().loadConversations()
    } catch (error) {
      console.error('Failed to send message:', error)
      set({ isLoading: false })
    }
  },

  // Send message with streaming
  sendMessageStream: async (query: string) => {
    try {
      set({
        isStreaming: true,
        currentProgress: [],
        currentResponse: '',
        currentSources: [],
        currentMaterialData: [],
      })

      // Add user message immediately
      const userMessage: Message = {
        id: Date.now(),
        role: 'user',
        content: query,
        created_at: new Date().toISOString(),
      }
      set({ messages: [...get().messages, userMessage] })

      const conversationId = get().currentConversation?.id

      await chatApi.streamQuery(query, get().userId, conversationId, (event) => {
        if (event.type === 'progress') {
          set({
            currentProgress: [
              ...get().currentProgress,
              {
                step: event.step || '',
                status: event.status as any,
                message: event.message || '',
              },
            ],
          })
        } else if (event.type === 'response') {
          // Add assistant message
          const assistantMessage: Message = {
            id: Date.now() + 1,
            role: 'assistant',
            content: event.response || '',
            metadata: {
              sources: event.sources,
              query_intent: event.query_intent,
              material_data: event.material_data,
            },
            created_at: new Date().toISOString(),
          }

          set({
            messages: [...get().messages, assistantMessage],
            currentResponse: event.response || '',
            currentSources: event.sources || [],
            currentMaterialData: event.material_data || [],
            isStreaming: false,
          })

          // Reload conversations
          get().loadConversations()
        } else if (event.type === 'error') {
          console.error('Stream error:', event.message)
          set({ isStreaming: false })
        }
      })
    } catch (error) {
      console.error('Failed to stream message:', error)
      set({ isStreaming: false })
    }
  },

  // Load settings
  loadSettings: async () => {
    try {
      const settings = await settingsApi.getSettings(get().userId)
      set({ userSettings: settings })
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  },

  // Update settings
  updateSettings: async (settings: Partial<UserSettings>) => {
    try {
      const updated = await settingsApi.updateSettings(get().userId, settings)
      set({ userSettings: updated })
    } catch (error) {
      console.error('Failed to update settings:', error)
    }
  },

  // Add custom prompt
  addCustomPrompt: async (prompt: string) => {
    try {
      const result = await settingsApi.addCustomPrompt(get().userId, prompt)
      set({
        userSettings: {
          ...get().userSettings!,
          custom_prompts: result.custom_prompts,
        },
      })
    } catch (error) {
      console.error('Failed to add custom prompt:', error)
    }
  },

  // Delete custom prompt
  deleteCustomPrompt: async (index: number) => {
    try {
      const result = await settingsApi.deleteCustomPrompt(get().userId, index)
      set({
        userSettings: {
          ...get().userSettings!,
          custom_prompts: result.custom_prompts,
        },
      })
    } catch (error) {
      console.error('Failed to delete custom prompt:', error)
    }
  },

  // Submit feedback
  submitFeedback: async (messageId: number, rating: number, comment?: string) => {
    try {
      await feedbackApi.submitFeedback(get().userId, {
        message_id: messageId,
        rating,
        comment,
      })
    } catch (error) {
      console.error('Failed to submit feedback:', error)
    }
  },

  // Export material data
  exportMaterialData: async (materials: MaterialData[]) => {
    try {
      const blob = await exportApi.exportMaterialData(materials)
      saveAs(blob, `material_data_${Date.now()}.xlsx`)
    } catch (error) {
      console.error('Failed to export material data:', error)
    }
  },

  // Export conversation
  exportConversation: async (conversationId: number) => {
    try {
      const blob = await exportApi.exportConversation(conversationId)
      saveAs(blob, `conversation_${conversationId}_${Date.now()}.txt`)
    } catch (error) {
      console.error('Failed to export conversation:', error)
    }
  },

  // Toggle sidebar
  toggleSidebar: () => {
    set({ sidebarOpen: !get().sidebarOpen })
  },

  // Toggle settings
  toggleSettings: () => {
    set({ settingsOpen: !get().settingsOpen })
  },
}))
