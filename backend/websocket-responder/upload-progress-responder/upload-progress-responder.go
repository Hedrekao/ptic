package uploadprogressresponder

import (
	inituploadhandler "backend/websocket-handler/init-upload-handler"
	websocketresponder "backend/websocket-responder"

	"github.com/gorilla/websocket"
)

type UploadProgressData struct {
	Type string
}

func SendUploadProgress(conn *websocket.Conn) error {
	if inituploadhandler.TotalFilesToBeUploaded == 0 {
		return nil
	}

	response := map[string]int{
		"progress": inituploadhandler.FilesUploaded / inituploadhandler.TotalFilesToBeUploaded,
	}

	websocketresponder.SendWebSocketResponse(conn, websocketresponder.WebSocketResponse{Type: "upload_progress", Data: response})

	return nil
}
