package uploadhandler

import (
	"backend/utils"
	"backend/websocket-handler/types"
	"encoding/base64"
	"fmt"
	"os"
	"path/filepath"
)

const SAVE_DIR = "./uploads"

func HandleFileUpload(Data types.FileUploadData) error {
	// Extract the directory from the file name
	dirPath := filepath.Join(SAVE_DIR, filepath.Dir(Data.FileName))

	// Ensure the directory exists
	if err := utils.EnsureDirExists(dirPath); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	// Create the full file path including directories
	filePath := filepath.Join(SAVE_DIR, Data.FileName)

	file, err := os.Create(filePath)
	if err != nil {
		return fmt.Errorf("failed to create file: %w", err)
	}

	defer file.Close()

	// Decode the base64 file data
	data, err := base64.StdEncoding.DecodeString(Data.FileData)
	if err != nil {
		return fmt.Errorf("failed to decode base64: %w", err)
	}

	// Write the data to the file
	if _, err := file.Write(data); err != nil {
		return fmt.Errorf("failed to write to file: %w", err)
	}

	return nil
}
