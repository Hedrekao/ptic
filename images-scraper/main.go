package main

import (
	"context"
	"encoding/csv"
	"fmt"
	"io"
	"net/http"
	"os"
	"path"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

const (
	baseImagenetURL  = "https://www.image-net.org/api/imagenet.synset.geturls"
	baseImagenetPath = "images"
	baseSallingPath  = "images-salling"
)

func main() {

	if len(os.Args) < 2 {
		panic("Missing mode, either 'imagenet' or 'salling'")
	}

	mode := os.Args[1]

	switch mode {
	case "imagenet":
		imageNetScraper()
	case "salling":
		sallingScraper()
	}

}

func imageNetScraper() {

	categories := os.Args[2:]

	if len(categories) == 0 {
		panic("Missing categories to scrape")
	}

	for _, category := range categories {
		scrapeImages(category, baseImagenetURL, baseImagenetPath)
	}
}

func sallingScraper() {

	if len(os.Args) < 5 {
		panic("Too little arguments")
	}

	baseSallingURL := os.Args[2]
	images_csv := os.Args[3]
	product_csv := os.Args[4]

	categoryMapping := createCategoryMappping(product_csv)

	fmt.Println("Category mapping created")

	file, err := os.Open(images_csv)
	if err != nil {
		panic(err)
	}
	defer file.Close()

	reader := csv.NewReader(file)

	// Read and process the header
	_, err = reader.Read()
	if err != nil {
		panic(err)
	}

	// Process each row
	semaphore := make(chan struct{}, 50)
	wg := sync.WaitGroup{}
	var atomicCounter int64
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break // End of file
		}
		if err != nil {
			panic(err)
		}

		product_id := record[1]
		image_id := record[2]

		timeout := 10 * time.Second
		wg.Add(1)

		var categories []string
		if strings.Contains(product_id, ";") {
			product_ids := strings.Split(product_id, ";")
			categories = make([]string, len(product_ids))

			for i, product_id := range product_ids {
				categories[i] = categoryMapping[product_id]
			}

		} else {
			categories = []string{categoryMapping[product_id]}
		}

		var folderPaths []string
		for _, category := range categories {
			folderPath := path.Join(baseSallingPath, category)
			if err := os.MkdirAll(folderPath, os.ModePerm); err != nil {
				panic(err)
			}
			folderPaths = append(folderPaths, folderPath)
		}

		go func(url, fileName string, atomicCounter *int64) {
			defer wg.Done()
			semaphore <- struct{}{}
			defer func() {
				<-semaphore
			}()
			ctx, cancel := context.WithTimeout(context.Background(), timeout)
			defer cancel()
			downloadImage(ctx, url, folderPaths, fileName, atomicCounter)
		}(baseSallingURL+fmt.Sprintf("/%s", image_id), fmt.Sprintf("%s.jpg", image_id), &atomicCounter)

	}

	wg.Wait()

}

func createCategoryMappping(product_csv string) map[string]string {
	mapping := make(map[string]string)

	file, err := os.Open(product_csv)
	if err != nil {
		panic(err)
	}
	defer file.Close()

	reader := csv.NewReader(file)

	// Read and process the header
	_, err = reader.Read()
	if err != nil {
		panic(err)
	}

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break // End of file
		}
		if err != nil {
			panic(err)
		}

		category := record[2]
		product_id := record[3]

		mapping[product_id] = category
	}

	return mapping
}

func scrapeImages(category, baseURL, basePath string) {

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

	id := 0
	wg := sync.WaitGroup{}
	for _, url := range urls {
		id++
		wg.Add(1)
		go func(url, fileName string) {
			defer wg.Done()
			semaphore <- struct{}{}
			defer func() {
				<-semaphore
			}()
			ctx, cancel := context.WithTimeout(context.Background(), timeout)
			defer cancel()
			downloadImage(ctx, url, []string{folderPath}, fileName, nil)
		}(url, fmt.Sprintf("%d.jpg", id))
	}

	wg.Wait()

	files, err := os.ReadDir(folderPath)
	if err != nil {
		fmt.Println("Error reading directory", folderPath)
		return
	}

	fmt.Println("Finished downloading", len(files), "images for category", category)
}

func downloadImage(ctx context.Context, url string, folderPath []string, fileName string, atomicCounter *int64) {

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

	for _, folderPath := range folderPath {

		filePath := path.Join(folderPath, fileName)

		file, err := os.Create(filePath)

		if err != nil {
			return
		}

		defer file.Close()

		// write the image to the file
		_, err = io.Copy(file, resp.Body)

		if err != nil {
			println("Error copying image to file", err)
			return
		}
	}

	n_products := atomic.AddInt64(atomicCounter, 1)

	if n_products%1000 == 0 {
		fmt.Printf("Downloaded %d images\n", n_products)
	}

}
