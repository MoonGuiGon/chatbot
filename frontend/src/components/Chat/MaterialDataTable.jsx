/**
 * Material Data Table Component with Enhanced Visualization
 */
import PropTypes from 'prop-types'
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Button,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
} from '@mui/material'
import {
  Download,
  Storage,
  TrendingUp,
  TrendingDown,
  Remove,
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

export const MaterialDataTable = ({ materials, onExport }) => {
  const getStockStatus = (current, minimum) => {
    const ratio = current / minimum
    if (ratio >= 2) return { label: '충분', color: 'success', icon: <TrendingUp /> }
    if (ratio >= 1) return { label: '적정', color: 'warning', icon: <Remove /> }
    return { label: '부족', color: 'error', icon: <TrendingDown /> }
  }

  const getStockPercentage = (current, minimum) => {
    return Math.min((current / (minimum * 2)) * 100, 100)
  }

  const handleExportExcel = () => {
    // Prepare data for export
    const exportData = materials.map((mat) => ({
      '자재코드': mat.materialId,
      '부품명': mat.name,
      '카테고리': mat.category,
      '현재재고': mat.inventory?.current_stock || 0,
      '최소재고': mat.inventory?.minimum_stock || 0,
      '상태': getStockStatus(
        mat.inventory?.current_stock || 0,
        mat.inventory?.minimum_stock || 0
      ).label,
    }))

    // Create workbook and worksheet
    const ws = XLSX.utils.json_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '부품정보')

    // Generate buffer and save
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    saveAs(blob, `부품정보_${new Date().toISOString().split('T')[0]}.xlsx`)
  }

  return (
    <Box
      component={motion.div}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
        }}
      >
        <Typography
          variant="subtitle2"
          sx={{ display: 'flex', alignItems: 'center', fontWeight: 600 }}
        >
          <Storage sx={{ mr: 1, fontSize: 18 }} />
          부품 정보
        </Typography>
        <Button
          size="small"
          startIcon={<Download />}
          onClick={handleExportExcel}
          variant="outlined"
          sx={{ textTransform: 'none' }}
        >
          Excel 다운로드
        </Button>
      </Box>

      <TableContainer
        component={Paper}
        variant="outlined"
        sx={{ borderRadius: 2, overflow: 'hidden' }}
      >
        <Table size="small">
          <TableHead>
            <TableRow sx={{ backgroundColor: 'primary.main' }}>
              <TableCell sx={{ color: 'white', fontWeight: 600 }}>
                자재코드
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 600 }}>
                부품명
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 600 }}>
                카테고리
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 600 }}>
                재고 현황
              </TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 600 }}>
                상태
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {materials.map((mat, index) => {
              const current = mat.inventory?.current_stock || 0
              const minimum = mat.inventory?.minimum_stock || 0
              const status = getStockStatus(current, minimum)
              const percentage = getStockPercentage(current, minimum)

              return (
                <TableRow
                  key={mat.materialId || index}
                  component={motion.tr}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  sx={{
                    '&:hover': { backgroundColor: 'action.hover' },
                  }}
                >
                  <TableCell>
                    <Chip
                      label={mat.materialId}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell sx={{ fontWeight: 500 }}>{mat.name}</TableCell>
                  <TableCell>{mat.category}</TableCell>
                  <TableCell>
                    <Box sx={{ minWidth: 120 }}>
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          mb: 0.5,
                        }}
                      >
                        <Typography variant="caption">
                          {current} / {minimum}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {percentage.toFixed(0)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={percentage}
                        color={status.color}
                        sx={{ height: 6, borderRadius: 1 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={status.label}
                      color={status.color}
                      size="small"
                      icon={status.icon}
                    />
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Knowledge Graph Context */}
      {materials.some((m) => m.kg_context) && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
            연관 정보 (Knowledge Graph)
          </Typography>
          {materials
            .filter((m) => m.kg_context)
            .map((mat, index) => (
              <Box key={index} sx={{ ml: 2, mb: 1 }}>
                {mat.kg_context.suppliers?.length > 0 && (
                  <Typography variant="caption">
                    🏢 공급업체: {mat.kg_context.suppliers.map(s => s.name).join(', ')}
                  </Typography>
                )}
                {mat.kg_context.similar_materials?.length > 0 && (
                  <Typography variant="caption" display="block">
                    🔄 유사 부품: {mat.kg_context.similar_materials.map(m => m.materialId).join(', ')}
                  </Typography>
                )}
              </Box>
            ))}
        </Box>
      )}
    </Box>
  )
}

MaterialDataTable.propTypes = {
  materials: PropTypes.arrayOf(
    PropTypes.shape({
      materialId: PropTypes.string,
      name: PropTypes.string,
      category: PropTypes.string,
      inventory: PropTypes.object,
      kg_context: PropTypes.object,
    })
  ).isRequired,
  onExport: PropTypes.func.isRequired,
}
