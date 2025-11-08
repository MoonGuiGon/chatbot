import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Divider
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Add as AddIcon,
  Memory as MemoryIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import axios from 'axios';

const MemoryPanel = ({ userId }) => {
  const [memories, setMemories] = useState([]);
  const [stats, setStats] = useState({});
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newMemory, setNewMemory] = useState({
    category: '선호도',
    key: '',
    value: '',
    importance: 'medium'
  });

  useEffect(() => {
    if (userId) {
      loadMemories();
      loadStats();
    }
  }, [userId]);

  const loadMemories = async () => {
    try {
      const response = await axios.get(`/api/memory/${userId}`);
      if (response.data.success) {
        setMemories(response.data.memories);
      }
    } catch (error) {
      console.error('메모리 로드 오류:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`/api/memory/stats/${userId}`);
      if (response.data.success) {
        setStats(response.data);
      }
    } catch (error) {
      console.error('통계 로드 오류:', error);
    }
  };

  const handleDeleteMemory = async (memoryId) => {
    try {
      const response = await axios.delete(`/api/memory/${userId}/${memoryId}`);
      if (response.data.success) {
        loadMemories();
        loadStats();
      }
    } catch (error) {
      console.error('메모리 삭제 오류:', error);
    }
  };

  const handleClearAll = async () => {
    if (window.confirm('모든 메모리를 초기화하시겠습니까?')) {
      try {
        const response = await axios.post(`/api/memory/${userId}/clear`);
        if (response.data.success) {
          loadMemories();
          loadStats();
        }
      } catch (error) {
        console.error('메모리 초기화 오류:', error);
      }
    }
  };

  const handleAddMemory = async () => {
    try {
      const response = await axios.post(`/api/memory/${userId}/manual`, newMemory);
      if (response.data.success) {
        setAddDialogOpen(false);
        setNewMemory({
          category: '선호도',
          key: '',
          value: '',
          importance: 'medium'
        });
        loadMemories();
        loadStats();
      }
    } catch (error) {
      console.error('메모리 추가 오류:', error);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      '선호도': 'primary',
      '역할': 'secondary',
      '자주조회': 'info',
      '명시적요청': 'warning',
      '업무컨텍스트': 'success'
    };
    return colors[category] || 'default';
  };

  const getImportanceColor = (importance) => {
    const colors = {
      'high': 'error',
      'medium': 'warning',
      'low': 'default'
    };
    return colors[importance] || 'default';
  };

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <MemoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          사용자 메모리
        </Typography>
        <Box>
          <Button
            startIcon={<AddIcon />}
            onClick={() => setAddDialogOpen(true)}
            variant="outlined"
            size="small"
            sx={{ mr: 1 }}
          >
            추가
          </Button>
          <Button
            startIcon={<ClearIcon />}
            onClick={handleClearAll}
            variant="outlined"
            color="error"
            size="small"
          >
            초기화
          </Button>
        </Box>
      </Box>

      {/* 통계 */}
      {stats.total_memories > 0 && (
        <Box sx={{ mb: 2 }}>
          <Alert severity="info">
            총 {stats.total_memories}개의 정보가 저장되어 있습니다.
          </Alert>
        </Box>
      )}

      {/* 메모리 목록 */}
      {memories.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            아직 저장된 메모리가 없습니다.
          </Typography>
          <Typography variant="caption" color="text.secondary">
            대화를 나누면 자동으로 중요한 정보가 저장됩니다.
          </Typography>
        </Box>
      ) : (
        <List>
          {memories.map((memory, index) => (
            <React.Fragment key={memory._id || index}>
              <ListItem>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 0.5 }}>
                      <Typography variant="subtitle2">{memory.key}</Typography>
                      <Chip
                        label={memory.category}
                        size="small"
                        color={getCategoryColor(memory.category)}
                      />
                      <Chip
                        label={memory.importance}
                        size="small"
                        color={getImportanceColor(memory.importance)}
                      />
                    </Box>
                  }
                  secondary={memory.value}
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={() => handleDeleteMemory(memory._id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
              {index < memories.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      )}

      {/* 메모리 추가 Dialog */}
      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>메모리 추가</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>카테고리</InputLabel>
              <Select
                value={newMemory.category}
                onChange={(e) => setNewMemory({ ...newMemory, category: e.target.value })}
                label="카테고리"
              >
                <MenuItem value="선호도">선호도</MenuItem>
                <MenuItem value="역할">역할</MenuItem>
                <MenuItem value="자주조회">자주 조회</MenuItem>
                <MenuItem value="명시적요청">명시적 요청</MenuItem>
                <MenuItem value="업무컨텍스트">업무 컨텍스트</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="키워드"
              value={newMemory.key}
              onChange={(e) => setNewMemory({ ...newMemory, key: e.target.value })}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              multiline
              rows={3}
              label="내용"
              value={newMemory.value}
              onChange={(e) => setNewMemory({ ...newMemory, value: e.target.value })}
              sx={{ mb: 2 }}
            />

            <FormControl fullWidth>
              <InputLabel>중요도</InputLabel>
              <Select
                value={newMemory.importance}
                onChange={(e) => setNewMemory({ ...newMemory, importance: e.target.value })}
                label="중요도"
              >
                <MenuItem value="high">높음</MenuItem>
                <MenuItem value="medium">보통</MenuItem>
                <MenuItem value="low">낮음</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>취소</Button>
          <Button
            onClick={handleAddMemory}
            variant="contained"
            disabled={!newMemory.key || !newMemory.value}
          >
            추가
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MemoryPanel;
