package main

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

type Task struct {
	ID          int
	Title       string
	Description string
	Time        string
}

const fileName = "todos.csv"

// read tasks from csv
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
		if len(rec) == 4 {
			id, _ := strconv.Atoi(rec[0])
			tasks = append(tasks, Task{id, rec[1], rec[2], rec[3]})
		}
	}
	return tasks, nil
}

// write tasks to csv
func writeCSV(tasks []Task) error {
	file, err := os.Create(fileName)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, t := range tasks {
		record := []string{strconv.Itoa(t.ID), t.Title, t.Description, t.Time}
		if err := writer.Write(record); err != nil {
			return err
		}
	}
	return nil
}

// check time format and 5 min gap
func isValidTime(input string, tasks []Task) bool {
	formats := []string{"3:04PM", "3:04 PM", "03:04PM", "03:04 PM", "15:04"}
	var newTime time.Time
	var err error

	input = strings.ToUpper(strings.TrimSpace(input))

	ok := false
	for _, f := range formats {
		newTime, err = time.Parse(f, input)
		if err == nil {
			ok = true
			break
		}
	}
	if !ok {
		return false
	}

	for _, t := range tasks {
		var exist time.Time
		for _, f := range formats {
			exist, err = time.Parse(f, t.Time)
			if err == nil {
				break
			}
		}
		diff := newTime.Sub(exist)
		if diff < 0 {
			diff = -diff
		}
		if diff < 5*time.Minute {
			return false
		}
	}
	return true
}

// add task
func addTask() {
	tasks, _ := readCSV()
	var title, desc, t string

	fmt.Print("Enter Title: ")
	fmt.Scanln(&title)
	fmt.Print("Enter Description: ")
	fmt.Scanln(&desc)
	fmt.Print("Enter Time (e.g., 4:05PM or 04:05 PM): ")
	fmt.Scanln(&t)

	if !isValidTime(t, tasks) {
		fmt.Println("❌ Invalid time or less than 5 minutes gap")
		return
	}

	newID := 1
	if len(tasks) > 0 {
		newID = tasks[len(tasks)-1].ID + 1
	}

	tasks = append(tasks, Task{newID, title, desc, strings.ToUpper(strings.TrimSpace(t))})

	if err := writeCSV(tasks); err != nil {
		fmt.Println("Error saving task:", err)
		return
	}
	fmt.Println("✅ Task added successfully")
}

// list tasks
func listTasks() {
	tasks, _ := readCSV()
	if len(tasks) == 0 {
		fmt.Println("No tasks found")
		return
	}
	fmt.Println("---- Your Tasks ----")
	for _, t := range tasks {
		fmt.Printf("[%d] %s | %s | %s\n", t.ID, t.Title, t.Description, t.Time)
	}
}

// update task
func updateTask() {
	tasks, _ := readCSV()
	listTasks()
	if len(tasks) == 0 {
		return
	}
	var id int
	fmt.Print("Enter Task ID to update: ")
	fmt.Scanln(&id)

	if id < 1 || id > len(tasks) {
		fmt.Println("❌ Invalid Task ID")
		return
	}
	var newDesc string
	fmt.Print("Enter new Description: ")
	fmt.Scanln(&newDesc)

	tasks[id-1].Description = newDesc
	if err := writeCSV(tasks); err != nil {
		fmt.Println("Error updating task:", err)
		return
	}
	fmt.Println("✅ Task updated successfully")
}

// delete task
func deleteTask() {
	tasks, _ := readCSV()
	listTasks()
	if len(tasks) == 0 {
		return
	}
	var id int
	fmt.Print("Enter Task ID to delete: ")
	fmt.Scanln(&id)

	if id < 1 || id > len(tasks) {
		fmt.Println("❌ Invalid Task ID")
		return
	}
	tasks = append(tasks[:id-1], tasks[id:]...)

	// reset IDs
	for i := range tasks {
		tasks[i].ID = i + 1
	}

	if err := writeCSV(tasks); err != nil {
		fmt.Println("Error deleting task:", err)
		return
	}
	fmt.Println("✅ Task deleted successfully")
}

// main menu
func main() {
	for {
		fmt.Println("\n---- ToDo List ----")
		fmt.Println("1. Add Task")
		fmt.Println("2. List Tasks")
		fmt.Println("3. Update Task")
		fmt.Println("4. Delete Task")
		fmt.Println("5. Exit")

		var choice int
		fmt.Print("Enter choice: ")
		fmt.Scanln(&choice)

		if choice == 1 {
			addTask()
		} else if choice == 2 {
			listTasks()
		} else if choice == 3 {
			updateTask()
		} else if choice == 4 {
			deleteTask()
		} else if choice == 5 {
			fmt.Println("Goodbye!")
			return
		} else {
			fmt.Println("❌ Invalid choice")
		}
	}
}
