import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  TextField,
  Typography,
  Box,
  Divider,
  Tabs,
  Tab
} from '@mui/material';
import useChatStore from '../../store/chatStore';
import MemoryPanel from './MemoryPanel';

const SettingsDialog = ({ open, onClose, userId = 'user_demo' }) => {
  const { settings, updateSettings } = useChatStore();
  const [localSettings, setLocalSettings] = useState(settings);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    setLocalSettings(settings);
  }, [settings, open]);

  const handleSave = () => {
    updateSettings(localSettings);
    onClose();
  };

  const handleReset = () => {
    const defaultSettings = {
      model: 'gpt-4',
      temperature: 0.1,
      maxTokens: 2000,
      customPrompt: ''
    };
    setLocalSettings(defaultSettings);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>설정</DialogTitle>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
          <Tab label="LLM 설정" />
          <Tab label="메모리 관리" />
        </Tabs>
      </Box>
      <DialogContent>
        {activeTab === 0 ? (
          <Box sx={{ mt: 2 }}>
          {/* Model Selection */}
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>LLM 모델</InputLabel>
            <Select
              value={localSettings.model}
              onChange={(e) => setLocalSettings({ ...localSettings, model: e.target.value })}
              label="LLM 모델"
            >
              <MenuItem value="gpt-4">GPT-4 (추천)</MenuItem>
              <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
              <MenuItem value="custom-model-1">Custom Model 1</MenuItem>
              <MenuItem value="custom-model-2">Custom Model 2</MenuItem>
            </Select>
          </FormControl>

          {/* Temperature */}
          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>
              Temperature: {localSettings.temperature}
            </Typography>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              낮을수록 일관적, 높을수록 창의적 (추천: 0.1)
            </Typography>
            <Slider
              value={localSettings.temperature}
              onChange={(e, v) => setLocalSettings({ ...localSettings, temperature: v })}
              min={0}
              max={1}
              step={0.1}
              marks={[
                { value: 0, label: '0' },
                { value: 0.5, label: '0.5' },
                { value: 1, label: '1' }
              ]}
            />
          </Box>

          {/* Max Tokens */}
          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>
              Max Tokens: {localSettings.maxTokens}
            </Typography>
            <Typography variant="caption" color="text.secondary" gutterBottom display="block">
              응답 최대 길이 (추천: 2000)
            </Typography>
            <Slider
              value={localSettings.maxTokens}
              onChange={(e, v) => setLocalSettings({ ...localSettings, maxTokens: v })}
              min={500}
              max={4000}
              step={100}
              marks={[
                { value: 500, label: '500' },
                { value: 2000, label: '2000' },
                { value: 4000, label: '4000' }
              ]}
            />
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Custom Prompt */}
          <TextField
            fullWidth
            multiline
            rows={6}
            label="Custom System Prompt"
            placeholder="당신은 반도체 부품 전문가입니다..."
            value={localSettings.customPrompt}
            onChange={(e) => setLocalSettings({ ...localSettings, customPrompt: e.target.value })}
            helperText="시스템 프롬프트를 커스터마이징할 수 있습니다. 비워두면 기본 프롬프트를 사용합니다."
          />
          </Box>
        ) : (
          <MemoryPanel userId={userId} />
        )}
      </DialogContent>
      <DialogActions>
        {activeTab === 0 && (
          <>
            <Button onClick={handleReset} color="secondary">
              초기화
            </Button>
            <Button onClick={onClose}>
              취소
            </Button>
            <Button onClick={handleSave} variant="contained">
              저장
            </Button>
          </>
        )}
        {activeTab === 1 && (
          <Button onClick={onClose}>
            닫기
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default SettingsDialog;
