package uploadprogressresponder

import (
	types "backend/websocket-handler/types"
	websocketresponder "backend/websocket-responder"
	"fmt"
)

func SendUploadProgress(ctx *types.ConnectionContext) error {
	if ctx.TotalFilesToBeUploaded == 0 {
		return nil
	}

	response := map[string]float32{
		"progress": float32(ctx.FilesUploaded) / float32(ctx.TotalFilesToBeUploaded) * 100,
	}

	fmt.Println("Sending upload progress: ", response)
	websocketresponder.SendWebSocketResponse(ctx.Conn, websocketresponder.WebSocketResponse{Type: "upload_progress", Data: response})

	if ctx.FilesUploaded == ctx.TotalFilesToBeUploaded {
		ctx.FilesUploaded = 0
		ctx.TotalFilesToBeUploaded = 0
	}

	return nil
}
