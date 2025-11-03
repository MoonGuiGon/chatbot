/**
 * Message Bubble Component
 */
import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Chip,
  Collapse,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Rating,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  ThumbUp,
  ThumbDown,
  ContentCopy,
  ExpandMore,
  ExpandLess,
  Download,
  Storage,
  Description,
} from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Message, Source, MaterialData } from '../../types'
import { useChatStore } from '../../store/chatStore'

interface MessageBubbleProps {
  message: Message
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const [showSources, setShowSources] = useState(false)
  const [feedbackOpen, setFeedbackOpen] = useState(false)
  const [rating, setRating] = useState<number>(0)
  const [comment, setComment] = useState('')

  const { submitFeedback, exportMaterialData } = useChatStore()

  const isUser = message.role === 'user'
  const sources = message.metadata?.sources || []
  const materialData = message.metadata?.material_data || []

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
  }

  const handleFeedback = async (positive: boolean) => {
    await submitFeedback(message.id, positive ? 5 : 1)
  }

  const handleDetailedFeedback = async () => {
    if (rating > 0) {
      await submitFeedback(message.id, rating, comment)
      setFeedbackOpen(false)
      setRating(0)
      setComment('')
    }
  }

  const handleExportMaterial = () => {
    if (materialData.length > 0) {
      exportMaterialData(materialData)
    }
  }

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Paper
        elevation={1}
        sx={{
          maxWidth: '75%',
          p: 2,
          backgroundColor: isUser ? 'primary.light' : 'background.paper',
          borderRadius: 2,
        }}
      >
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>

        {/* Material Data Table */}
        {!isUser && materialData.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center' }}>
                <Storage sx={{ mr: 1, fontSize: 18 }} />
                부품 정보
              </Typography>
              <Button
                size="small"
                startIcon={<Download />}
                onClick={handleExportMaterial}
              >
                Excel 다운로드
              </Button>
            </Box>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>자재코드</TableCell>
                    <TableCell>부품명</TableCell>
                    <TableCell>카테고리</TableCell>
                    <TableCell>현재재고</TableCell>
                    <TableCell>최소재고</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {materialData.map((mat: MaterialData) => (
                    <TableRow key={mat.materialId}>
                      <TableCell>{mat.materialId}</TableCell>
                      <TableCell>{mat.name}</TableCell>
                      <TableCell>{mat.category}</TableCell>
                      <TableCell>
                        {mat.inventory?.current_stock || '-'}
                      </TableCell>
                      <TableCell>
                        {mat.inventory?.minimum_stock || '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* Sources */}
        {!isUser && sources.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                cursor: 'pointer',
                '&:hover': { opacity: 0.8 },
              }}
              onClick={() => setShowSources(!showSources)}
            >
              <Typography variant="caption" sx={{ mr: 1 }}>
                출처 ({sources.length})
              </Typography>
              {showSources ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
            </Box>
            <Collapse in={showSources}>
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {sources.map((source: Source, idx: number) => (
                  <Chip
                    key={idx}
                    label={
                      source.type === 'mongodb'
                        ? `MongoDB: ${source.material_id}`
                        : `문서: ${source.source}`
                    }
                    size="small"
                    icon={source.type === 'mongodb' ? <Storage /> : <Description />}
                    sx={{ fontSize: '0.75rem' }}
                  />
                ))}
              </Box>
            </Collapse>
          </Box>
        )}

        {/* Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 0.5, mt: 1 }}>
          <IconButton size="small" onClick={handleCopy} title="복사">
            <ContentCopy fontSize="small" />
          </IconButton>
          {!isUser && (
            <>
              <IconButton
                size="small"
                color="success"
                onClick={() => handleFeedback(true)}
                title="좋아요"
              >
                <ThumbUp fontSize="small" />
              </IconButton>
              <IconButton
                size="small"
                color="error"
                onClick={() => setFeedbackOpen(true)}
                title="피드백"
              >
                <ThumbDown fontSize="small" />
              </IconButton>
            </>
          )}
        </Box>
      </Paper>

      {/* Feedback Dialog */}
      <Dialog open={feedbackOpen} onClose={() => setFeedbackOpen(false)}>
        <DialogTitle>피드백 제공</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              평가:
            </Typography>
            <Rating
              value={rating}
              onChange={(_, value) => setRating(value || 0)}
            />
          </Box>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="의견 (선택사항)"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackOpen(false)}>취소</Button>
          <Button
            onClick={handleDetailedFeedback}
            variant="contained"
            disabled={rating === 0}
          >
            제출
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
