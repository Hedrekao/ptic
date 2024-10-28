package selectmoderesponder

import (
	"backend/websocket-handler/types"
	websocketresponder "backend/websocket-responder"
	"fmt"
)

func SendModeSelected(ctx *types.ConnectionContext) error {
	response := map[string]string{
		"mode": string(ctx.SelectedMode),
	}

	fmt.Println("Sending mode selected: ", response)
	websocketresponder.SendWebSocketResponse(ctx.Conn, websocketresponder.WebSocketResponse{Type: "mode_selected", Data: response})

	return nil
}
