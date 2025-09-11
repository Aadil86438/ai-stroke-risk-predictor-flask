package main

import (
	"fmt"
	"time"

	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

// Struct for st1006_customers table
type Customer struct {
	ID           uint      `gorm:"primaryKey"`
	CustomerName string
	City         string
	PostalCode   string
	CreatedBy    string
	UpdatedBy    string
	CreatedAt    time.Time
	UpdatedAt    time.Time
}

// Connect DB
func connectDB() *gorm.DB {
	dsn := "root:Best@123@tcp(192.168.2.5:3306)/training?parseTime=true"
	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
	if err != nil {
		panic("❌ Failed to connect database")
	}
	return db
}

func main() {
	db := connectDB()

	// ✅ Insert (Create)
	newCustomer := Customer{
		CustomerName: "adili",
		City:         "Chennai",
		PostalCode:   "600001",
		CreatedBy:    "admin",
		UpdatedBy:    "admin",
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}
	if err := db.Create(&newCustomer).Error; err != nil {
		fmt.Println("Error creating:", err)
	} else {
		fmt.Println("Inserted:", newCustomer)
	}

	// ✅ Select all (Find)
	var customers []Customer
	if err := db.Find(&customers).Error; err != nil {
		fmt.Println("Error fetching:", err)
	} else {
		fmt.Println("All Customers:", customers)
	}

	// ✅ Select first (First)
	var firstCustomer Customer
	if err := db.First(&firstCustomer).Error; err != nil {
		fmt.Println("Error fetching first:", err)
	} else {
		fmt.Println("First Customer:", firstCustomer)
	}

	// ✅ Update
	if err := db.Model(&firstCustomer).Update("City", "Bangalore").Error; err != nil {
		fmt.Println("Error updating:", err)
	} else {
		fmt.Println("Updated Customer:", firstCustomer)
	}

	// ✅ Delete
	if err := db.Delete(&firstCustomer).Error; err != nil {
		fmt.Println("Error deleting:", err)
	} else {
		fmt.Println("Deleted Customer with ID:", firstCustomer.ID)
	}
}
