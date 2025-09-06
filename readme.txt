package main

import (
	"encoding/csv"
	"encoding/json"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

type Task struct {
	ID          int    `json:"id"`
	Title       string `json:"title"`
	Description string `json:"description"`
	Time        string `json:"time"`
	Status      string `json:"status"`
}

type ErrorStruct struct {
	Status  string `json:"status"`
	Errcode string `json:"errcode"`
	Message string `json:"message"`
}

const fileName = "todos.csv"

func readCSV() ([]Task, error) {
	var tasks []Task
	file, err := os.OpenFile(fileName, os.O_RDONLY|os.O_CREATE, 0644)
	if err != nil {
		return tasks, err
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		return tasks, err
	}

	for _, rec := range records {
		if len(rec) == 5 {
			id, _ := strconv.Atoi(rec[0])
			tasks = append(tasks, Task{id, rec[1], rec[2], rec[3], rec[4]})
		}
	}
	return tasks, nil
}

func writeCSV(tasks []Task) error {
	file, err := os.Create(fileName)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, t := range tasks {
		record := []string{strconv.Itoa(t.ID), t.Title, t.Description, t.Time, t.Status}
		if err := writer.Write(record); err != nil {
			return err
		}
	}
	return nil
}

func addTask(w http.ResponseWriter, r *http.Request) {
	var es ErrorStruct
	title := r.URL.Query().Get("title")
	desc := r.URL.Query().Get("description")
	taskTime := r.URL.Query().Get("time")

	if strings.TrimSpace(title) == "" || strings.TrimSpace(desc) == "" {
		es.Status = "error"
		es.Errcode = "MF01"
		es.Message = "Title and Description cannot be empty"
		json.NewEncoder(w).Encode(es)
		return
	}

	tasks, _ := readCSV()
	formats := []string{"3:04PM", "3:04 PM"}
	var newTime time.Time
	valid := false
	for _, f := range formats {
		t, err := time.Parse(f, taskTime)
		if err == nil {
			newTime = t
			valid = true
			break
		}
	}
	if !valid {
		es.Status = "error"
		es.Errcode = "MF02"
		es.Message = "Invalid time format"
		json.NewEncoder(w).Encode(es)
		return
	}

	for _, t := range tasks {
		for _, f := range formats {
			exist, err := time.Parse(f, t.Time)
			if err == nil {
				diff := newTime.Sub(exist)
				if diff < 5*time.Minute && diff > -5*time.Minute {
					es.Status = "error"
					es.Errcode = "MF03"
					es.Message = "Task time must be 5 minutes apart"
					json.NewEncoder(w).Encode(es)
					return
				}
			}
		}
	}

	id := len(tasks) + 1
	newTask := Task{ID: id, Title: title, Description: desc, Time: taskTime, Status: "Pending"}
	tasks = append(tasks, newTask)
	writeCSV(tasks)

	es.Status = "success"
	es.Errcode = "S01"
	es.Message = "Task added successfully"
	json.NewEncoder(w).Encode(es)
}

func listTasks(w http.ResponseWriter, r *http.Request) {
	tasks, _ := readCSV()
	json.NewEncoder(w).Encode(tasks)
}

func updateTask(w http.ResponseWriter, r *http.Request) {
	var es ErrorStruct
	idStr := r.URL.Query().Get("id")
	newDesc := r.URL.Query().Get("description")

	if strings.TrimSpace(newDesc) == "" {
		es.Status = "error"
		es.Errcode = "MF04"
		es.Message = "Description cannot be empty"
		json.NewEncoder(w).Encode(es)
		return
	}

	id, _ := strconv.Atoi(idStr)
	tasks, _ := readCSV()
	found := false
	for i := range tasks {
		if tasks[i].ID == id {
			tasks[i].Description = newDesc
			found = true
			break
		}
	}
	if !found {
		es.Status = "error"
		es.Errcode = "MF05"
		es.Message = "Task not found"
		json.NewEncoder(w).Encode(es)
		return
	}

	writeCSV(tasks)
	es.Status = "success"
	es.Errcode = "S02"
	es.Message = "Task updated successfully"
	json.NewEncoder(w).Encode(es)
}

func deleteTask(w http.ResponseWriter, r *http.Request) {
	var es ErrorStruct
	idStr := r.URL.Query().Get("id")
	id, _ := strconv.Atoi(idStr)
	tasks, _ := readCSV()
	newTasks := []Task{}
	found := false
	for _, t := range tasks {
		if t.ID != id {
			newTasks = append(newTasks, t)
		} else {
			found = true
		}
	}
	if !found {
		es.Status = "error"
		es.Errcode = "MF06"
		es.Message = "Task not found"
		json.NewEncoder(w).Encode(es)
		return
	}

	writeCSV(newTasks)
	es.Status = "success"
	es.Errcode = "S03"
	es.Message = "Task deleted successfully"
	json.NewEncoder(w).Encode(es)
}

func main() {
	http.HandleFunc("/add", addTask)
	http.HandleFunc("/list", listTasks)
	http.HandleFunc("/update", updateTask)
	http.HandleFunc("/delete", deleteTask)
	http.ListenAndServe(":8080", nil)
}
