package uploadprogressresponder

import (
	inituploadhandler "backend/websocket-handler/init-upload-handler"
	websocketresponder "backend/websocket-responder"
	"fmt"

	"github.com/gorilla/websocket"
)

func SendUploadProgress(conn *websocket.Conn) error {
	if inituploadhandler.TotalFilesToBeUploaded == 0 {
		return nil
	}

	response := map[string]float32{
		"progress": float32(inituploadhandler.FilesUploaded) / float32(inituploadhandler.TotalFilesToBeUploaded) * 100,
	}

	fmt.Println("Sending upload progress: ", response)
	websocketresponder.SendWebSocketResponse(conn, websocketresponder.WebSocketResponse{Type: "upload_progress", Data: response})

	if inituploadhandler.FilesUploaded == inituploadhandler.TotalFilesToBeUploaded {
		inituploadhandler.FilesUploaded = 0
		inituploadhandler.TotalFilesToBeUploaded = 0
	}

	return nil
}
