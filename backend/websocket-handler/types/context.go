package types

import "github.com/gorilla/websocket"

type ConnectionContext struct {
	Conn                   *websocket.Conn
	Id                     string
	SelectedMode           EMode
	FilesUploaded          int
	TotalFilesToBeUploaded int
	FilesToPredict         []string
	ApprovedFiles          []ApprovedFile
	PredictionFiles        []PredictionFile
}

type ApprovedFile struct {
	FilePath string `json:"fileName"`
	Class    string `json:"class"`
}

type PredictionFile struct {
	FilePath         string           `json:"fileName"`
	PredictedClasses []PredictedClass `json:"predictedClasses"`
}

type PredictedClass struct {
	Class  string  `json:"class"`
	Weight float64 `json:"weight"`
}
