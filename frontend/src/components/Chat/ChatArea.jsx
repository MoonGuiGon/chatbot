import React, { useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import MessageBubble from './MessageBubble';
import ProgressIndicator from './ProgressIndicator';
import useChatStore from '../../store/chatStore';

const ChatArea = () => {
  const { messages, isLoading, progress } = useChatStore();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, progress]);

  return (
    <Box
      sx={{
        flex: 1,
        overflow: 'auto',
        p: 2,
        bgcolor: 'background.default'
      }}
    >
      {messages.map((message, index) => (
        <MessageBubble
          key={index}
          message={message}
          isUser={message.role === 'user'}
        />
      ))}

      {/* 진행 상황 표시 */}
      {isLoading && <ProgressIndicator progress={progress} />}

      <div ref={messagesEndRef} />
    </Box>
  );
};

export default ChatArea;
