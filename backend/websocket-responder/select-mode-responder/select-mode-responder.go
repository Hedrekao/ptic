package selectmoderesponder

import (
	selectmodehandler "backend/websocket-handler/select-mode-handler"
	websocketresponder "backend/websocket-responder"
	"fmt"

	"github.com/gorilla/websocket"
)

func SendModeSelected(conn *websocket.Conn) error {
	response := map[string]string{
		"mode": string(selectmodehandler.ModeSelected),
	}

	fmt.Println("Sending mode selected: ", response)
	websocketresponder.SendWebSocketResponse(conn, websocketresponder.WebSocketResponse{Type: "mode_selected", Data: response})

	return nil
}
