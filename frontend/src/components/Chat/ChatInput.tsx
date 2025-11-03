/**
 * Chat Input Component
 */
import React, { useState, useRef } from 'react'
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Container,
  Tooltip,
} from '@mui/material'
import { Send, Stop } from '@mui/icons-material'
import { useChatStore } from '../../store/chatStore'

export const ChatInput: React.FC = () => {
  const [input, setInput] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const { sendMessageStream, isStreaming, isLoading, currentConversation, createNewConversation } =
    useChatStore()

  const handleSend = async () => {
    if (!input.trim() || isStreaming || isLoading) return

    const message = input.trim()
    setInput('')

    // Create conversation if none exists
    if (!currentConversation) {
      await createNewConversation()
    }

    // Send message with streaming
    await sendMessageStream(message)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Paper
      elevation={3}
      sx={{
        borderTop: 1,
        borderColor: 'divider',
        p: 2,
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            inputRef={inputRef}
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요..."
            disabled={isStreaming || isLoading}
            variant="outlined"
            size="small"
          />
          <Tooltip title={isStreaming ? '중지' : '전송'}>
            <IconButton
              color="primary"
              onClick={handleSend}
              disabled={(!input.trim() && !isStreaming) || isLoading}
              sx={{
                backgroundColor: 'primary.main',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                },
                '&:disabled': {
                  backgroundColor: 'grey.300',
                },
              }}
            >
              {isStreaming ? <Stop /> : <Send />}
            </IconButton>
          </Tooltip>
        </Box>
      </Container>
    </Paper>
  )
}
