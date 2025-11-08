import React, { useState, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  LinearProgress,
  Alert,
  Chip
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  Delete,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material';
import { documentAPI } from '../../services/api';

const DocumentUploadDialog = ({ open, onClose }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState([]);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const handleRemoveFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    setUploading(true);
    setUploadResults([]);

    const results = [];

    for (const file of files) {
      try {
        const result = await documentAPI.uploadDocument(file, (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          console.log(`${file.name}: ${percentCompleted}%`);
        });

        results.push({
          fileName: file.name,
          success: result.success,
          documentId: result.document_id,
          message: '업로드 성공'
        });
      } catch (error) {
        results.push({
          fileName: file.name,
          success: false,
          message: error.message || '업로드 실패'
        });
      }
    }

    setUploadResults(results);
    setUploading(false);
    setFiles([]);
  };

  const handleClose = () => {
    setFiles([]);
    setUploadResults([]);
    onClose();
  };

  const getFileIcon = (fileName) => {
    const ext = fileName.split('.').pop().toLowerCase();
    return <InsertDriveFile />;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>문서 업로드</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            PDF, PPT, Excel, Word 파일을 업로드할 수 있습니다. 업로드된 문서는 검수 후 VectorDB에 저장됩니다.
          </Alert>

          {/* File Selection */}
          <Button
            component="label"
            variant="outlined"
            startIcon={<CloudUpload />}
            fullWidth
            sx={{ mb: 2 }}
            disabled={uploading}
          >
            파일 선택
            <input
              type="file"
              hidden
              multiple
              accept=".pdf,.ppt,.pptx,.doc,.docx,.xls,.xlsx"
              onChange={handleFileSelect}
            />
          </Button>

          {/* File List */}
          {files.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                선택된 파일 ({files.length})
              </Typography>
              <List dense>
                {files.map((file, index) => (
                  <ListItem
                    key={index}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        onClick={() => handleRemoveFile(index)}
                        disabled={uploading}
                      >
                        <Delete />
                      </IconButton>
                    }
                  >
                    <ListItemIcon>
                      {getFileIcon(file.name)}
                    </ListItemIcon>
                    <ListItemText
                      primary={file.name}
                      secondary={formatFileSize(file.size)}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Progress */}
          {uploading && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                업로드 중...
              </Typography>
              <LinearProgress />
            </Box>
          )}

          {/* Upload Results */}
          {uploadResults.length > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                업로드 결과
              </Typography>
              <List dense>
                {uploadResults.map((result, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {result.success ? (
                        <CheckCircle color="success" />
                      ) : (
                        <ErrorIcon color="error" />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={result.fileName}
                      secondary={result.message}
                    />
                    {result.success && (
                      <Chip
                        label="검수 대기"
                        size="small"
                        color="warning"
                      />
                    )}
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>
          닫기
        </Button>
        <Button
          onClick={handleUpload}
          variant="contained"
          disabled={files.length === 0 || uploading}
        >
          업로드
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentUploadDialog;
