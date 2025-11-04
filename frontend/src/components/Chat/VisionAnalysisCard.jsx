/**
 * Vision Analysis Result Card
 */
import { useState } from 'react'
import PropTypes from 'prop-types'
import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Chip,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogContent,
} from '@mui/material'
import {
  Visibility,
  ExpandMore,
  ExpandLess,
  ZoomIn,
  Image as ImageIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'

export const VisionAnalysisCard = ({ source }) => {
  const [expanded, setExpanded] = useState(false)
  const [imageOpen, setImageOpen] = useState(false)

  const metadata = source.metadata || {}
  const visionData = metadata.vision_analysis || {}

  // Mock screenshot for demo (실제로는 API에서 가져옴)
  const screenshotUrl = metadata.screenshot_path || '/api/screenshots/' + metadata.source

  return (
    <Card
      component={motion.div}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.3 }}
      sx={{
        mt: 2,
        borderLeft: 4,
        borderColor: 'primary.main',
        backgroundColor: 'background.default',
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Visibility sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="subtitle2" fontWeight={600}>
            시각 분석 결과
          </Typography>
          <IconButton
            size="small"
            onClick={() => setExpanded(!expanded)}
            sx={{ ml: 'auto' }}
          >
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>

        {/* Screenshot Preview */}
        {screenshotUrl && (
          <Box
            sx={{
              position: 'relative',
              cursor: 'pointer',
              mb: 2,
              borderRadius: 1,
              overflow: 'hidden',
              '&:hover .zoom-overlay': {
                opacity: 1,
              },
            }}
            onClick={() => setImageOpen(true)}
          >
            <CardMedia
              component="img"
              image={screenshotUrl}
              alt="Document screenshot"
              sx={{
                maxHeight: 200,
                objectFit: 'contain',
                backgroundColor: '#f5f5f5',
              }}
              onError={(e) => {
                e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200"><rect width="400" height="200" fill="%23f0f0f0"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23999">이미지 로드 실패</text></svg>'
              }}
            />
            <Box
              className="zoom-overlay"
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0,0,0,0.5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                opacity: 0,
                transition: 'opacity 0.3s',
              }}
            >
              <ZoomIn sx={{ color: 'white', fontSize: 40 }} />
            </Box>
          </Box>
        )}

        {/* Summary */}
        {visionData.summary && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {visionData.summary}
          </Typography>
        )}

        {/* Expanded Details */}
        <Collapse in={expanded}>
          {/* Key Points */}
          {visionData.key_points && visionData.key_points.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" fontWeight={600} display="block" gutterBottom>
                핵심 포인트:
              </Typography>
              <List dense>
                {visionData.key_points.map((point, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemText
                      primary={point}
                      primaryTypographyProps={{ variant: 'caption' }}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Structured Data */}
          {visionData.structured_data &&
            Object.keys(visionData.structured_data).length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" fontWeight={600} display="block" gutterBottom>
                  구조화 데이터:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {Object.entries(visionData.structured_data).map(([key, value]) => (
                    <Chip
                      key={key}
                      label={`${key}: ${value}`}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            )}

          {/* Visual Elements */}
          {visionData.visual_elements && visionData.visual_elements.length > 0 && (
            <Box>
              <Typography variant="caption" fontWeight={600} display="block" gutterBottom>
                시각 요소:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {visionData.visual_elements.map((element, index) => (
                  <Chip
                    key={index}
                    label={element}
                    size="small"
                    icon={<ImageIcon />}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}
        </Collapse>
      </CardContent>

      {/* Full Image Dialog */}
      <Dialog
        open={imageOpen}
        onClose={() => setImageOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent sx={{ p: 0 }}>
          <img
            src={screenshotUrl}
            alt="Full screenshot"
            style={{ width: '100%', height: 'auto' }}
          />
        </DialogContent>
      </Dialog>
    </Card>
  )
}

VisionAnalysisCard.propTypes = {
  source: PropTypes.shape({
    metadata: PropTypes.object,
    has_visual_analysis: PropTypes.bool,
  }).isRequired,
}
