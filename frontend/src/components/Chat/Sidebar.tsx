/**
 * Sidebar Component - Conversation List
 */
import React, { useEffect } from 'react'
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  IconButton,
  Typography,
  Button,
  Divider,
} from '@mui/material'
import {
  Add,
  Delete,
  Settings,
} from '@mui/icons-material'
import { useChatStore } from '../../store/chatStore'
import dayjs from 'dayjs'
import 'dayjs/locale/ko'

dayjs.locale('ko')

const DRAWER_WIDTH = 280

export const Sidebar: React.FC = () => {
  const {
    conversations,
    currentConversation,
    sidebarOpen,
    loadConversations,
    selectConversation,
    createNewConversation,
    deleteConversation,
    toggleSettings,
  } = useChatStore()

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={sidebarOpen}
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Button
          fullWidth
          variant="contained"
          startIcon={<Add />}
          onClick={createNewConversation}
          sx={{ mb: 2 }}
        >
          새 대화
        </Button>

        <Button
          fullWidth
          variant="outlined"
          startIcon={<Settings />}
          onClick={toggleSettings}
        >
          설정
        </Button>
      </Box>

      <Divider />

      <List sx={{ flexGrow: 1, overflowY: 'auto' }}>
        {conversations.map((conv) => (
          <ListItem
            key={conv.id}
            disablePadding
            secondaryAction={
              <IconButton
                edge="end"
                size="small"
                onClick={(e) => {
                  e.stopPropagation()
                  deleteConversation(conv.id)
                }}
              >
                <Delete fontSize="small" />
              </IconButton>
            }
          >
            <ListItemButton
              selected={currentConversation?.id === conv.id}
              onClick={() => selectConversation(conv.id)}
            >
              <ListItemText
                primary={
                  <Typography variant="body2" noWrap>
                    {conv.title}
                  </Typography>
                }
                secondary={
                  <Typography variant="caption" color="text.secondary">
                    {dayjs(conv.updated_at).format('MM/DD HH:mm')}
                  </Typography>
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
          Enterprise Chatbot v1.0
        </Typography>
      </Box>
    </Drawer>
  )
}
