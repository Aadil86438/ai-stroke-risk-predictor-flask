package main

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
)


type Response struct {
	Status string `json:"status"`
	Result int    `json:"result"`
	ErrMsg string `json:"errmsg"`
}


func sumHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("sumHandler (+)")

	
	resp := Response{Status: "error"}

	
	if r.Method == http.MethodGet {
		
		num1Str := r.Header.Get("num1")
		num2Str := r.Header.Get("num2")

		
		num1, err1 := strconv.Atoi(num1Str)
		num2, err2 := strconv.Atoi(num2Str)

		if err1 != nil || err2 != nil {
			resp.ErrMsg = "num1 or num2 invalid"
		} else {
	
			resp.Status = "success"
			resp.Result = num1 + num2
		}
	} else {
		resp.ErrMsg = "Only GET method allowed"
	}

	w.Header().Set("Content-Type", "application/json")
	err := json.NewEncoder(w).Encode(resp)
	if err != nil {
		http.Error(w, "Encoding error", http.StatusInternalServerError)
	}

	log.Println("sumHandler (-)")
}

func main() {
	http.HandleFunc("/sum", sumHandler)
	log.Println(" Server started at :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
