package main

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"time"
)

// Struct for account
type Account struct {
	Name   string
	Mobile string
	PIN    string
	Time   string
}

// Struct for transaction
type Transaction struct {
	Mobile string
	Amount int
	Time   string
	Type   string // "Credit" or "Debit"
}

// Save account to CSV
func (a Account) Save() error {
	file, err := os.OpenFile("account_opening.csv", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer file.Close()
	w := csv.NewWriter(file)
	defer w.Flush()
	return w.Write([]string{a.Name, a.Mobile, a.PIN, a.Time})
}

// Save transaction to CSV
func (t Transaction) Save() error {
	file, err := os.OpenFile("transaction_details.csv", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer file.Close()
	w := csv.NewWriter(file)
	defer w.Flush()
	return w.Write([]string{t.Mobile, strconv.Itoa(t.Amount), t.Time, t.Type})
}

// Check if account exists
func accountExists(mobile string) bool {
	file, err := os.Open("account_opening.csv")
	if err != nil {
		return false
	}
	defer file.Close()
	r := csv.NewReader(file)
	records, _ := r.ReadAll()
	for _, rec := range records {
		if rec[1] == mobile {
			return true
		}
	}
	return false
}

// Verify account with pin
func checkAccount(mobile, pin string) bool {
	file, err := os.Open("account_opening.csv")
	if err != nil {
		return false
	}
	defer file.Close()
	r := csv.NewReader(file)
	records, _ := r.ReadAll()
	for _, rec := range records {
		if rec[1] == mobile && rec[2] == pin {
			return true
		}
	}
	return false
}

// Calculate balance
func balance(mobile string) int {
	file, err := os.Open("transaction_details.csv")
	if err != nil {
		return 0
	}
	defer file.Close()
	r := csv.NewReader(file)
	records, _ := r.ReadAll()
	bal := 0
	for _, rec := range records {
		if rec[0] == mobile {
			amt, _ := strconv.Atoi(rec[1])
			if rec[3] == "Credit" {
				bal += amt
			} else {
				bal -= amt
			}
		}
	}
	return bal
}

func main() {
	for {
		fmt.Println("\n--- Banking System ---")
		fmt.Println("1. Open Account")
		fmt.Println("2. Add Money")
		fmt.Println("3. Withdraw Money")
		fmt.Println("4. Balance Check")
		fmt.Println("5. Statement")
		fmt.Println("6. Exit")

		var choice int
		fmt.Print("Enter choice: ")
		fmt.Scan(&choice)

		if choice == 1 {
			var name, mobile, pin string
			fmt.Print("Enter Name: ")
			fmt.Scan(&name)
			fmt.Print("Enter Mobile (10 digits): ")
			fmt.Scan(&mobile)

			if len(mobile) != 10 {
				fmt.Println("Invalid Mobile Number. Must be exactly 10 digits.")
				continue
			}
			if accountExists(mobile) {
				fmt.Println("Account already exists with this mobile number.")
				continue
			}

			fmt.Print("Set 4-digit PIN: ")
			fmt.Scan(&pin)
			if len(pin) != 4 {
				fmt.Println("Invalid PIN. Must be exactly 4 digits.")
				continue
			}

			now := time.Now().Format("2006-01-02 15:04:05")
			acc := Account{name, mobile, pin, now}
			if err := acc.Save(); err != nil {
				fmt.Println("Error:", err)
			} else {
				fmt.Println("Account Created Successfully")
			}

		} else if choice == 2 {
			var mobile, pin string
			var amt int
			fmt.Print("Enter Mobile: ")
			fmt.Scan(&mobile)
			fmt.Print("Enter PIN: ")
			fmt.Scan(&pin)

			if !checkAccount(mobile, pin) {
				fmt.Println("Invalid Mobile or PIN")
				continue
			}

			fmt.Print("Enter Amount to Add: ")
			fmt.Scan(&amt)
			if amt <= 0 {
				fmt.Println("Invalid Amount")
				continue
			}

			now := time.Now().Format("2006-01-02 15:04:05")
			tr := Transaction{mobile, amt, now, "Credit"}
			if err := tr.Save(); err != nil {
				fmt.Println("Error:", err)
			} else {
				fmt.Println("Amount Added Successfully")
			}

		} else if choice == 3 {
			var mobile, pin string
			var amt int
			fmt.Print("Enter Mobile: ")
			fmt.Scan(&mobile)
			fmt.Print("Enter PIN: ")
			fmt.Scan(&pin)

			if !checkAccount(mobile, pin) {
				fmt.Println("Invalid Mobile or PIN")
				continue
			}

			fmt.Print("Enter Amount to Withdraw: ")
			fmt.Scan(&amt)
			if amt <= 0 {
				fmt.Println("Invalid Amount")
				continue
			}

			bal := balance(mobile)
			if amt > bal {
				fmt.Println("Insufficient Balance")
				continue
			}

			now := time.Now().Format("2006-01-02 15:04:05")
			tr := Transaction{mobile, amt, now, "Debit"}
			if err := tr.Save(); err != nil {
				fmt.Println("Error:", err)
			} else {
				fmt.Println("Amount Withdrawn Successfully")
			}

		} else if choice == 4 {
			var mobile, pin string
			fmt.Print("Enter Mobile: ")
			fmt.Scan(&mobile)
			fmt.Print("Enter PIN: ")
			fmt.Scan(&pin)

			if !checkAccount(mobile, pin) {
				fmt.Println("Invalid Mobile or PIN")
				continue
			}
			fmt.Println("Available Balance:", balance(mobile))

		} else if choice == 5 {
			var mobile, pin string
			fmt.Print("Enter Mobile: ")
			fmt.Scan(&mobile)
			fmt.Print("Enter PIN: ")
			fmt.Scan(&pin)

			if !checkAccount(mobile, pin) {
				fmt.Println("Invalid Mobile or PIN")
				continue
			}

			file, err := os.Open("transaction_details.csv")
			if err != nil {
				fmt.Println("No Transactions Found")
				continue
			}
			defer file.Close()
			r := csv.NewReader(file)
			records, _ := r.ReadAll()

			fmt.Println("\n--- Statement ---")
			found := false
			for _, rec := range records {
				if rec[0] == mobile {
					fmt.Printf("Amount: %s | Time: %s | Type: %s\n", rec[1], rec[2], rec[3])
					found = true
				}
			}
			if !found {
				fmt.Println("No Transactions Found")
			}

		} else if choice == 6 {
			fmt.Println("Thank you for using our Banking System.")
			break
		} else {
			fmt.Println("Invalid Choice. Please Try Again.")
		}
	}
}
