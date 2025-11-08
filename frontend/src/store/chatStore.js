import { create } from 'zustand';

const useChatStore = create((set, get) => ({
  // 대화 상태
  conversations: [],
  currentConversationId: null,
  messages: [],
  isLoading: false,
  progress: [],

  // 설정
  settings: {
    model: 'gpt-4',
    temperature: 0.1,
    maxTokens: 2000,
    customPrompt: ''
  },

  // UI 상태
  sidebarOpen: true,
  settingsOpen: false,

  // Actions
  setCurrentConversation: (conversationId) => {
    set({ currentConversationId: conversationId });
  },

  addMessage: (message) => {
    set((state) => ({
      messages: [...state.messages, message]
    }));
  },

  setMessages: (messages) => {
    set({ messages });
  },

  setLoading: (isLoading) => {
    set({ isLoading });
  },

  setProgress: (progress) => {
    set({ progress });
  },

  addProgress: (progressItem) => {
    set((state) => ({
      progress: [...state.progress, progressItem]
    }));
  },

  clearProgress: () => {
    set({ progress: [] });
  },

  updateSettings: (newSettings) => {
    set((state) => ({
      settings: { ...state.settings, ...newSettings }
    }));
  },

  toggleSidebar: () => {
    set((state) => ({ sidebarOpen: !state.sidebarOpen }));
  },

  toggleSettings: () => {
    set((state) => ({ settingsOpen: !state.settingsOpen }));
  },

  setConversations: (conversations) => {
    set({ conversations });
  },

  addConversation: (conversation) => {
    set((state) => ({
      conversations: [conversation, ...state.conversations]
    }));
  },

  // 새 대화 시작
  startNewConversation: () => {
    set({
      currentConversationId: null,
      messages: [],
      progress: []
    });
  }
}));

export default useChatStore;
