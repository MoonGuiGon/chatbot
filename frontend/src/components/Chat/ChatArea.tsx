/**
 * Main Chat Area Component
 */
import React, { useEffect, useRef } from 'react'
import { Box, Container } from '@mui/material'
import { MessageBubble } from './MessageBubble'
import { ProgressIndicator } from './ProgressIndicator'
import { useChatStore } from '../../store/chatStore'

export const ChatArea: React.FC = () => {
  const { messages, isStreaming, currentProgress } = useChatStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentProgress])

  return (
    <Box
      sx={{
        flexGrow: 1,
        overflowY: 'auto',
        p: 3,
        backgroundColor: 'grey.50',
      }}
    >
      <Container maxWidth="lg">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <ProgressIndicator steps={currentProgress} show={isStreaming} />
        <div ref={messagesEndRef} />
      </Container>
    </Box>
  )
}
