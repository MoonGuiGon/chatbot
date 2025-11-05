/**
 * Enhanced Chart Component with Download Support
 */
import { useRef } from 'react'
import PropTypes from 'prop-types'
import {
  Box,
  Paper,
  Typography,
  Button,
  ButtonGroup,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Download,
  ShowChart,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Timeline,
} from '@mui/icons-material'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  AreaChart,
  Area,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { motion } from 'framer-motion'
import { saveAs } from 'file-saver'

// Modern vibrant color palette (inspired by the image)
const COLORS = [
  '#06b6d4', // Cyan
  '#f59e0b', // Amber
  '#eab308', // Yellow
  '#3b82f6', // Blue
  '#8b5cf6', // Purple
  '#ec4899', // Pink
  '#ef4444', // Red
  '#10b981', // Emerald
  '#06b6d4', // Cyan (repeat for more data)
  '#d946ef', // Fuchsia
]

export const EnhancedChart = ({ data, type = 'line', title, xKey, yKey, height = 300 }) => {
  const chartRef = useRef(null)

  const handleDownloadPNG = async () => {
    if (!chartRef.current) return

    try {
      const { default: html2canvas } = await import('html2canvas')
      const canvas = await html2canvas(chartRef.current, {
        backgroundColor: '#ffffff',
        scale: 2,
      })
      canvas.toBlob((blob) => {
        saveAs(blob, `${title || 'chart'}.png`)
      })
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const handleDownloadCSV = () => {
    if (!data || data.length === 0) return

    const headers = Object.keys(data[0]).join(',')
    const rows = data.map((row) => Object.values(row).join(','))
    const csv = [headers, ...rows].join('\n')

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    saveAs(blob, `${title || 'data'}.csv`)
  }

  const renderChart = () => {
    const commonProps = {
      data,
      margin: { top: 10, right: 30, left: 0, bottom: 0 },
    }

    switch (type) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey={xKey} stroke="#666" style={{ fontSize: '12px' }} />
            <YAxis stroke="#666" style={{ fontSize: '12px' }} />
            <RechartsTooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            <Line
              type="monotone"
              dataKey={yKey}
              stroke={COLORS[0]}
              strokeWidth={3}
              dot={{ fill: COLORS[0], r: 5 }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        )

      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey={xKey} stroke="#666" style={{ fontSize: '12px' }} />
            <YAxis stroke="#666" style={{ fontSize: '12px' }} />
            <RechartsTooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            <Bar dataKey={yKey} fill={COLORS[0]} radius={[8, 8, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        )

      case 'pie':
        return (
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey={yKey}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <RechartsTooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
          </PieChart>
        )

      case 'area':
        return (
          <AreaChart {...commonProps}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COLORS[0]} stopOpacity={0.8} />
                <stop offset="95%" stopColor={COLORS[0]} stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey={xKey} stroke="#666" style={{ fontSize: '12px' }} />
            <YAxis stroke="#666" style={{ fontSize: '12px' }} />
            <RechartsTooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            <Area
              type="monotone"
              dataKey={yKey}
              stroke={COLORS[0]}
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorValue)"
            />
          </AreaChart>
        )

      default:
        return null
    }
  }

  return (
    <Box
      component={motion.div}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      sx={{ my: 2 }}
    >
      <Paper
        elevation={2}
        sx={{
          p: 3,
          borderRadius: 4,
          background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
          border: '1px solid rgba(99, 102, 241, 0.1)',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              color: 'text.primary',
              letterSpacing: '-0.02em',
            }}
          >
            {type === 'line' && <ShowChart sx={{ mr: 1.5, fontSize: 24, color: 'primary.main' }} />}
            {type === 'bar' && <BarChartIcon sx={{ mr: 1.5, fontSize: 24, color: 'primary.main' }} />}
            {type === 'pie' && <PieChartIcon sx={{ mr: 1.5, fontSize: 24, color: 'primary.main' }} />}
            {type === 'area' && <Timeline sx={{ mr: 1.5, fontSize: 24, color: 'primary.main' }} />}
            {title || '차트'}
          </Typography>

          <ButtonGroup size="small" variant="outlined" sx={{
            boxShadow: 'none',
            '& .MuiButton-root': {
              borderColor: 'rgba(99, 102, 241, 0.3)',
              color: 'primary.main',
              fontWeight: 600,
              '&:hover': {
                borderColor: 'primary.main',
                backgroundColor: 'primary.light',
              }
            }
          }}>
            <Tooltip title="PNG 다운로드">
              <Button onClick={handleDownloadPNG} startIcon={<Download />}>
                PNG
              </Button>
            </Tooltip>
            <Tooltip title="CSV 다운로드">
              <Button onClick={handleDownloadCSV}>CSV</Button>
            </Tooltip>
          </ButtonGroup>
        </Box>

        <Box ref={chartRef} sx={{ width: '100%', height }}>
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        </Box>

        {/* Data summary */}
        <Box sx={{
          mt: 3,
          pt: 2,
          borderTop: '1px solid rgba(99, 102, 241, 0.1)',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}>
          <Box sx={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: 'success.main',
          }} />
          <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 500 }}>
            데이터 포인트: {data?.length || 0}개
          </Typography>
        </Box>
      </Paper>
    </Box>
  )
}

EnhancedChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.object).isRequired,
  type: PropTypes.oneOf(['line', 'bar', 'pie', 'area']),
  title: PropTypes.string,
  xKey: PropTypes.string,
  yKey: PropTypes.string.isRequired,
  height: PropTypes.number,
}
