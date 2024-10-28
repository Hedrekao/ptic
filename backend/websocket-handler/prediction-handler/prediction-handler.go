package predictionhandler

import (
	"backend/model"
	"backend/websocket-handler/types"
)

func HandlePrediction(ctx *types.ConnectionContext) error {
	// Predict the files
	for _, file := range ctx.FilesToPredict {
		prediction, err := model.Predict(file, ctx)
		if err != nil {
			return err
		}

		// TODO: continue here
	}

	return nil
}
