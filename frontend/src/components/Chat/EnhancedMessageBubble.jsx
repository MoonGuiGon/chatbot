/**
 * Enhanced Message Bubble with Multimodal Support
 */
import { useState } from 'react'
import PropTypes from 'prop-types'
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Chip,
  Collapse,
  Button,
  Rating,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Card,
  CardMedia,
  CardContent,
  Tooltip,
  Zoom,
  Fade,
  Avatar,
  Divider,
  Stack,
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
  Image as ImageIcon,
  PlayArrow,
  Code,
  TableChart,
  Check,
  SmartToy,
  Person,
} from '@mui/icons-material'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { motion } from 'framer-motion'
import { useChatStore } from '../../store/chatStore'
import { MaterialDataTable } from './MaterialDataTable'
import { VisionAnalysisCard } from './VisionAnalysisCard'
import { EnhancedChart } from './EnhancedChart'
import 'katex/dist/katex.min.css'

export const EnhancedMessageBubble = ({ message }) => {
  const [showSources, setShowSources] = useState(false)
  const [feedbackOpen, setFeedbackOpen] = useState(false)
  const [rating, setRating] = useState(0)
  const [comment, setComment] = useState('')
  const [copied, setCopied] = useState(false)
  const [imagePreview, setImagePreview] = useState(null)

  const { submitFeedback, exportMaterialData } = useChatStore()

  const isUser = message.role === 'user'
  const sources = message.metadata?.sources || []
  const materialData = message.metadata?.material_data || []
  const chartData = message.metadata?.chart_data || null
  const hasVisualAnalysis = sources.some((s) => s.has_visual_analysis)

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleFeedback = async (positive) => {
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

  // Custom markdown components
  const markdownComponents = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '')
      return !inline && match ? (
        <SyntaxHighlighter
          style={vscDarkPlus}
          language={match[1]}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code
          className={className}
          style={{
            backgroundColor: '#f5f5f5',
            padding: '2px 6px',
            borderRadius: '4px',
            fontSize: '0.9em',
          }}
          {...props}
        >
          {children}
        </code>
      )
    },
    table({ children }) {
      return (
        <Box sx={{ overflowX: 'auto', my: 2 }}>
          <table style={{ borderCollapse: 'collapse', width: '100%' }}>
            {children}
          </table>
        </Box>
      )
    },
    th({ children }) {
      return (
        <th
          style={{
            border: '1px solid #ddd',
            padding: '12px',
            backgroundColor: '#f5f5f5',
            fontWeight: 600,
            textAlign: 'left',
          }}
        >
          {children}
        </th>
      )
    },
    td({ children }) {
      return (
        <td
          style={{
            border: '1px solid #ddd',
            padding: '12px',
          }}
        >
          {children}
        </td>
      )
    },
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 3,
          gap: 1,
        }}
      >
        {!isUser && (
          <Avatar
            sx={{
              bgcolor: 'primary.main',
              width: 40,
              height: 40,
            }}
          >
            <SmartToy />
          </Avatar>
        )}

        <Paper
          elevation={isUser ? 1 : 3}
          sx={{
            maxWidth: '75%',
            p: 2.5,
            backgroundColor: isUser ? 'primary.light' : 'background.paper',
            borderRadius: 3,
            position: 'relative',
            '&::before': !isUser
              ? {
                  content: '""',
                  position: 'absolute',
                  left: -8,
                  top: 16,
                  width: 0,
                  height: 0,
                  borderTop: '8px solid transparent',
                  borderBottom: '8px solid transparent',
                  borderRight: '8px solid',
                  borderRightColor: 'background.paper',
                }
              : {},
          }}
        >
          {/* Message Content with Enhanced Markdown */}
          <ReactMarkdown
            remarkPlugins={[remarkGfm, remarkMath]}
            rehypePlugins={[rehypeKatex]}
            components={markdownComponents}
          >
            {message.content}
          </ReactMarkdown>

          {/* Vision Analysis Cards */}
          {!isUser &&
            hasVisualAnalysis &&
            sources
              .filter((s) => s.has_visual_analysis)
              .map((source, idx) => (
                <VisionAnalysisCard key={idx} source={source} />
              ))}

          {/* Chart */}
          {!isUser && chartData && (
            <EnhancedChart
              data={chartData.data}
              type={chartData.type || 'line'}
              title={chartData.title}
              xKey={chartData.xKey || 'name'}
              yKey={chartData.yKey || 'value'}
              height={chartData.height || 300}
            />
          )}

          {/* Material Data Table */}
          {!isUser && materialData.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <MaterialDataTable
                materials={materialData}
                onExport={handleExportMaterial}
              />
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
                <Typography variant="caption" sx={{ mr: 1, fontWeight: 500 }}>
                  출처 ({sources.length})
                </Typography>
                {showSources ? (
                  <ExpandLess fontSize="small" />
                ) : (
                  <ExpandMore fontSize="small" />
                )}
              </Box>
              <Collapse in={showSources}>
                <Stack spacing={1} sx={{ mt: 1 }}>
                  {sources.map((source, idx) => (
                    <Chip
                      key={idx}
                      label={
                        source.type === 'mongodb'
                          ? `MongoDB: ${source.material_id}`
                          : `${source.source}`
                      }
                      size="small"
                      icon={
                        source.type === 'mongodb' ? (
                          <Storage />
                        ) : source.has_visual_analysis ? (
                          <ImageIcon />
                        ) : (
                          <Description />
                        )
                      }
                      sx={{
                        fontSize: '0.75rem',
                        '& .MuiChip-icon': { fontSize: '1rem' },
                      }}
                      variant="outlined"
                    />
                  ))}
                </Stack>
              </Collapse>
            </Box>
          )}

          {/* Actions */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: 0.5,
              mt: 2,
              pt: 1,
              borderTop: !isUser ? '1px solid' : 'none',
              borderColor: 'divider',
            }}
          >
            <Tooltip title={copied ? 'Copied!' : 'Copy'} arrow>
              <IconButton size="small" onClick={handleCopy}>
                {copied ? <Check fontSize="small" /> : <ContentCopy fontSize="small" />}
              </IconButton>
            </Tooltip>
            {!isUser && (
              <>
                <Tooltip title="Good response" arrow>
                  <IconButton
                    size="small"
                    color="success"
                    onClick={() => handleFeedback(true)}
                  >
                    <ThumbUp fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Give feedback" arrow>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => setFeedbackOpen(true)}
                  >
                    <ThumbDown fontSize="small" />
                  </IconButton>
                </Tooltip>
              </>
            )}
          </Box>
        </Paper>

        {isUser && (
          <Avatar
            sx={{
              bgcolor: 'secondary.main',
              width: 40,
              height: 40,
            }}
          >
            <Person />
          </Avatar>
        )}
      </Box>

      {/* Feedback Dialog */}
      <Dialog
        open={feedbackOpen}
        onClose={() => setFeedbackOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>피드백 제공</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              평가:
            </Typography>
            <Rating
              value={rating}
              onChange={(_, value) => setRating(value || 0)}
              size="large"
            />
          </Box>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="의견 (선택사항)"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="어떤 점이 개선되면 좋을까요?"
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

      {/* Image Preview Dialog */}
      {imagePreview && (
        <Dialog
          open={Boolean(imagePreview)}
          onClose={() => setImagePreview(null)}
          maxWidth="lg"
        >
          <DialogContent>
            <img
              src={imagePreview}
              alt="Preview"
              style={{ width: '100%', height: 'auto' }}
            />
          </DialogContent>
        </Dialog>
      )}
    </motion.div>
  )
}

EnhancedMessageBubble.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.number.isRequired,
    role: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    metadata: PropTypes.object,
  }).isRequired,
}
