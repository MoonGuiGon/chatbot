/**
 * Analytics Dashboard Component
 */
import { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Tabs,
  Tab,
  Avatar,
  List,
  ListItem,
  ListItemText,
  Chip,
} from '@mui/material'
import {
  TrendingUp,
  QuestionAnswer,
  ThumbUp,
  Speed,
  Storage,
  Description,
} from '@mui/icons-material'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { motion } from 'framer-motion'
import { feedbackApi, conversationApi } from '../../services/api'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

export const AnalyticsDashboard = () => {
  const [tabValue, setTabValue] = useState(0)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const feedbackStats = await feedbackApi.getFeedbackStats()
      const knowledge = await feedbackApi.getKnowledgeEntries(10)

      // Mock data for demo
      setStats({
        feedback: feedbackStats,
        knowledge: knowledge.entries || [],
        usage: generateMockUsageData(),
        responseTime: generateMockResponseTime(),
        topQueries: generateMockTopQueries(),
        dataSourceUsage: generateMockDataSourceUsage(),
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateMockUsageData = () => {
    return Array.from({ length: 7 }, (_, i) => ({
      day: ['월', '화', '수', '목', '금', '토', '일'][i],
      queries: Math.floor(Math.random() * 50) + 20,
      responses: Math.floor(Math.random() * 50) + 20,
    }))
  }

  const generateMockResponseTime = () => {
    return Array.from({ length: 10 }, (_, i) => ({
      time: `${i + 1}:00`,
      avgTime: Math.random() * 2 + 0.5,
      cacheHitRate: Math.random() * 40 + 60,
    }))
  }

  const generateMockTopQueries = () => {
    return [
      { query: 'MAT-001 재고 조회', count: 45 },
      { query: '부품 사양서 검색', count: 38 },
      { query: '공급업체 정보', count: 32 },
      { query: '장착 이력 조회', count: 28 },
      { query: '구매 현황 분석', count: 25 },
    ]
  }

  const generateMockDataSourceUsage = () => {
    return [
      { name: 'MongoDB', value: 35 },
      { name: 'VectorDB', value: 40 },
      { name: 'Knowledge Graph', value: 15 },
      { name: 'Cache', value: 10 },
    ]
  }

  const StatCard = ({ title, value, icon, color, subtitle }) => (
    <Card
      component={motion.div}
      whileHover={{ scale: 1.02 }}
      sx={{ height: '100%' }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ bgcolor: color, mr: 2 }}>
            {icon}
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h4" fontWeight={600}>
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
          </Box>
        </Box>
        {subtitle && (
          <Typography variant="caption" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  )

  if (loading || !stats) {
    return <Box>Loading...</Box>
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        분석 대시보드
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="총 질문 수"
            value="1,234"
            icon={<QuestionAnswer />}
            color="primary.main"
            subtitle="지난 30일"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="평균 응답 시간"
            value="0.8초"
            icon={<Speed />}
            color="success.main"
            subtitle="캐시 hit: 85%"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="긍정 피드백"
            value={stats.feedback.positive || 0}
            icon={<ThumbUp />}
            color="info.main"
            subtitle={`평균 평점: ${stats.feedback.average_rating || 0}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="학습된 지식"
            value={stats.knowledge.length}
            icon={<Storage />}
            color="warning.main"
            subtitle="Knowledge Base"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ mb: 2 }}>
        <Tab label="사용 현황" />
        <Tab label="성능 분석" />
        <Tab label="인기 질문" />
        <Tab label="데이터 소스" />
      </Tabs>

      {/* Tab 0: Usage */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                일별 사용 추이
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats.usage}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="queries" stroke="#8884d8" name="질문" />
                  <Line type="monotone" dataKey="responses" stroke="#82ca9d" name="답변" />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                학습된 지식
              </Typography>
              <List>
                {stats.knowledge.slice(0, 5).map((entry, index) => (
                  <ListItem key={index} dense>
                    <ListItemText
                      primary={entry.query_pattern}
                      secondary={`신뢰도: ${entry.confidence_score}`}
                      primaryTypographyProps={{ variant: 'body2' }}
                      secondaryTypographyProps={{ variant: 'caption' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Tab 1: Performance */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                응답 시간 및 캐시 히트율
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats.responseTime}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="avgTime"
                    stroke="#8884d8"
                    name="평균 응답시간 (초)"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="cacheHitRate"
                    stroke="#82ca9d"
                    name="캐시 히트율 (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Tab 2: Top Queries */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                인기 질문 Top 5
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.topQueries} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="query" type="category" width={150} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                질문 분석
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Chip label="부품 관련: 45%" sx={{ mb: 1, width: '100%' }} />
                <Chip label="문서 검색: 30%" sx={{ mb: 1, width: '100%' }} />
                <Chip label="이력 조회: 25%" sx={{ width: '100%' }} />
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Tab 3: Data Sources */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                데이터 소스 사용 비율
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={stats.dataSourceUsage}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) =>
                      `${name}: ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {stats.dataSourceUsage.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                데이터 소스 상태
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="MongoDB"
                    secondary="부품 정보 1,234개"
                  />
                  <Chip label="정상" color="success" size="small" />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="pgvector"
                    secondary="문서 5,678개"
                  />
                  <Chip label="정상" color="success" size="small" />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Neo4j"
                    secondary="관계 2,345개"
                  />
                  <Chip label="정상" color="success" size="small" />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Redis Cache"
                    secondary="히트율 85%"
                  />
                  <Chip label="최적" color="success" size="small" />
                </ListItem>
              </List>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  )
}
