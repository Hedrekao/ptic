package websockethandler

import (
	predictionhandler "backend/websocket-handler/prediction-handler"
	types "backend/websocket-handler/types"
	uploadhandler "backend/websocket-handler/upload-handler"
	websocketresponder "backend/websocket-responder"
	"path/filepath"

	"log"
)

func handleInitUpload(ctx *types.ConnectionContext, data interface{}) {
	dataMap, ok := data.(map[string]interface{})
	if !ok {
		log.Println("Error: expected map for InitUploadData, but got a different type")
		return
	}

	numberOfFiles, ok := dataMap["numberOfFiles"].(float64)
	if !ok {
		log.Println("Error: numberOfFiles is not a float64")
		return
	}

	rootDir, ok := dataMap["rootDir"].(string)
	if !ok {
		log.Println("Error: rootDir is not a string")
		return
	}

	uploadId, ok := dataMap["uploadId"].(float64)
	if !ok {
		log.Println("Error: uploadId is not an float64")
		return
	}

	ctx.TotalFilesToBeUploaded = int(numberOfFiles)
	ctx.RootDir = rootDir
	ctx.IsUploadCancelled = false
	ctx.FilesUploaded = 0
	ctx.UploadId = uploadId
}

func handleCancelUpload(ctx *types.ConnectionContext) {
	ctx.RootDir = ""
	ctx.FilesUploaded = 0
	ctx.FilesToPredict = make(map[string][]string)
	ctx.IsUploadCancelled = true
}

func handleFileUpload(ctx *types.ConnectionContext, data interface{}) {
	if ctx.IsUploadCancelled {
		log.Println("Upload cancelled, ignoring file upload")
		return
	}

	dataMap, ok := data.(map[string]interface{})
	if !ok {
		log.Println("Error: expected map for FileUploadData, but got a different type")
		return
	}

	fileUploadData := types.FileUploadData{
		FileName: dataMap["fileName"].(string),
		FileData: dataMap["fileData"].(string),
	}

	if err := uploadhandler.HandleFileUpload(ctx, fileUploadData); err != nil {
		log.Println("Error handling file upload:", err)
		return
	}

	log.Println("File uploaded:", fileUploadData.FileName)

	// Extract productName from either a file name or directory
	// We use this a key in a map containing paths for files to predict
	// This allows us to have multiple images for the same product
	dirPath, fileNameWithExt := filepath.Split(fileUploadData.FileName)
	dirPath = filepath.Clean(dirPath)

	var productName string
	if dirPath == ctx.RootDir {
		ext := filepath.Ext(fileNameWithExt)
		productName = fileNameWithExt[:len(fileNameWithExt)-len(ext)]
	} else {
		_, itemDir := filepath.Split(dirPath)
		productName = itemDir
	}

	ctx.FilesUploaded++
	ctx.FilesToPredict[productName] = append(ctx.FilesToPredict[productName], fileUploadData.FileName)

	websocketresponder.SendUploadProgress(ctx)
	log.Println("Received filename:", fileUploadData.FileName)
}

func handleSelectMode(ctx *types.ConnectionContext, data interface{}) {
	dataMap, ok := data.(map[string]interface{})
	if !ok {
		log.Println("Error: expected map for SelectMode, but got a different type")
		return
	}

	mode := dataMap["mode"].(string)

	modeSelectData := types.SelectModeData{
		Mode: types.EMode(mode),
	}

	ctx.SelectedMode = modeSelectData.Mode

	websocketresponder.SendModeSelected(ctx)
	log.Println("Mode selected for connection:", ctx.Id)
}

func handleInitPredictions(ctx *types.ConnectionContext) {
	predictionhandler.HandlePrediction(ctx)
	websocketresponder.SendPredictionProgress(ctx)
}

func handlePredictionApproval(ctx *types.ConnectionContext, data interface{}) {
	dataMap, ok := data.(map[string]interface{})
	if !ok {
		log.Println("Error: expected map for PredictionApprovalData, but got a different type")
		return
	}

	predictionApprovalData := types.PredictionApprovalData{
		ProductName: dataMap["productName"].(string),
		Class:       dataMap["class"].(string),
	}

	predictionhandler.HandlePredictionApproval(ctx, predictionApprovalData)
}
