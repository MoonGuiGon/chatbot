import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Chip,
  Button,
  Collapse,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert
} from '@mui/material';
import {
  ThumbUp,
  ThumbDown,
  Download,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { feedbackAPI } from '../../services/api';

const MessageBubble = ({ message, isUser, onFeedback }) => {
  const [showSources, setShowSources] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const handleFeedback = async (type) => {
    if (feedbackSubmitted) return;

    try {
      await feedbackAPI.submitFeedback({
        conversation_id: message.conversationId,
        message_id: message.id,
        query: message.query,
        response: message.content,
        feedback_type: type,
        sources_used: message.sources || []
      });

      setFeedbackSubmitted(true);
      onFeedback && onFeedback(type);
    } catch (error) {
      console.error('Feedback submission error:', error);
    }
  };

  const handleDownloadSources = () => {
    // 출처 다운로드 로직
    const sourcesText = JSON.stringify(message.sources, null, 2);
    const blob = new Blob([sourcesText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sources.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderTable = (tableData) => {
    if (!tableData || tableData.length === 0) return null;

    const headers = Object.keys(tableData[0]);

    return (
      <TableContainer component={Paper} sx={{ my: 2 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {headers.map((header) => (
                <TableCell key={header} sx={{ fontWeight: 'bold' }}>
                  {header}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {tableData.map((row, idx) => (
              <TableRow key={idx}>
                {headers.map((header) => (
                  <TableCell key={header}>{row[header]}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderChart = (chartData) => {
    if (!chartData) return null;

    const { type, title, data } = chartData;

    if (type === 'bar') {
      return (
        <Box sx={{ my: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            {title}
          </Typography>
          <BarChart width={500} height={300} data={data.labels.map((label, idx) => ({
            name: label,
            ...data.datasets.reduce((acc, dataset, datasetIdx) => ({
              ...acc,
              [dataset.label]: dataset.data[idx]
            }), {})
          }))}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            {data.datasets.map((dataset, idx) => (
              <Bar key={idx} dataKey={dataset.label} fill={`hsl(${idx * 60}, 70%, 50%)`} />
            ))}
          </BarChart>
        </Box>
      );
    }

    if (type === 'line') {
      return (
        <Box sx={{ my: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            {title}
          </Typography>
          <LineChart width={500} height={300} data={data.labels.map((label, idx) => ({
            name: label,
            ...data.datasets.reduce((acc, dataset) => ({
              ...acc,
              [dataset.label]: dataset.data[idx]
            }), {})
          }))}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            {data.datasets.map((dataset, idx) => (
              <Line key={idx} type="monotone" dataKey={dataset.label} stroke={`hsl(${idx * 60}, 70%, 50%)`} />
            ))}
          </LineChart>
        </Box>
      );
    }

    return null;
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2
      }}
    >
      <Paper
        elevation={2}
        sx={{
          maxWidth: '70%',
          p: 2,
          bgcolor: isUser ? 'primary.main' : 'background.paper',
          color: isUser ? 'primary.contrastText' : 'text.primary'
        }}
      >
        {/* 메시지 내용 */}
        <ReactMarkdown>{message.content}</ReactMarkdown>

        {/* 표 렌더링 */}
        {message.tableData && renderTable(message.tableData)}

        {/* 그래프 렌더링 */}
        {message.chartData && renderChart(message.chartData)}

        {/* 경고 메시지 */}
        {message.warnings && message.warnings.length > 0 && (
          <Box sx={{ mt: 2 }}>
            {message.warnings.map((warning, idx) => (
              <Alert key={idx} severity="warning" sx={{ mb: 1 }}>
                {warning}
              </Alert>
            ))}
          </Box>
        )}

        {/* Assistant 메시지만 출처 및 피드백 표시 */}
        {!isUser && (
          <Box sx={{ mt: 2 }}>
            {/* 신뢰도 점수 */}
            {message.confidenceScore !== undefined && (
              <Chip
                label={`신뢰도: ${(message.confidenceScore * 100).toFixed(0)}%`}
                size="small"
                color={message.confidenceScore > 0.7 ? 'success' : 'warning'}
                sx={{ mr: 1, mb: 1 }}
              />
            )}

            {/* 출처 토글 */}
            {message.sources && message.sources.length > 0 && (
              <>
                <Button
                  size="small"
                  onClick={() => setShowSources(!showSources)}
                  endIcon={showSources ? <ExpandLess /> : <ExpandMore />}
                  sx={{ mr: 1, mb: 1 }}
                >
                  출처 ({message.sources.length})
                </Button>

                <IconButton size="small" onClick={handleDownloadSources} sx={{ mb: 1 }}>
                  <Download fontSize="small" />
                </IconButton>

                <Collapse in={showSources}>
                  <Box sx={{ mt: 1, p: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                    {message.sources.map((source, idx) => (
                      <Typography key={idx} variant="caption" display="block">
                        {idx + 1}. {source.metadata?.file_name || source.metadata?.part_number || 'Unknown'}
                        {source.similarity_score && ` (${(source.similarity_score * 100).toFixed(0)}%)`}
                      </Typography>
                    ))}
                  </Box>
                </Collapse>
              </>
            )}

            {/* 피드백 버튼 */}
            <Box sx={{ mt: 1 }}>
              <IconButton
                size="small"
                onClick={() => handleFeedback('positive')}
                disabled={feedbackSubmitted}
                color={feedbackSubmitted ? 'success' : 'default'}
              >
                <ThumbUp fontSize="small" />
              </IconButton>
              <IconButton
                size="small"
                onClick={() => handleFeedback('negative')}
                disabled={feedbackSubmitted}
                color={feedbackSubmitted ? 'error' : 'default'}
              >
                <ThumbDown fontSize="small" />
              </IconButton>
            </Box>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default MessageBubble;
