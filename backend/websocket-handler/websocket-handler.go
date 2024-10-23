package websockethandler

import (
	inituploadhandler "backend/websocket-handler/init-upload-handler"
	selectmodehandler "backend/websocket-handler/select-mode-handler"
	uploadhandler "backend/websocket-handler/upload-handler"
	selectmoderesponder "backend/websocket-responder/select-mode-responder"
	uploadprogressresponder "backend/websocket-responder/upload-progress-responder"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

type MessageType string

const (
	TypeUpload     MessageType = "file_upload"
	TypeInitUpload MessageType = "init_upload"
	TypeSelectMode MessageType = "select_mode"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

type WebSocketMessage struct {
	Type MessageType `json:"type"`
	Data interface{} `json:"data"`
}

func HandleWebSocketConnection(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("WebSocket upgrade error:", err)
		return
	}
	defer conn.Close()

	fmt.Println("New WebSocket connection established")

	for {
		_, message, err := conn.ReadMessage()
		if err != nil {
			if websocket.IsCloseError(err, websocket.CloseNormalClosure) {
				fmt.Println("WebSocket closed normally.")
				return
			}
			log.Println("Error reading message:", err)
			return
		}

		var msg WebSocketMessage
		if err := json.Unmarshal(message, &msg); err != nil {
			log.Println("Error unmarshalling JSON:", err)
			continue
		}

		fmt.Println("Received message type:", msg.Type)

		switch {
		case msg.Type == TypeInitUpload:
			dataMap, ok := msg.Data.(map[string]interface{})

			if !ok {
				fmt.Println("Error: expected map for InitUploadData, but got a different type")
				return
			}

			numberOfFiles, ok := dataMap["numberOfFiles"].(float64)

			if !ok {
				fmt.Println("Error: numberOfFiles is not a float64")
				return
			}

			data := inituploadhandler.InitUploadData{
				NumberOfFiles: int(numberOfFiles), // Cast float64 to int
			}

			inituploadhandler.HandleInitUpload(data)

		case msg.Type == TypeUpload:
			dataMap, ok := msg.Data.(map[string]interface{})
			if !ok {
				fmt.Println("Error: expected map for FileUploadData, but got a different type")
				return
			}

			fileUploadData := uploadhandler.FileUploadData{
				FileName: dataMap["fileName"].(string),
				FileData: dataMap["fileData"].(string), // Assuming field is a string (Base64)
			}

			if err := uploadhandler.HandleFileUpload(fileUploadData); err != nil {
				log.Println("Error handling file upload:", err)
			}

			log.Println("File uploaded:", fileUploadData.FileName)

			uploadprogressresponder.SendUploadProgress(conn)

			fmt.Println("Received filename:", fileUploadData.FileName)

		case msg.Type == TypeSelectMode:
			dataMap, ok := msg.Data.(map[string]interface{})
			if !ok {
				fmt.Println("Error: expected map for SelectMode, but got a different type")
				return
			}

			modeSelectData := selectmodehandler.SelectModeData{
				Mode: dataMap["mode"].(selectmodehandler.EMode),
			}

			selectmodehandler.HandleSelectMode(modeSelectData)

			selectmoderesponder.SendModeSelected(conn)
		}
	}
}
