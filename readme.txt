package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

// Request structure
type AddRequest struct {
	Num1 int `json:"num1"`
	Num2 int `json:"num2"`
}

// Response structure
type AddResponse struct {
	Result int    `json:"result"`
	Status string `json:"status"`
}

// ------------ SERVER ------------
func addHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Only POST allowed", http.StatusMethodNotAllowed)
		return
	}
	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Error reading body", http.StatusBadRequest)
		return
	}

	var req AddRequest
	if err := json.Unmarshal(body, &req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	res := AddResponse{Result: req.Num1 + req.Num2, Status: "success"}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(res)
}

// ------------ CLIENT ------------
func callAddAPI(num1, num2 int) {
	reqData := AddRequest{Num1: num1, Num2: num2}
	jsonData, _ := json.Marshal(reqData)

	url := "http://localhost:8080/add"
	request, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	request.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	response, err := client.Do(request)
	if err != nil {
		fmt.Println("Error calling API:", err)
		return
	}
	defer response.Body.Close()

	body, _ := io.ReadAll(response.Body)

	var res AddResponse
	json.Unmarshal(body, &res)

	fmt.Println("API Response:", res)
}

func main() {
	// Run server in goroutine
	go func() {
		http.HandleFunc("/add", addHandler)
		fmt.Println("Server started at :8080")
		http.ListenAndServe(":8080", nil)
	}()

	// Call the API as client
	callAddAPI(5, 15)
}
