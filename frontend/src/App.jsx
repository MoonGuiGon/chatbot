/**
 * Main App Component - Enhanced Version
 */
import { useState, useEffect } from 'react'
import {
  Box,
  CssBaseline,
  ThemeProvider,
  createTheme,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  useMediaQuery,
  Fab,
  Zoom,
  Drawer,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Chat as ChatIcon,
  KeyboardArrowUp,
} from '@mui/icons-material'
import { Toaster } from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'
import { Sidebar } from './components/Chat/Sidebar'
import { ChatArea } from './components/Chat/ChatArea'
import { EnhancedChatInput } from './components/Chat/EnhancedChatInput'
import { SettingsDialog } from './components/Settings/SettingsDialog'
import { AnalyticsDashboard } from './components/Dashboard/AnalyticsDashboard'
import { useChatStore } from './store/chatStore'

// Enhanced theme with modern design
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#e3f2fd',
      dark: '#0d47a1',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
    success: {
      main: '#2e7d32',
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
    ].join(','),
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          transition: 'box-shadow 0.3s',
          '&:hover': {
            boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
          },
        },
      },
    },
  },
})

function App() {
  const [showDashboard, setShowDashboard] = useState(false)
  const [showScrollTop, setShowScrollTop] = useState(false)
  const { toggleSidebar, sidebarOpen } = useChatStore()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  // Scroll to top functionality
  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 300)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            borderRadius: '12px',
            background: '#333',
            color: '#fff',
          },
          success: {
            iconTheme: {
              primary: '#4caf50',
              secondary: '#fff',
            },
          },
        }}
      />

      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        {/* Sidebar */}
        {isMobile ? (
          <Drawer
            anchor="left"
            open={sidebarOpen}
            onClose={toggleSidebar}
            sx={{ '& .MuiDrawer-paper': { width: 280 } }}
          >
            <Sidebar />
          </Drawer>
        ) : (
          <Sidebar />
        )}

        {/* Main Content */}
        <Box
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* App Bar */}
          <AppBar
            position="static"
            elevation={1}
            sx={{
              backgroundColor: 'background.paper',
              color: 'text.primary',
              borderBottom: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Toolbar>
              <IconButton
                edge="start"
                onClick={toggleSidebar}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>

              <Box
                component={motion.div}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 2 }}
              >
                <Typography variant="h6" component="div">
                  Enterprise AI Chatbot
                </Typography>
                <Box
                  sx={{
                    display: 'flex',
                    gap: 0.5,
                    alignItems: 'center',
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      px: 1,
                      py: 0.5,
                      backgroundColor: 'primary.light',
                      borderRadius: 1,
                      fontWeight: 600,
                    }}
                  >
                    멀티모달 RAG
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      px: 1,
                      py: 0.5,
                      backgroundColor: 'success.light',
                      borderRadius: 1,
                      fontWeight: 600,
                    }}
                  >
                    Knowledge Graph
                  </Typography>
                </Box>
              </Box>

              <IconButton
                onClick={() => setShowDashboard(!showDashboard)}
                color={showDashboard ? 'primary' : 'default'}
              >
                {showDashboard ? <ChatIcon /> : <DashboardIcon />}
              </IconButton>
            </Toolbar>
          </AppBar>

          {/* Content Area */}
          <AnimatePresence mode="wait">
            {showDashboard ? (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                style={{ flexGrow: 1, overflow: 'auto' }}
              >
                <AnalyticsDashboard />
              </motion.div>
            ) : (
              <motion.div
                key="chat"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                style={{
                  flexGrow: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  overflow: 'hidden',
                }}
              >
                <ChatArea />
                <EnhancedChatInput />
              </motion.div>
            )}
          </AnimatePresence>
        </Box>

        {/* Settings Dialog */}
        <SettingsDialog />

        {/* Scroll to Top Button */}
        <Zoom in={showScrollTop}>
          <Fab
            color="primary"
            size="small"
            onClick={scrollToTop}
            sx={{
              position: 'fixed',
              bottom: 80,
              right: 16,
            }}
          >
            <KeyboardArrowUp />
          </Fab>
        </Zoom>
      </Box>
    </ThemeProvider>
  )
}

export default App
