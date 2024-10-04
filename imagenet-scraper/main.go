package main

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"path"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

const (
	baseURL  = "https://www.image-net.org/api/imagenet.synset.geturls"
	basePath = "images"
)

func main() {

	maxImages, err := strconv.Atoi(os.Args[1])

	if err != nil {
		panic("Invalid max images")
	}

	categories := os.Args[2:]

	if len(categories) == 0 {
		panic("Missing categories to scrape")
	}

	for _, category := range categories {
		scrapeImages(category, maxImages)
	}

}

func scrapeImages(category string, maxImages int) {

	// create a folder for the category
	folderPath := path.Join(basePath, category)
	timeout := 10 * time.Second

	if err := os.MkdirAll(folderPath, os.ModePerm); err != nil {
		panic(err)
	}

	// get the urls for the category
	resp, err := http.Get(baseURL + "?wnid=" + category)

	if err != nil {
		fmt.Println("Error fetching urls for category", category)
		return
	}

	defer resp.Body.Close()

	// read the response body

	body, err := io.ReadAll(resp.Body)

	if err != nil {
		fmt.Println("Error reading response body for category", category)
		return
	}

	stringBody := string(body)

	urls := strings.Split(stringBody, "\r\n")

	fmt.Println("Found", len(urls), "urls for category", category)

	// download the images

	semaphore := make(chan struct{}, 20)

	var downloadedImages int32
	wg2 := sync.WaitGroup{}
	for _, url := range urls {
		wg2.Add(1)
		go func(url string) {
			defer wg2.Done()
			semaphore <- struct{}{}
			defer func() {
				<-semaphore
			}()
			ctx, cancel := context.WithTimeout(context.Background(), timeout)
			defer cancel()
			downloadImage(ctx, url, folderPath, &downloadedImages, maxImages)
		}(url)
	}

	wg2.Wait()

	files, err := os.ReadDir(folderPath)
	if err != nil {
		fmt.Println("Error reading directory", folderPath)
		return
	}

	fmt.Println("Finished downloading", len(files), "images for category", category)
}

func downloadImage(ctx context.Context, url, folderPath string, downloadedImages *int32, maxImages int) {

	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)

	if err != nil {
		return
	}

	resp, err := http.DefaultClient.Do(req)

	if err != nil {
		return
	}

	if resp.StatusCode != http.StatusOK {
		return
	}

	defer resp.Body.Close()

	// create a file to save the image
	photoId := atomic.AddInt32(downloadedImages, 1)

	if photoId > int32(maxImages) {
		return
	}

	filePath := path.Join(folderPath, fmt.Sprintf("%d.jpg", photoId))

	file, err := os.Create(filePath)

	if err != nil {
		return
	}

	defer file.Close()

	// write the image to the file

	_, err = io.Copy(file, resp.Body)

	if err != nil {
		os.Remove(filePath)
		atomic.AddInt32(downloadedImages, -1)
		return
	}

}
