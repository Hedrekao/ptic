package main

import (
	websockethandler "backend/websocket-handler"
	"log"
	"net/http"
	"os"

	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	// If environment is Azure, create a new Blob client
	var blobClient *azblob.Client
	if os.Getenv("ENV") == "AZURE" {
		blobConnectionString, ok := os.LookupEnv("BLOB_STORAGE_CONNECTION_STRING")

		if !ok {
			log.Fatal("Error getting blob storage connection string:", err)
		}

		blobClient, err = azblob.NewClientFromConnectionString(blobConnectionString, nil)

		if err != nil {
			log.Fatal("Error creating blob client:", err)
		}
	}

	log.Println("Server starting...")
	http.HandleFunc("/ws", websockethandler.HandleWebSocketConnection(blobClient))

	fs := http.FileServer(http.Dir("./uploads"))
	http.Handle("/uploads/", http.StripPrefix("/uploads", fs))

	err = http.ListenAndServe(":4200", nil)
	if err != nil {
		log.Fatal("Error starting server:", err)
	}
}
