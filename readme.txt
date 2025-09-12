package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"io"
	"net/http"
	"strings"
)

// ---------- MODELS ----------
type User struct {
	ID     uint   `gorm:"primaryKey" json:"id"`
	Name   string `json:"name"`
	Email  string `json:"email"`
	Phone  string `json:"phone"`
	Status string `json:"status"` // Active / Inactive
}

type Bank struct {
	ID       uint   `gorm:"primaryKey" json:"id"`
	IFSC     string `json:"ifsc"`
	BankName string `json:"bank_name"`
	MICR     string `json:"micr"`
}

// ---------- DATABASE ----------
var db *gorm.DB

func connectDB() {
	// 👉 Replace with your DB credentials
	// Example for MySQL: username:password@tcp(127.0.0.1:3306)/dbname
	dsn := "username:password@tcp(localhost:3306)/yourdbname?charset=utf8mb4&parseTime=True&loc=Local"

	var err error
	db, err = gorm.Open(mysql.Open(dsn), &gorm.Config{})
	if err != nil {
		panic("❌ Failed to connect DB: " + err.Error())
	}
	fmt.Println("✅ Database Connected")

	// Auto migrate tables
	db.AutoMigrate(&User{}, &Bank{})
}

// ---------- VALIDATION ----------
func isValidPhone(phone string) bool {
	return len(phone) == 10
}

func isInvalidName(name string) bool {
	return strings.ToLower(name) == "employee"
}

// ---------- HANDLERS ----------

// 1st API: Upload CSV & call Razorpay IFSC API
func uploadCSVHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Only POST allowed", http.StatusMethodNotAllowed)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "CSV file required", http.StatusBadRequest)
		return
	}
	defer file.Close()

	reader := csv.NewReader(file)
	_, _ = reader.Read() // skip header

	inserted := 0
	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}

		name := record[0]
		email := record[1]
		phone := record[2]
		ifsc := record[3]
		accountNo := record[4] // just for info, not storing

		// ✅ Validation
		if !isValidPhone(phone) {
			fmt.Println("❌ Invalid phone skipped:", phone)
			continue
		}
		if isInvalidName(name) {
			fmt.Println("❌ Invalid name skipped:", name)
			continue
		}

		// Call Razorpay IFSC API
		resp, err := http.Get("https://ifsc.razorpay.com/" + ifsc)
		if err != nil {
			fmt.Println("❌ Razorpay call failed for:", ifsc)
			continue
		}
		defer resp.Body.Close()

		var bankResp map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&bankResp)

		// Insert user
		user := User{Name: name, Email: email, Phone: phone, Status: "Active"}
		db.Create(&user)

		// Insert bank
		bank := Bank{
			IFSC:     ifsc,
			BankName: fmt.Sprintf("%v", bankResp["BANK"]),
			MICR:     fmt.Sprintf("%v", bankResp["MICR"]),
		}
		db.Create(&bank)

		fmt.Println("✅ Inserted:", name, accountNo)
		inserted++
	}

	json.NewEncoder(w).Encode(map[string]interface{}{"message": "CSV processed", "inserted": inserted})
}

// 2nd API: List Active Users
func activeUsersHandler(w http.ResponseWriter, r *http.Request) {
	var users []User
	db.Where("status = ?", "Active").Find(&users)
	json.NewEncoder(w).Encode(users)
}

// 3rd API: Check Inactive Users
func inactiveUsersHandler(w http.ResponseWriter, r *http.Request) {
	var input struct {
		Email string `json:"email"`
		Phone string `json:"phone"`
	}
	json.NewDecoder(r.Body).Decode(&input)

	var users []User
	db.Where("status = ? AND (email = ? OR phone = ?)", "Inactive", input.Email, input.Phone).Find(&users)

	if len(users) == 0 {
		http.Error(w, "No inactive user found", http.StatusNotFound)
		return
	}
	json.NewEncoder(w).Encode(users)
}

// 4th API: Check Duplicate
func duplicateHandler(w http.ResponseWriter, r *http.Request) {
	var input struct {
		Email string `json:"email"`
		Phone string `json:"phone"`
		IFSC  string `json:"ifsc"`
	}
	json.NewDecoder(r.Body).Decode(&input)

	var user User
	var bank Bank

	errUser := db.Where("email = ? OR phone = ?", input.Email, input.Phone).First(&user).Error
	errBank := db.Where("ifsc = ?", input.IFSC).First(&bank).Error

	if errUser == nil || errBank == nil {
		http.Error(w, "Duplicate found", http.StatusBadRequest)
		return
	}
	json.NewEncoder(w).Encode(map[string]string{"message": "No duplicate"})
}

// 5th API: Fetch User Details
func userDetailsHandler(w http.ResponseWriter, r *http.Request) {
	var input struct {
		Email string `json:"email"`
		Phone string `json:"phone"`
	}
	json.NewDecoder(r.Body).Decode(&input)

	var user User
	err := db.Where("email = ? AND phone = ?", input.Email, input.Phone).First(&user).Error
	if err != nil {
		http.Error(w, "User not found", http.StatusNotFound)
		return
	}
	json.NewEncoder(w).Encode(user)
}

// ---------- MAIN ----------
func main() {
	connectDB()

	http.HandleFunc("/upload-csv", uploadCSVHandler)     // 1st API
	http.HandleFunc("/active-users", activeUsersHandler) // 2nd API
	http.HandleFunc("/inactive-users", inactiveUsersHandler) // 3rd API
	http.HandleFunc("/check-duplicate", duplicateHandler)    // 4th API
	http.HandleFunc("/user-details", userDetailsHandler)     // 5th API

	fmt.Println("🚀 Server running at http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}



POST http://localhost:8080/upload-csv
Body → form-data → file (CSV)

CSV Example:
name,email,phone,ifsc,account_no
John,john@gmail.com,9876543210,YESB0DNB002,12345
Employee,emp@gmail.com,9999999999,HDFC000123,11111
