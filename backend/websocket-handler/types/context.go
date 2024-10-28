package types

import "github.com/gorilla/websocket"

type ConnectionContext struct {
	Conn                   *websocket.Conn
	Id                     string
	SelectedMode           EMode
	FilesUploaded          int
	TotalFilesToBeUploaded int
}
