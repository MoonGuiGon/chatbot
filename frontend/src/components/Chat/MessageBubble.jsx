import React, { useState, useMemo } from 'react';
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
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { feedbackAPI } from '../../services/api';

const MessageBubble = ({ message, isUser, onFeedback }) => {
  const [showSources, setShowSources] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  // Content에서 JSON 코드 블록 추출 및 파싱
  const parsedCharts = useMemo(() => {
    if (!message.content || isUser) return [];

    const charts = [];
    // ```json ... ``` 패턴 찾기
    const jsonBlockRegex = /```json\s*\n([\s\S]*?)\n```/g;
    let match;

    while ((match = jsonBlockRegex.exec(message.content)) !== null) {
      try {
        const jsonData = JSON.parse(match[1]);
        if (jsonData.type && jsonData.data) {
          charts.push(jsonData);
        }
      } catch (e) {
        console.warn('Failed to parse JSON block:', e);
      }
    }

    return charts;
  }, [message.content, isUser]);

  // Content에서 Markdown 표 제외하고 렌더링할 내용
  const contentWithoutJsonBlocks = useMemo(() => {
    if (!message.content) return '';
    // JSON 블록 제거
    return message.content.replace(/```json\s*\n[\s\S]*?\n```/g, '');
  }, [message.content]);

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

  const renderChart = (chartData, idx) => {
    if (!chartData) return null;

    const { type, title, data } = chartData;

    // 차트 데이터 변환
    const chartDataFormatted = data.labels ? data.labels.map((label, labelIdx) => ({
      name: label,
      ...data.datasets.reduce((acc, dataset) => ({
        ...acc,
        [dataset.label]: dataset.data[labelIdx]
      }), {})
    })) : data.datasets[0].data.map((value, i) => ({
      name: data.labels ? data.labels[i] : `Item ${i + 1}`,
      value
    }));

    if (type === 'bar') {
      return (
        <Box key={idx} sx={{ my: 3, p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            {title}
          </Typography>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={chartDataFormatted}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                labelStyle={{ fontWeight: 'bold' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              {data.datasets.map((dataset, datasetIdx) => (
                <Bar
                  key={datasetIdx}
                  dataKey={dataset.label}
                  fill={dataset.backgroundColor ? dataset.backgroundColor[0] || dataset.backgroundColor : `hsl(${datasetIdx * 120}, 70%, 50%)`}
                  stroke={dataset.borderColor ? dataset.borderColor[0] || dataset.borderColor : undefined}
                  strokeWidth={dataset.borderWidth || 0}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </Box>
      );
    }

    if (type === 'line') {
      return (
        <Box key={idx} sx={{ my: 3, p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            {title}
          </Typography>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={chartDataFormatted}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                labelStyle={{ fontWeight: 'bold' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              {data.datasets.map((dataset, datasetIdx) => (
                <Line
                  key={datasetIdx}
                  type="monotone"
                  dataKey={dataset.label}
                  stroke={dataset.borderColor || `hsl(${datasetIdx * 120}, 70%, 50%)`}
                  fill={dataset.backgroundColor}
                  strokeWidth={3}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </Box>
      );
    }

    if (type === 'pie') {
      const COLORS = data.datasets[0].backgroundColor || [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
      ];

      const pieData = data.labels.map((label, i) => ({
        name: label,
        value: data.datasets[0].data[i]
      }));

      return (
        <Box key={idx} sx={{ my: 3, p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            {title}
          </Typography>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
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
        {/* 메시지 내용 (JSON 블록 제외) */}
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeRaw]}
          components={{
            table: ({ node, ...props }) => (
              <TableContainer component={Paper} sx={{ my: 2, maxWidth: '100%', overflowX: 'auto' }}>
                <Table size="small" {...props} />
              </TableContainer>
            ),
            thead: ({ node, ...props }) => <TableHead {...props} />,
            tbody: ({ node, ...props }) => <TableBody {...props} />,
            tr: ({ node, ...props }) => <TableRow {...props} />,
            th: ({ node, ...props }) => (
              <TableCell
                sx={{
                  fontWeight: 'bold',
                  bgcolor: 'action.hover',
                  borderBottom: '2px solid',
                  borderColor: 'divider'
                }}
                {...props}
              />
            ),
            td: ({ node, ...props }) => (
              <TableCell
                sx={{
                  borderBottom: '1px solid',
                  borderColor: 'divider'
                }}
                {...props}
              />
            ),
          }}
        >
          {contentWithoutJsonBlocks}
        </ReactMarkdown>

        {/* 표 렌더링 (legacy support) */}
        {message.tableData && renderTable(message.tableData)}

        {/* 그래프 렌더링 (legacy support) */}
        {message.chartData && renderChart(message.chartData, 0)}

        {/* Content에서 추출한 차트들 렌더링 */}
        {parsedCharts.length > 0 && (
          <Box sx={{ mt: 2 }}>
            {parsedCharts.map((chart, idx) => renderChart(chart, idx))}
          </Box>
        )}

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
