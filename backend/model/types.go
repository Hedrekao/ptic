package model

type PredictBody struct {
	FilePath string `json:"filePath"`
}

type PredictionResponse struct {
	Predictions map[string]float64 `json:"predictions"`
}
