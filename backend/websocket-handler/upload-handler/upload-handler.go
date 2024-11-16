package uploadhandler

import (
	"backend/utils"
	"backend/websocket-handler/types"
	"encoding/base64"
	"fmt"
	"os"
	"path/filepath"
)

// TODO: clean this constant (maybe as env)
const SAVE_DIR = "./uploads"

func HandleFileUpload(ctx *types.ConnectionContext, data types.FileUploadData) error {

	// Decode the base64 file imageData
	imageData, err := base64.StdEncoding.DecodeString(data.FileData)
	if err != nil {
		return fmt.Errorf("failed to decode base64: %w", err)
	}

	if os.Getenv("ENV") == "AZURE" {
		blobClient := ctx.BlobClient
		containerName := "images"

		blobClient.UploadBuffer(ctx.Ctx, containerName, data.FileName, imageData, nil)

	} else {
		// Extract the directory from the file name
		dirPath := filepath.Join(SAVE_DIR, filepath.Dir(data.FileName))

		// Ensure the directory exists
		if err := utils.EnsureDirExists(dirPath); err != nil {
			return fmt.Errorf("failed to create directory: %w", err)
		}

		// Create the full file path including directories
		filePath := filepath.Join(SAVE_DIR, data.FileName)

		file, err := os.Create(filePath)
		if err != nil {
			return fmt.Errorf("failed to create file: %w", err)
		}

		defer file.Close()

		// Write the data to the file
		if _, err := file.Write(imageData); err != nil {
			return fmt.Errorf("failed to write to file: %w", err)
		}

	}
	return nil
}
