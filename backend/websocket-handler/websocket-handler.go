package websockethandler

import (
	"backend/file-handler"
	"fmt"
	"net/http"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		// Allow all origins (for testing). You can add proper checks later.
		return true
	},
}

// HandleWebSocketConnection upgrades the connection to WebSocket and handles file uploads
func HandleWebSocketConnection(w http.ResponseWriter, r *http.Request) {
	// Upgrade the HTTP connection to a WebSocket connection
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		http.Error(w, "Could not upgrade to WebSocket", http.StatusInternalServerError)
		return
	}
	defer conn.Close()

	fmt.Println("New connection from:", conn.RemoteAddr())

	// Handle the incoming file and save it
	if err := filehandler.SaveFileFromWebSocket(conn); err != nil {
		fmt.Println("Error handling file:", err)
		conn.WriteMessage(websocket.TextMessage, []byte("Error: "+err.Error()))
		return
	}

	// Send a success message back to the client
	conn.WriteMessage(websocket.TextMessage, []byte("File received successfully"))
}
