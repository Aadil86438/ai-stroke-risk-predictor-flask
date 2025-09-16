package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

// Request struct for input
type CalcRequest struct {
	Num1      float64 `json:"num1"`
	Num2      float64 `json:"num2"`
	Operation string  `json:"operation"` // "add", "sub", "mul", "div"
}

// Response struct for output
type CalcResponse struct {
	Result float64 `json:"result"`
	Error  string  `json:"error,omitempty"`
}

func calculateHandler(w http.ResponseWriter, r *http.Request) {
	var req CalcRequest
	var res CalcResponse

	// Decode JSON request
	err := json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	// Perform operation
	switch req.Operation {
	case "add":
		res.Result = req.Num1 + req.Num2
	case "sub":
		res.Result = req.Num1 - req.Num2
	case "mul":
		res.Result = req.Num1 * req.Num2
	case "div":
		if req.Num2 == 0 {
			res.Error = "Division by zero not allowed"
		} else {
			res.Result = req.Num1 / req.Num2
		}
	default:
		res.Error = "Invalid operation. Use add, sub, mul, div"
	}

	// Send JSON response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(res)
}

func main() {
	http.HandleFunc("/calculate", calculateHandler)
	fmt.Println("🚀 Server running on http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}


{
  "num1": 10,
  "num2": 5,
  "operation": "add"
}
