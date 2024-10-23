package inituploadhandler

type InitUploadData struct {
	NumberOfFiles int `json:"numberOfFiles"`
}

var FilesUploaded = 0
var TotalFilesToBeUploaded = 0

func HandleInitUpload(Data InitUploadData) {
	TotalFilesToBeUploaded = Data.NumberOfFiles
}
