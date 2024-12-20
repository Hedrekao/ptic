package predictionhandler

import (
	"backend/model"
	"backend/websocket-handler/types"
	websocketresponder "backend/websocket-responder"
	"fmt"
	"math"
	"os"
)

func HandlePrediction(ctx *types.ConnectionContext) {

	var predictionServiceUrl string
	if url, ok := os.LookupEnv("PREDICTION_SERVICE_URL"); ok {
		predictionServiceUrl = url + "/predict"
	} else {
		predictionServiceUrl = "http://localhost:8000/predict"
	}

	for productName, paths := range ctx.FilesToPredict {

		predictions := make(map[string]float64)
		for _, path := range paths {
			prediction, err := model.Predict(path, predictionServiceUrl, ctx)
			fmt.Println("Prediction:", prediction)
			if err != nil {
				fmt.Println("Error predicting file:", err)
				return
			}
			for class, weight := range prediction.Predictions {
				predictions[class] += weight
			}
		}

		nPredictions := float64(len(paths))
		if nPredictions != 1 {
			for class, weight := range predictions {
				finalWeight := weight / nPredictions
				finalWeight = math.Round(finalWeight*100000) / 100000
				predictions[class] = finalWeight
			}
		}

		finalPrediction := model.MapToPredictionFile(productName, predictions, paths)

		switch ctx.SelectedMode {
		case types.Automatic:
			mostProbableClass := finalPrediction.PredictedClasses[0].Class
			ctx.ApprovedFiles = append(ctx.ApprovedFiles, types.ApprovedFile{ProductName: finalPrediction.ProductName, Class: mostProbableClass})
			websocketresponder.SendPredictionProgress(ctx)
		case types.Manual:
			ctx.PredictionFiles = append(ctx.PredictionFiles, finalPrediction)
			websocketresponder.SendPredictionApprovalRequest(ctx)

		case types.SemiAutomatic:
			mostProbableClassWeight := finalPrediction.PredictedClasses[0].Weight
			secondMostProbableClassWeight := finalPrediction.PredictedClasses[1].Weight
			difference := mostProbableClassWeight - secondMostProbableClassWeight
			if difference > 0.2 {
				mostProbableClass := finalPrediction.PredictedClasses[0].Class
				ctx.ApprovedFiles = append(ctx.ApprovedFiles, types.ApprovedFile{ProductName: finalPrediction.ProductName, Class: mostProbableClass})
				websocketresponder.SendPredictionProgress(ctx)
			} else {
				ctx.PredictionFiles = append(ctx.PredictionFiles, finalPrediction)
				websocketresponder.SendPredictionApprovalRequest(ctx)
			}
		}
	}
}

func HandlePredictionApproval(ctx *types.ConnectionContext, data types.PredictionApprovalData) {
	approvedFile := types.ApprovedFile{
		ProductName: data.ProductName,
		Class:       data.Class,
	}

	ctx.ApprovedFiles = append(ctx.ApprovedFiles, approvedFile)
	ctx.IsAwaitingApproval = false

	websocketresponder.SendPredictionProgress(ctx)
	websocketresponder.SendPredictionApprovalRequest(ctx)
}
