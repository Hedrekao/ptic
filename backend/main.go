package main

import (
	websockethandler "backend/websocket-handler"
	"log"
	"net/http"

	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	log.Println("Server starting...")
	http.HandleFunc("/ws", websockethandler.HandleWebSocketConnection)

	fs := http.FileServer(http.Dir("./uploads"))
	http.Handle("/uploads/", http.StripPrefix("/uploads", fs))

	err = http.ListenAndServe(":4200", nil)
	if err != nil {
		log.Fatal("Error starting server:", err)
	}
}
