package predictionhandler

import (
	"backend/model"
	"backend/websocket-handler/types"
	websocketresponder "backend/websocket-responder"
	"fmt"
)

func HandlePrediction(ctx *types.ConnectionContext) {
	for _, file := range ctx.FilesToPredict {
		prediction, err := model.Predict(file, ctx)
		if err != nil {
			fmt.Println("Error predicting file:", err)
		}

		fmt.Println("Prediction:", prediction)

		switch ctx.SelectedMode {
		case types.Automatic:
			mostProbableClass := prediction.PredictedClasses[0].Class
			ctx.ApprovedFiles = append(ctx.ApprovedFiles, types.ApprovedFile{FilePath: prediction.FilePath, Class: mostProbableClass})
			websocketresponder.SendPredictionProgress(ctx)
		case types.Manual:
			ctx.PredictionFiles = append(ctx.PredictionFiles, prediction)
			websocketresponder.SendPredictionApprovalRequest(ctx)

		case types.SemiAutomatic:
			mostProbableClassWeight := prediction.PredictedClasses[0].Weight
			if mostProbableClassWeight > 0.2 {
				mostProbableClass := prediction.PredictedClasses[0].Class
				ctx.ApprovedFiles = append(ctx.ApprovedFiles, types.ApprovedFile{FilePath: prediction.FilePath, Class: mostProbableClass})
				websocketresponder.SendPredictionProgress(ctx)
			} else {
				ctx.PredictionFiles = append(ctx.PredictionFiles, prediction)
				websocketresponder.SendPredictionApprovalRequest(ctx)
			}
		}
	}
}

func HandlePredictionApproval(ctx *types.ConnectionContext, data types.PredictionApprovalData) {
	approvedFile := types.ApprovedFile{
		FilePath: data.FilePath,
		Class:    data.Class,
	}

	ctx.ApprovedFiles = append(ctx.ApprovedFiles, approvedFile)
	ctx.IsAwaitingApproval = false

	websocketresponder.SendPredictionProgress(ctx)
	websocketresponder.SendPredictionApprovalRequest(ctx)
}
