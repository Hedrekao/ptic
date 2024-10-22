package websockethandler

import (
	inituploadhandler "backend/websocket-handler/init-upload-handler"
	uploadhandler "backend/websocket-handler/upload-handler"
	uploadprogressresponder "backend/websocket-responder/upload-progress-responder"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

// Define a custom type for the message type
type MessageType string

// Define constants for the allowed values
const (
	TypeUpload     MessageType = "file_upload"
	TypeInitUpload MessageType = "init_upload"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		// Allow all origins (for testing). You can add proper checks later.
		return true
	},
}

type WebSocketMessage struct {
	Type MessageType `json:"type"` // The message type (label)
	Data interface{} `json:"data"` // The actual message data
}

// HandleWebSocketConnection upgrades the connection to WebSocket and handles file uploads
func HandleWebSocketConnection(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("WebSocket upgrade error:", err)
		return
	}
	defer conn.Close()

	fmt.Println("New WebSocket connection established")

	for {
		// Read incoming message
		_, message, err := conn.ReadMessage()
		if err != nil {
			if websocket.IsCloseError(err, websocket.CloseNormalClosure) {
				fmt.Println("WebSocket closed normally.")
				return
			}
			log.Println("Error reading message:", err)
			return
		}

		// Decode JSON message
		var msg WebSocketMessage
		if err := json.Unmarshal(message, &msg); err != nil {
			log.Println("Error unmarshalling JSON:", err)
			continue
		}

		fmt.Println("Received message type:", msg.Type)

		switch {
		case msg.Type == TypeInitUpload:
			// Use a map to unmarshal data first
			dataMap, ok := msg.Data.(map[string]interface{})

			if !ok {
				fmt.Println("Error: expected map for InitUploadData, but got a different type")
				return
			}

			// Extract and convert the necessary fields
			data := inituploadhandler.InitUploadData{
				NumberOfFiles: dataMap["numberOfFiles"].(int),
			}

			inituploadhandler.HandleInitUpload(data)

		case msg.Type == TypeUpload:
			// Use a map to unmarshal data first
			dataMap, ok := msg.Data.(map[string]interface{})
			if !ok {
				fmt.Println("Error: expected map for FileUploadData, but got a different type")
				return
			}

			// Extract and convert the necessary fields
			fileUploadData := uploadhandler.FileUploadData{
				FileName: dataMap["fileName"].(string), // Assuming field is a string
				FileData: dataMap["fileData"].(string), // Assuming field is a string (Base64)
			}

			if err := uploadhandler.HandleFileUpload(fileUploadData); err != nil {
				log.Println("Error handling file upload:", err)
			}

			uploadprogressresponder.SendUploadProgress(conn)

			fmt.Println("Received filename:", fileUploadData.FileName)
		}
	}
}
