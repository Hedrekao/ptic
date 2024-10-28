package model

import (
	"backend/websocket-handler/types"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

const MODEL_URL = "http://localhost:8000/predict"

func Predict(filePath string, ctx *types.ConnectionContext) (types.PredictionFile, error) {
	requestBody := PredictBody{
		FilePath: filePath,
	}
	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		return types.PredictionFile{}, fmt.Errorf("failed to marshal request body: %w", err)
	}

	// Send POST request with the JSON data
	res, err := http.Post(MODEL_URL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return types.PredictionFile{}, fmt.Errorf("failed to make POST request: %w", err)
	}
	defer res.Body.Close()

	// Read the response body
	body, err := io.ReadAll(res.Body)
	if err != nil {
		return types.PredictionFile{}, fmt.Errorf("failed to read response body: %w", err)
	}

	// Unmarshal the response JSON into the PredictionResponse struct
	var predictionResponse PredictionResponse
	if err := json.Unmarshal(body, &predictionResponse); err != nil {
		return types.PredictionFile{}, fmt.Errorf("failed to unmarshal response JSON: %w", err)
	}

	return mapToPredictionFile(filePath, predictionResponse), nil
}

func mapToPredictionFile(filePath string, predictionResponse PredictionResponse) types.PredictionFile {
	var predictedClasses []types.PredictedClass

	// Iterate over the predictions and populate the PredictedClasses slice
	for class, weight := range predictionResponse.Predictions {
		predictedClasses = append(predictedClasses, types.PredictedClass{
			Class:  class,
			Weight: weight,
		})
	}

	// Create and return the PredictionFile
	return types.PredictionFile{
		FilePath:         filePath,
		PredictedClasses: predictedClasses,
	}
}
