package utils

import "os"

// EnsureDirExists creates the directory if it does not exist
func EnsureDirExists(dir string) error {
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		return os.MkdirAll(dir, os.ModePerm)
	}
	return nil
}
