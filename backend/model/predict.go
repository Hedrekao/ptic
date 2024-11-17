package model

import (
	"backend/websocket-handler/types"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sort"
)

func Predict(filePath string, predictionServiceUrl string, ctx *types.ConnectionContext) (PredictionResponse, error) {
	requestBody := PredictBody{
		FilePath: filePath,
	}
	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		return PredictionResponse{}, fmt.Errorf("failed to marshal request body: %w", err)
	}

	// Send POST request with the JSON data
	res, err := http.Post(predictionServiceUrl, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return PredictionResponse{}, fmt.Errorf("failed to make POST request: %w", err)
	}
	defer res.Body.Close()

	// Read the response body
	body, err := io.ReadAll(res.Body)
	if err != nil {
		return PredictionResponse{}, fmt.Errorf("failed to read response body: %w", err)
	}

	// Unmarshal the response JSON into the PredictionResponse struct
	var predictionResponse PredictionResponse
	if err := json.Unmarshal(body, &predictionResponse); err != nil {
		return PredictionResponse{}, fmt.Errorf("failed to unmarshal response JSON: %w", err)
	}

	return predictionResponse, nil
}

func MapToPredictionFile(productName string, predictionResponse map[string]float64, filePaths []string) types.PredictionFile {
	var predictedClasses []types.PredictedClass

	// Iterate over the predictions and populate the PredictedClasses slice
	for class, weight := range predictionResponse {
		predictedClasses = append(predictedClasses, types.PredictedClass{
			Class:  class,
			Weight: weight,
		})
	}

	// Sort slice as map in go is not ordered
	// also the order might have became unstable becomes the weights might have averaged
	sort.Slice(predictedClasses, func(i, j int) bool {
		return predictedClasses[i].Weight > predictedClasses[j].Weight
	})

	predictedClasses = predictedClasses[:5]

	// Create and return the PredictionFile
	return types.PredictionFile{
		ProductName:      productName,
		PredictedClasses: predictedClasses,
		FilePaths:        filePaths,
	}
}
