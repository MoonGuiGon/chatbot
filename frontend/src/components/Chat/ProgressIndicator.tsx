/**
 * Progress Indicator Component
 * Shows the current processing status
 */
import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  CircularProgress,
  Fade,
} from '@mui/material'
import {
  CheckCircle,
  Error as ErrorIcon,
  Search,
  Storage,
  Description,
  SmartToy,
} from '@mui/icons-material'
import type { ProgressStep } from '../../types'

interface ProgressIndicatorProps {
  steps: ProgressStep[]
  show: boolean
}

const stepIcons: Record<string, React.ReactElement> = {
  analyzing: <Search />,
  retrieving_materials: <Storage />,
  searching_documents: <Description />,
  generating_response: <SmartToy />,
  completed: <CheckCircle />,
  error: <ErrorIcon />,
}

const stepLabels: Record<string, string> = {
  analyzing: '질문 분석',
  retrieving_materials: 'MongoDB 조회',
  searching_documents: 'VectorDB 검색',
  generating_response: '답변 생성',
  completed: '완료',
  error: '오류',
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ steps, show }) => {
  if (!show || steps.length === 0) return null

  const activeStep = steps.findIndex((s) => s.status === 'in_progress')

  return (
    <Fade in={show}>
      <Paper
        elevation={2}
        sx={{
          p: 2,
          mb: 2,
          borderLeft: 4,
          borderColor: 'primary.main',
          backgroundColor: 'background.default',
        }}
      >
        <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
          진행 상황
        </Typography>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={index} completed={step.status === 'completed'}>
              <StepLabel
                error={step.status === 'error'}
                StepIconComponent={() => (
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {step.status === 'in_progress' ? (
                      <CircularProgress size={24} />
                    ) : step.status === 'completed' ? (
                      <CheckCircle color="success" />
                    ) : step.status === 'error' ? (
                      <ErrorIcon color="error" />
                    ) : (
                      stepIcons[step.step] || <Search />
                    )}
                  </Box>
                )}
              >
                {stepLabels[step.step] || step.step}
              </StepLabel>
              <StepContent>
                <Typography variant="body2" color="text.secondary">
                  {step.message}
                </Typography>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>
    </Fade>
  )
}
