package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

type Task struct {
	ID          int    `json:"id"`
	Title       string `json:"title"`
	Description string `json:"description"`
	Status      string `json:"status"`
}

var filename = "tasks.json"

func readTasks() ([]Task, error) {
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		if os.IsNotExist(err) {
			return []Task{}, nil
		}
		return nil, err
	}
	var tasks []Task
	err = json.Unmarshal(data, &tasks)
	return tasks, err
}

func writeTasks(tasks []Task) error {
	data, err := json.Marshal(tasks)
	if err != nil {
		return err
	}
	return ioutil.WriteFile(filename, data, 0644)
}

func addTask(w http.ResponseWriter, r *http.Request) {
	var t Task
	body, _ := ioutil.ReadAll(r.Body)
	json.Unmarshal(body, &t)

	if t.Title == "" || t.Description == "" {
		http.Error(w, "Title and Description cannot be empty", http.StatusBadRequest)
		return
	}

	tasks, _ := readTasks()
	t.ID = len(tasks) + 1
	t.Status = "Pending"
	tasks = append(tasks, t)
	writeTasks(tasks)
	w.Write([]byte("Task added"))
}

func listTasks(w http.ResponseWriter, r *http.Request) {
	tasks, _ := readTasks()
	data, _ := json.Marshal(tasks)
	w.Write(data)
}

func updateTask(w http.ResponseWriter, r *http.Request) {
	var t Task
	body, _ := ioutil.ReadAll(r.Body)
	json.Unmarshal(body, &t)

	tasks, _ := readTasks()
	updated := false
	for i := range tasks {
		if tasks[i].ID == t.ID {
			if t.Title != "" {
				tasks[i].Title = t.Title
			}
			if t.Description != "" {
				tasks[i].Description = t.Description
			}
			if t.Status != "" {
				tasks[i].Status = t.Status
			}
			updated = true
			break
		}
	}
	if !updated {
		http.Error(w, "Task not found", http.StatusNotFound)
		return
	}
	writeTasks(tasks)
	w.Write([]byte("Task updated"))
}

func deleteTask(w http.ResponseWriter, r *http.Request) {
	var t Task
	body, _ := ioutil.ReadAll(r.Body)
	json.Unmarshal(body, &t)

	tasks, _ := readTasks()
	newTasks := []Task{}
	found := false
	for _, task := range tasks {
		if task.ID != t.ID {
			newTasks = append(newTasks, task)
		} else {
			found = true
		}
	}
	if !found {
		http.Error(w, "Task not found", http.StatusNotFound)
		return
	}
	writeTasks(newTasks)
	w.Write([]byte("Task deleted"))
}

func main() {
	http.HandleFunc("/add", addTask)
	http.HandleFunc("/list", listTasks)
	http.HandleFunc("/update", updateTask)
	http.HandleFunc("/delete", deleteTask)

	fmt.Println("Server running on port 8080")
	http.ListenAndServe(":8080", nil)
}
