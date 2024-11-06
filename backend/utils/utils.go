package utils

import (
	"backend/websocket-handler/types"
	"encoding/csv"
	"os"
	"strings"
)

func EnsureDirExists(dir string) error {
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		return os.MkdirAll(dir, os.ModePerm)
	}
	return nil
}

func ConvertToCSV(approvedFiles []types.ApprovedFile) (string, error) {
	var sb strings.Builder
	writer := csv.NewWriter(&sb)

	if err := writer.Write([]string{"FilePath", "Class"}); err != nil {
		return "", err
	}

	for _, file := range approvedFiles {
		if err := writer.Write([]string{file.FilePath, file.Class}); err != nil {
			return "", err
		}
	}

	writer.Flush()
	if err := writer.Error(); err != nil {
		return "", err
	}

	return sb.String(), nil
}
