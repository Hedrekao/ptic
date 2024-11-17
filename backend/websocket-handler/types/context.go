package types

import (
	"context"

	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
	"github.com/gorilla/websocket"
)

type ConnectionContext struct {
	Ctx                    context.Context
	Conn                   *websocket.Conn
	BlobClient             *azblob.Client
	Id                     string
	SelectedMode           EMode
	RootDir                string
	FilesUploaded          int
	TotalFilesToBeUploaded int
	FilesToPredict         map[string][]string
	ApprovedFiles          []ApprovedFile   // Files with final prediction, either approved or automaically predicted
	PredictionFiles        []PredictionFile // Files to be approved manually
	IsAwaitingApproval     bool
}

type ApprovedFile struct {
	ProductName string `json:"productName"`
	Class       string `json:"class"`
}

type PredictionFile struct {
	ProductName      string           `json:"productName"`
	PredictedClasses []PredictedClass `json:"predictedClasses"`
	FilePaths        []string         `json:"filePaths"`
}

type PredictedClass struct {
	Class  string  `json:"class"`
	Weight float64 `json:"weight"`
}
