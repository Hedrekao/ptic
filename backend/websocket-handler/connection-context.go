package websockethandler

import (
	types "backend/websocket-handler/types"
	uploadhandler "backend/websocket-handler/upload-handler"
	selectmoderesponder "backend/websocket-responder/select-mode-responder"
	uploadprogressresponder "backend/websocket-responder/upload-progress-responder"
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

	uploadprogressresponder.SendUploadProgress(ctx)
	fmt.Println("Received filename:", fileUploadData.FileName)
}

func handleSelectMode(ctx *types.ConnectionContext, data interface{}) {
	dataMap, ok := data.(map[string]interface{})
	if !ok {
		fmt.Println("Error: expected map for SelectMode, but got a different type")
		return
	}

	modeSelectData := types.SelectModeData{
		Mode: dataMap["mode"].(types.EMode),
	}

	ctx.SelectedMode = modeSelectData.Mode

	selectmoderesponder.SendModeSelected(ctx)
	fmt.Println("Mode selected for connection:", ctx.Id)
}

func handleInitPredictions(ctx *types.ConnectionContext) {

}
