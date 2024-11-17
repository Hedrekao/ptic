package uploadshandler

import (
	"io"
	"net/http"
	"strings"

	"github.com/Azure/azure-sdk-for-go/sdk/storage/azblob"
)

func HandleUploads(blobClient *azblob.Client) http.HandlerFunc {

	if blobClient != nil {
		return handleAzureUploads(blobClient)
	}

	fs := http.FileServer(http.Dir("./uploads"))
	fileServer := http.StripPrefix("/uploads/", fs)

	return fileServer.ServeHTTP
}

func handleAzureUploads(blobClient *azblob.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		path := strings.TrimPrefix(r.URL.Path, "/uploads/")

		// Get blob data
		blobDownloadResponse, err := blobClient.DownloadStream(
			r.Context(),
			"images",
			path,
			nil,
		)

		defer blobDownloadResponse.Body.Close()

		if err != nil {
			if strings.Contains(err.Error(), "BlobNotFound") {
				http.NotFound(w, r)
				return
			}
			http.Error(w, "Failed to download file", http.StatusInternalServerError)
			return
		}

		// Set content type if available
		if blobDownloadResponse.ContentType != nil {
			w.Header().Set("Content-Type", *blobDownloadResponse.ContentType)
		}

		// Copy the blob data to the response writer
		_, err = io.Copy(w, blobDownloadResponse.Body)
		if err != nil {
			http.Error(w, "Failed to stream file", http.StatusInternalServerError)
			return
		}
	}
}
