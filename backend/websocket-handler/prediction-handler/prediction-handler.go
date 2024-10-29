package predictionhandler

import (
	"backend/model"
	"backend/websocket-handler/types"
)

func HandlePrediction(ctx *types.ConnectionContext) error {
	// Predict the files
	for _, file := range ctx.FilesToPredict {
		err := predictFile(file, ctx)
		if err != nil {
			return err
		}
		// TODO: continue here
	}

	return nil
}

func predictFile(filePath string, ctx *types.ConnectionContext) error {
	prediction, err := model.Predict(filePath, ctx)
	if err != nil {
		return err
	}

	switch ctx.SelectedMode {
	case types.ModeClassification:
	}

	ctx.SelectedMode

	ctx.PredictionFiles = append(ctx.PredictionFiles, prediction)

	return nil
}
