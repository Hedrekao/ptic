package websocketresponder

import (
	"backend/utils"
	"backend/websocket-handler/types"
	"fmt"

	"github.com/gorilla/websocket"
)

type WebSocketResponse struct {
	Type string      `json:"type"`
	Data interface{} `json:"data"`
}

func sendWebSocketResponse(conn *websocket.Conn, response WebSocketResponse) error {
	fmt.Println("Sending WebSocket response:", response)
	return conn.WriteJSON(response)
}

func SendModeSelected(ctx *types.ConnectionContext) {
	response := map[string]string{
		"mode": string(ctx.SelectedMode),
	}

	sendWebSocketResponse(ctx.Conn, WebSocketResponse{Type: "mode_selected", Data: response})
}

func SendUploadProgress(ctx *types.ConnectionContext) {
	if ctx.TotalFilesToBeUploaded == 0 {
		return
	}

	response := map[string]float32{
		"progress": float32(ctx.FilesUploaded) / float32(ctx.TotalFilesToBeUploaded) * 100,
	}

	sendWebSocketResponse(ctx.Conn, WebSocketResponse{Type: "upload_progress", Data: response})
}

func SendPredictionProgress(ctx *types.ConnectionContext) {
	if len(ctx.FilesToPredict) == 0 {
		return
	}

	response := map[string]int{
		"filesToPredict": len(ctx.FilesToPredict),
		"approvedFiles":  len(ctx.ApprovedFiles),
	}

	sendWebSocketResponse(ctx.Conn, WebSocketResponse{Type: "prediction_progress", Data: response})

	fmt.Println("Approved files:", len(ctx.ApprovedFiles))
	fmt.Println("Total files to be uploaded:", ctx.TotalFilesToBeUploaded)
	if len(ctx.ApprovedFiles) == ctx.TotalFilesToBeUploaded {
		sendCSVFile(ctx)
	}
}

func SendPredictionApprovalRequest(ctx *types.ConnectionContext) {
	if ctx.IsAwaitingApproval || len(ctx.PredictionFiles) == 0 {
		return
	}

	approval := ctx.PredictionFiles[0]
	ctx.PredictionFiles = ctx.PredictionFiles[1:]

	response := map[string]types.PredictionFile{
		"fileToApprove": approval,
	}

	ctx.IsAwaitingApproval = true
	sendWebSocketResponse(ctx.Conn, WebSocketResponse{Type: "prediction_approval_request", Data: response})
}

func sendCSVFile(ctx *types.ConnectionContext) {
	csv, err := utils.ConvertToCSV(ctx.ApprovedFiles)
	if err != nil {
		fmt.Println("Error converting to CSV:", err)
		return
	}

	response := map[string]string{
		"csvData": csv,
	}

	sendWebSocketResponse(ctx.Conn, WebSocketResponse{Type: "csv_file", Data: response})
}
