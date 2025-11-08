import React from 'react';
import {
  Box,
  Paper,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Typography
} from '@mui/material';
import {
  Psychology,
  Storage,
  Description,
  Create,
  FactCheck
} from '@mui/icons-material';

const ProgressIndicator = ({ progress }) => {
  if (!progress || progress.length === 0) return null;

  const steps = [
    { stage: 'query_analysis', label: '질문 분석', icon: <Psychology /> },
    { stage: 'mongodb_search', label: '부품 정보 검색', icon: <Storage /> },
    { stage: 'vectordb_search', label: '문서 검색', icon: <Description /> },
    { stage: 'response_generation', label: '답변 생성', icon: <Create /> },
    { stage: 'quality_check', label: '품질 검증', icon: <FactCheck /> }
  ];

  const getActiveStep = () => {
    const lastProgress = progress[progress.length - 1];
    return steps.findIndex(step => step.stage === lastProgress.stage);
  };

  const activeStep = getActiveStep();

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <CircularProgress size={20} sx={{ mr: 1 }} />
        <Typography variant="body2">
          {progress[progress.length - 1]?.message || '처리 중...'}
        </Typography>
      </Box>

      <Stepper activeStep={activeStep} alternativeLabel>
        {steps.map((step, index) => (
          <Step key={step.stage} completed={index <= activeStep}>
            <StepLabel icon={step.icon}>
              {step.label}
            </StepLabel>
          </Step>
        ))}
      </Stepper>
    </Paper>
  );
};

export default ProgressIndicator;
