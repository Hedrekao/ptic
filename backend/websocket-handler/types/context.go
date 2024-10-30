package types

import "github.com/gorilla/websocket"

type ConnectionContext struct {
	Conn                   *websocket.Conn
	Id                     string
	SelectedMode           EMode
	FilesUploaded          int
	TotalFilesToBeUploaded int
	FilesToPredict         []string
	ApprovedFiles          []ApprovedFile   // Files with final prediction, either approved or automaically predicted
	PredictionFiles        []PredictionFile // Files to be approved manually
	IsAwaitingApproval     bool
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
