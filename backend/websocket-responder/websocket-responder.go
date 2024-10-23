package websocketresponder

import (
	"github.com/gorilla/websocket"
)

type ResponseType string

const (
	TypeUploadProgress ResponseType = "upload_progress"
)

type WebSocketResponse struct {
	Type ResponseType `json:"type"`
	Data interface{}  `json:"data"`
}

func SendWebSocketResponse(conn *websocket.Conn, response WebSocketResponse) error {
	return conn.WriteJSON(response)
}
