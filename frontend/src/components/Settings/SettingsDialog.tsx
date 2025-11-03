/**
 * Settings Dialog Component
 */
import React, { useEffect, useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  TextField,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Chip,
  Divider,
  Alert,
} from '@mui/material'
import { Delete, Add } from '@mui/icons-material'
import { useChatStore } from '../../store/chatStore'

export const SettingsDialog: React.FC = () => {
  const { settingsOpen, toggleSettings, userSettings, loadSettings, addCustomPrompt, deleteCustomPrompt } =
    useChatStore()

  const [newPrompt, setNewPrompt] = useState('')

  useEffect(() => {
    if (settingsOpen && !userSettings) {
      loadSettings()
    }
  }, [settingsOpen, userSettings, loadSettings])

  const handleAddPrompt = async () => {
    if (newPrompt.trim()) {
      await addCustomPrompt(newPrompt.trim())
      setNewPrompt('')
    }
  }

  const handleDeletePrompt = async (index: number) => {
    await deleteCustomPrompt(index)
  }

  return (
    <Dialog
      open={settingsOpen}
      onClose={toggleSettings}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>설정</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            맞춤 프롬프트
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            모든 질문에 자동으로 적용될 맞춤 지침을 추가하세요.
          </Typography>

          <Alert severity="info" sx={{ mb: 2 }}>
            예시: "답변은 항상 구체적인 숫자와 날짜를 포함해주세요"
          </Alert>

          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              fullWidth
              size="small"
              value={newPrompt}
              onChange={(e) => setNewPrompt(e.target.value)}
              placeholder="새 프롬프트 입력..."
              onKeyPress={(e) => e.key === 'Enter' && handleAddPrompt()}
            />
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleAddPrompt}
              disabled={!newPrompt.trim()}
            >
              추가
            </Button>
          </Box>

          <List>
            {userSettings?.custom_prompts?.map((prompt, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  <IconButton
                    edge="end"
                    onClick={() => handleDeletePrompt(index)}
                  >
                    <Delete />
                  </IconButton>
                }
              >
                <ListItemText primary={prompt} />
              </ListItem>
            ))}
            {(!userSettings?.custom_prompts || userSettings.custom_prompts.length === 0) && (
              <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
                등록된 맞춤 프롬프트가 없습니다.
              </Typography>
            )}
          </List>
        </Box>

        <Divider sx={{ my: 3 }} />

        <Box>
          <Typography variant="h6" gutterBottom>
            시스템 정보
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Chip label="버전: 1.0.0" size="small" />
            <Chip label="LangGraph 기반 멀티 에이전트" size="small" />
            <Chip label="스트리밍 응답 지원" size="small" />
            <Chip label="피드백 학습 시스템" size="small" />
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={toggleSettings}>닫기</Button>
      </DialogActions>
    </Dialog>
  )
}
