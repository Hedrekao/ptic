package websockethandler

import (
	predictionhandler "backend/websocket-handler/prediction-handler"
	types "backend/websocket-handler/types"
	uploadhandler "backend/websocket-handler/upload-handler"
	websocketresponder "backend/websocket-responder"

	"fmt"
	"log"
)

func handleInitUpload(ctx *types.ConnectionContext, data interface{}) {
	dataMap, ok := data.(map[string]interface{})
	if !ok {
		fmt.Println("Error: expected map for InitUploadData, but got a different type")
		return
	}

	numberOfFiles, ok := dataMap["numberOfFiles"].(float64)
	if !ok {
		fmt.Println("Error: numberOfFiles is not a float64")
		return
	}

	ctx.TotalFilesToBeUploaded = int(numberOfFiles)
}

func handleFileUpload(ctx *types.ConnectionContext, data interface{}) {
	dataMap, ok := data.(map[string]interface{})
	if !ok {
		fmt.Println("Error: expected map for FileUploadData, but got a different type")
		return
	}

	fileUploadData := types.FileUploadData{
		FileName: dataMap["fileName"].(string),
		FileData: dataMap["fileData"].(string),
	}

	if err := uploadhandler.HandleFileUpload(fileUploadData); err != nil {
		log.Println("Error handling file upload:", err)
	}

	log.Println("File uploaded:", fileUploadData.FileName)

	ctx.FilesUploaded++
	ctx.FilesToPredict = append(ctx.FilesToPredict, fileUploadData.FileName)

	websocketresponder.SendUploadProgress(ctx)
	fmt.Println("Received filename:", fileUploadData.FileName)
}

func handleSelectMode(ctx *types.ConnectionContext, data interface{}) {
	fmt.Println(data)
	dataMap, ok := data.(map[string]interface{})
	if !ok {
		fmt.Println("Error: expected map for SelectMode, but got a different type")
		return
	}
	fmt.Println(dataMap)
	fmt.Println(dataMap["mode"])

	mode := dataMap["mode"].(string)

	modeSelectData := types.SelectModeData{
		Mode: types.EMode(mode),
	}

	ctx.SelectedMode = modeSelectData.Mode

	websocketresponder.SendModeSelected(ctx)
	fmt.Println("Mode selected for connection:", ctx.Id)
}

func handleInitPredictions(ctx *types.ConnectionContext) {
	predictionhandler.HandlePrediction(ctx)
	websocketresponder.SendPredictionProgress(ctx)
}

func handlePredictionApproval(ctx *types.ConnectionContext, data interface{}) {
	dataMap, ok := data.(map[string]interface{})
	if !ok {
		fmt.Println("Error: expected map for PredictionApprovalData, but got a different type")
		return
	}

	predictionApprovalData := types.PredictionApprovalData{
		FilePath: dataMap["fileName"].(string),
		Class:    dataMap["class"].(string),
	}

	predictionhandler.HandlePredictionApproval(ctx, predictionApprovalData)
}
