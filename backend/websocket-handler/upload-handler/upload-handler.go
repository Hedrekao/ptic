package uploadhandler

import (
	"backend/utils"
	inituploadhandler "backend/websocket-handler/init-upload-handler"
	"encoding/base64"
	"fmt"
	"os"
	"path/filepath"
)

type FileUploadData struct {
	FileName string `json:"fileName"`
	FileData string `json:"fileData"`
}

const SAVE_DIR = "./uploads"

func HandleFileUpload(Data FileUploadData) error {
	if err := utils.EnsureDirExists(SAVE_DIR); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	filePath := filepath.Join(SAVE_DIR, Data.FileName)

	file, err := os.Create(filePath)

	if err != nil {
		return fmt.Errorf("failed to create file: %w", err)
	}

	defer file.Close()

	data, err := base64.StdEncoding.DecodeString(Data.FileData)

	if err != nil {
		return fmt.Errorf("failed to decode base64: %w", err)
	}

	if _, err := file.Write(data); err != nil {
		return fmt.Errorf("failed to write to file: %w", err)
	}

	inituploadhandler.FilesUploaded++

	return nil
}
