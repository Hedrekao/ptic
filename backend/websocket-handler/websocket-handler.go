package websockethandler

import (
	types "backend/websocket-handler/types"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
	"github.com/gorilla/websocket"
)

type MessageType string

const (
	TypeUpload             MessageType = "file_upload"
	TypeInitUpload         MessageType = "init_upload"
	TypeCancelUpload       MessageType = "cancel_upload"
	TypeSelectMode         MessageType = "select_mode"
	TypeInitPredictions    MessageType = "init_predictions"
	TypePredictionApproval MessageType = "prediction_approval"
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

func HandleWebSocketConnection(blobClient *azblob.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		conn, err := upgrader.Upgrade(w, r, nil)
		if err != nil {
			log.Println("WebSocket upgrade error:", err)
			return
		}

		ctx := &types.ConnectionContext{
			Ctx:               context.Background(),
			Conn:              conn,
			BlobClient:        blobClient,
			Id:                r.RemoteAddr, // Use RemoteAddr for ID, or generate a unique one
			FilesToPredict:    make(map[string][]string),
			IsUploadCancelled: false,
		}

		fmt.Println("New WebSocket connection established:", ctx.Id)
		go handleConnection(ctx)
	}
}

func handleConnection(ctx *types.ConnectionContext) {
	defer ctx.Conn.Close()

	for {
		_, message, err := ctx.Conn.ReadMessage()
		if err != nil {
			if websocket.IsCloseError(err, websocket.CloseNormalClosure) {
				fmt.Println("WebSocket closed normally:", ctx.Id)
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
			handleInitUpload(ctx, msg.Data)
		case msg.Type == TypeCancelUpload:
			handleCancelUpload(ctx)
		case msg.Type == TypeUpload:
			handleFileUpload(ctx, msg.Data)
		case msg.Type == TypeSelectMode:
			handleSelectMode(ctx, msg.Data)
		case msg.Type == TypeInitPredictions:
			handleInitPredictions(ctx)
		case msg.Type == TypePredictionApproval:
			handlePredictionApproval(ctx, msg.Data)
		}
	}
}
