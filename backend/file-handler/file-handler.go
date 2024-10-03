package filehandler

import (
	"backend/utils"
	"fmt"
	"os"
	"path/filepath"

	"github.com/gorilla/websocket"
)

const SAVE_DIR = "./uploads"

// SaveFileFromWebSocket reads file data from the WebSocket connection and saves it
func SaveFileFromWebSocket(conn *websocket.Conn) error {
	// Ensure the directory exists
	if err := utils.EnsureDirExists(SAVE_DIR); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	for {
		// Read filename (text message)
		messageType, fileNameBytes, err := conn.ReadMessage()
	
		if err != nil {
			if websocket.IsCloseError(err, websocket.CloseNormalClosure) {
				fmt.Println("WebSocket closed normally.")
				break
			}
			return fmt.Errorf("failed to read filename: %w", err)
		}

		// Check if the message is a text message (filename)
		if messageType != websocket.TextMessage {
			return fmt.Errorf("expected text message for filename, got %v", messageType)
		}
		fileName := string(fileNameBytes)

		// Send acknowledgment back to the client
		conn.WriteMessage(websocket.TextMessage, []byte("filename received"))

		// Create the file on the server
		filePath := filepath.Join(SAVE_DIR, fileName)
		file, err := os.Create(filePath)
		if err != nil {
			return fmt.Errorf("failed to create file: %w", err)
		}
		defer file.Close()

		fmt.Println("Receiving file:", fileName)

		// Now expect binary file data
		for {
			// Read binary message (file data)
			messageType, fileData, err := conn.ReadMessage()
			if err != nil {
				if websocket.IsCloseError(err, websocket.CloseNormalClosure) {
					fmt.Println("File transfer completed")
					break
				}
				return fmt.Errorf("error reading file data: %w", err)
			}

			if messageType == websocket.BinaryMessage {
				// Write binary data to file
				if _, err := file.Write(fileData); err != nil {
					return fmt.Errorf("failed to write to file: %w", err)
				}
				fmt.Println("File data written for:", fileName)
				break // Move to the next file
			}
		}
	}

	return nil
}
