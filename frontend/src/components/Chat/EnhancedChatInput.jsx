/**
 * Enhanced Chat Input with Voice, File Upload, and Shortcuts
 */
import { useState, useRef, useEffect, useCallback } from 'react'
import PropTypes from 'prop-types'
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Container,
  Tooltip,
  Chip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Badge,
  CircularProgress,
} from '@mui/material'
import {
  Send,
  Stop,
  AttachFile,
  Code,
  Description,
} from '@mui/icons-material'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { useChatStore } from '../../store/chatStore'

export const EnhancedChatInput = () => {
  const [input, setInput] = useState('')
  const [attachedFiles, setAttachedFiles] = useState([])
  const [menuAnchor, setMenuAnchor] = useState(null)
  const inputRef = useRef(null)

  const {
    sendMessageStream,
    isStreaming,
    isLoading,
    currentConversation,
    createNewConversation,
  } = useChatStore()

  // File dropzone
  const onDrop = useCallback((acceptedFiles) => {
    setAttachedFiles((prev) => [...prev, ...acceptedFiles])
    toast.success(`${acceptedFiles.length}개 파일 추가됨`)
  }, [])

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    noClick: true,
    noKeyboard: true,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc', '.docx'],
      'application/vnd.ms-excel': ['.xls', '.xlsx'],
    },
  })

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Cmd/Ctrl + K: Focus input
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
      // Cmd/Ctrl + Enter: Send message
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault()
        handleSend()
      }
      // Esc: Clear input
      if (e.key === 'Escape') {
        setInput('')
        setAttachedFiles([])
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [input])

  const handleSend = async () => {
    if (!input.trim() && attachedFiles.length === 0) return
    if (isStreaming || isLoading) return

    const message = input.trim()
    setInput('')
    setAttachedFiles([])

    // Create conversation if none exists
    if (!currentConversation) {
      await createNewConversation()
    }

    // TODO: Handle file uploads
    if (attachedFiles.length > 0) {
      toast('파일 업로드 기능은 곧 지원됩니다', { icon: '📎' })
    }

    // Send message with streaming
    await sendMessageStream(message)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const removeFile = (index) => {
    setAttachedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const insertTemplate = (template) => {
    setInput((prev) => prev + template)
    setMenuAnchor(null)
    inputRef.current?.focus()
  }

  return (
    <Paper
      elevation={3}
      sx={{
        borderTop: 1,
        borderColor: 'divider',
        p: 2,
        backgroundColor: 'background.paper',
      }}
      {...getRootProps()}
    >
      <Container maxWidth="lg">
        {/* Drag overlay */}
        <AnimatePresence>
          {isDragActive && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(25, 118, 210, 0.1)',
                border: '3px dashed',
                borderColor: 'primary.main',
                zIndex: 9999,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Box sx={{ textAlign: 'center' }}>
                <AttachFile sx={{ fontSize: 60, color: 'primary.main' }} />
                <Typography variant="h6" color="primary">
                  파일을 여기에 드롭하세요
                </Typography>
              </Box>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Attached files */}
        {attachedFiles.length > 0 && (
          <Box sx={{ mb: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {attachedFiles.map((file, index) => (
              <Chip
                key={index}
                label={file.name}
                onDelete={() => removeFile(index)}
                size="small"
                icon={<AttachFile />}
              />
            ))}
          </Box>
        )}

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          {/* Template menu */}
          <Tooltip title="템플릿">
            <IconButton
              size="small"
              onClick={(e) => setMenuAnchor(e.currentTarget)}
              color="primary"
            >
              <Code />
            </IconButton>
          </Tooltip>

          <Menu
            anchorEl={menuAnchor}
            open={Boolean(menuAnchor)}
            onClose={() => setMenuAnchor(null)}
          >
            <MenuItem onClick={() => insertTemplate('MAT-001의 현재 재고는?')}>
              <ListItemIcon>
                <Description />
              </ListItemIcon>
              <ListItemText primary="재고 조회" secondary="부품 재고 확인" />
            </MenuItem>
            <MenuItem onClick={() => insertTemplate('```python\n\n```')}>
              <ListItemIcon>
                <Code />
              </ListItemIcon>
              <ListItemText primary="코드 블록" secondary="코드 입력" />
            </MenuItem>
          </Menu>

          {/* File attach */}
          <Tooltip title="파일 첨부">
            <IconButton size="small" onClick={open} color="primary">
              <Badge badgeContent={attachedFiles.length} color="error">
                <AttachFile />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* Main input */}
          <TextField
            inputRef={inputRef}
            fullWidth
            multiline
            maxRows={6}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요... (Shift+Enter로 줄바꿈)"
            disabled={isStreaming || isLoading}
            variant="outlined"
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
              },
            }}
          />

          {/* Send button */}
          <Tooltip title={isStreaming ? '중지 (Esc)' : '전송 (Cmd+Enter)'}>
            <IconButton
              onClick={handleSend}
              disabled={(!input.trim() && attachedFiles.length === 0 && !isStreaming) || isLoading}
              sx={{
                backgroundColor: 'primary.main',
                color: 'white',
                width: 48,
                height: 48,
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

        {/* Shortcuts hint */}
        <Box
          sx={{
            mt: 1,
            display: 'flex',
            gap: 2,
            flexWrap: 'wrap',
          }}
        >
          <Typography variant="caption" color="text.secondary">
            💡 Cmd+K: 포커스 | Cmd+Enter: 전송 | Shift+Enter: 줄바꿈 | Esc: 초기화
          </Typography>
        </Box>
      </Container>
      <input {...getInputProps()} />
    </Paper>
  )
}

EnhancedChatInput.propTypes = {}
