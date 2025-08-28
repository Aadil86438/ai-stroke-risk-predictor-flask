package main

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"time"
)

// Account structure
type Account struct {
	Name    string
	Phone   string
	Pin     string
	Created string
}

func main() {
	for {
		fmt.Println("\n------ MENU ------")
		fmt.Println("1. Create Account")
		fmt.Println("2. Credit")
		fmt.Println("3. Debit")
		fmt.Println("4. Balance Check")
		fmt.Println("5. Statement")
		fmt.Println("6. Exit")

		fmt.Print("Enter your choice: ")
		var choice int
		fmt.Scan(&choice)

		switch choice {
		case 1:
			createAccount()
		case 2:
			credit()
		case 3:
			debit()
		case 4:
			balanceCheck()
		case 5:
			statement()
		case 6:
			fmt.Println("Thank you for using the system.")
			return
		default:
			fmt.Println("Invalid choice! Try again.")
		}
	}
}

// ---------------- CREATE ACCOUNT ----------------
func createAccount() {
	var name string
	var phone string
	var pin string

	fmt.Print("Enter your name: ")
	fmt.Scan(&name)
	fmt.Print("Enter phone number: ")
	fmt.Scan(&phone)
	fmt.Print("Set a 4-digit PIN: ")
	fmt.Scan(&pin)

	// read existing accounts
	accounts, _ := readAccounts("accounts.csv")

	// check duplicate phone number
	for _, acc := range accounts {
		if acc.Phone == phone {
			fmt.Println("Error: Account already exists for this number.")
			return
		}
	}

	// new account
	var acc Account
	acc.Name = name
	acc.Phone = phone
	acc.Pin = pin
	acc.Created = time.Now().Format("2006-01-02 15:04:05")

	accounts = append(accounts, acc)
	writeAccounts("accounts.csv", accounts)
	fmt.Println("Account created successfully.")
}

// ---------------- CREDIT ----------------
func credit() {
	var phone string
	var pin string
	var amt int

	fmt.Print("Enter phone number: ")
	fmt.Scan(&phone)
	fmt.Print("Enter PIN: ")
	fmt.Scan(&pin)
	fmt.Print("Enter amount to credit: ")
	fmt.Scan(&amt)

	if !accountExists(phone, pin) {
		fmt.Println("Error: Invalid account or PIN.")
		return
	}

	writeTransaction("transactions.csv", phone, pin, amt, "Credit")
	fmt.Println("Amount credited successfully.")
}

// ---------------- DEBIT ----------------
func debit() {
	var phone string
	var pin string
	var amt int

	fmt.Print("Enter phone number: ")
	fmt.Scan(&phone)
	fmt.Print("Enter PIN: ")
	fmt.Scan(&pin)
	fmt.Print("Enter amount to debit: ")
	fmt.Scan(&amt)

	if !accountExists(phone, pin) {
		fmt.Println("Error: Invalid account or PIN.")
		return
	}

	// check balance
	bal := calculateBalance(phone)
	if amt > bal {
		fmt.Println("Error: Insufficient balance.")
		return
	}

	writeTransaction("transactions.csv", phone, pin, amt, "Debit")
	fmt.Println("Amount debited successfully.")
}

// ---------------- BALANCE CHECK ----------------
func balanceCheck() {
	var phone string
	var pin string

	fmt.Print("Enter phone number: ")
	fmt.Scan(&phone)
	fmt.Print("Enter PIN: ")
	fmt.Scan(&pin)

	if !accountExists(phone, pin) {
		fmt.Println("Error: Invalid account or PIN.")
		return
	}

	bal := calculateBalance(phone)
	fmt.Println("Your current balance is:", bal)
}

// ---------------- STATEMENT ----------------
func statement() {
	var phone string
	var pin string

	fmt.Print("Enter phone number: ")
	fmt.Scan(&phone)
	fmt.Print("Enter PIN: ")
	fmt.Scan(&pin)

	if !accountExists(phone, pin) {
		fmt.Println("Error: Invalid account or PIN.")
		return
	}

	// read all transactions
	file, err := os.Open("transactions.csv")
	if err != nil {
		fmt.Println("No transactions found.")
		return
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, _ := reader.ReadAll()

	// create new statement file
	newFile := "statement_" + phone + ".csv"
	f, _ := os.Create(newFile)
	defer f.Close()
	writer := csv.NewWriter(f)
	defer writer.Flush()

	// write header
	writer.Write([]string{"Phone", "PIN", "Amount", "Type", "Time"})

	// write only this account transactions
	for _, rec := range records {
		if rec[0] == phone && rec[1] == pin {
			writer.Write(rec)
		}
	}

	fmt.Println("Statement saved to:", newFile)
}

// ---------------- HELPER FUNCTIONS ----------------
func readAccounts(fileName string) ([]Account, error) {
	var accounts []Account
	file, err := os.Open(fileName)
	if err != nil {
		return accounts, nil
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, _ := reader.ReadAll()
	for _, rec := range records {
		var acc Account
		acc.Name = rec[0]
		acc.Phone = rec[1]
		acc.Pin = rec[2]
		acc.Created = rec[3]
		accounts = append(accounts, acc)
	}
	return accounts, nil
}

func writeAccounts(fileName string, accounts []Account) {
	file, _ := os.Create(fileName)
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, acc := range accounts {
		writer.Write([]string{acc.Name, acc.Phone, acc.Pin, acc.Created})
	}
}

func writeTransaction(fileName, phone, pin string, amt int, tType string) {
	file, _ := os.OpenFile(fileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	writer.Write([]string{phone, pin, strconv.Itoa(amt), tType, time.Now().Format("2006-01-02 15:04:05")})
}

func accountExists(phone, pin string) bool {
	accounts, _ := readAccounts("accounts.csv")
	for _, acc := range accounts {
		if acc.Phone == phone && acc.Pin == pin {
			return true
		}
	}
	return false
}

func calculateBalance(phone string) int {
	file, err := os.Open("transactions.csv")
	if err != nil {
		return 0
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, _ := reader.ReadAll()

	balance := 0
	for _, rec := range records {
		if rec[0] == phone {
			amt, _ := strconv.Atoi(rec[2])
			if rec[3] == "Credit" {
				balance += amt
			} else if rec[3] == "Debit" {
				balance -= amt
			}
		}
	}
	return balance
}
