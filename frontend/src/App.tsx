/**
 * Main App Component
 */
import React from 'react'
import { Box, CssBaseline, ThemeProvider, createTheme, AppBar, Toolbar, Typography, IconButton } from '@mui/material'
import { Menu as MenuIcon } from '@mui/icons-material'
import { Sidebar } from './components/Chat/Sidebar'
import { ChatArea } from './components/Chat/ChatArea'
import { ChatInput } from './components/Chat/ChatInput'
import { SettingsDialog } from './components/Settings/SettingsDialog'
import { useChatStore } from './store/chatStore'

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
      '"Apple Color Emoji"',
      '"Segoe UI Emoji"',
      '"Segoe UI Symbol"',
    ].join(','),
  },
  shape: {
    borderRadius: 8,
  },
})

function App() {
  const { toggleSidebar, sidebarOpen } = useChatStore()

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        <Sidebar />
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          {/* App Bar */}
          <AppBar
            position="static"
            elevation={1}
            sx={{
              zIndex: (theme) => theme.zIndex.drawer + 1,
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                edge="start"
                onClick={toggleSidebar}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Enterprise Chatbot - 반도체 부품 관리 AI
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                LangGraph | RAG | Multi-Agent
              </Typography>
            </Toolbar>
          </AppBar>

          {/* Main Chat Area */}
          <ChatArea />

          {/* Input Area */}
          <ChatInput />
        </Box>

        {/* Settings Dialog */}
        <SettingsDialog />
      </Box>
    </ThemeProvider>
  )
}

export default App
