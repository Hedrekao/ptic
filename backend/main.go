package main

import (
	websockethandler "backend/websocket-handler"
	"fmt"
	"net/http"
)

func main() {
	fmt.Println("Server starting...")
	http.HandleFunc("/ws", websockethandler.HandleWebSocketConnection)

	err := http.ListenAndServe(":4200", nil)
	if err != nil {
		fmt.Println("Error starting server:", err)
	}
}
