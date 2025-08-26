package main

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"time"
)

type Account struct {
	Phone   string
	Balance int
}

func main() {
	for {
		fmt.Println("\n1. Open Account")
		fmt.Println("2. Credit")
		fmt.Println("3. Debit")
		fmt.Println("4. Exit")
		fmt.Print("Enter your choice: ")
		var choice int
		fmt.Scan(&choice)

		switch choice {
		case 1:
			openAccount()
		case 2:
			credit()
		case 3:
			debit()
		case 4:
			return
		default:
			fmt.Println("Invalid choice, try again.")
		}
	}
}

func openAccount() {
	fmt.Print("Enter phone number: ")
	var phone string
	fmt.Scan(&phone)

	accounts, _ := readAccounts("accounts.csv")
	for _, acc := range accounts {
		if acc.Phone == phone {
			fmt.Println("Account already exists for this number.")
			return
		}
	}

	newAcc := Account{Phone: phone, Balance: 0}
	accounts = append(accounts, newAcc)
	writeAccounts("accounts.csv", accounts)
	fmt.Println("Account created successfully.")
}

func credit() {
	fmt.Print("Enter phone number: ")
	var phone string
	fmt.Scan(&phone)

	fmt.Print("Enter amount to credit: ")
	var amt int
	fmt.Scan(&amt)

	accounts, _ := readAccounts("accounts.csv")
	found := false
	for i, acc := range accounts {
		if acc.Phone == phone {
			accounts[i].Balance += amt
			writeAccounts("accounts.csv", accounts)
			writeTransaction("transactions.csv", phone, amt, "Credit")
			fmt.Println("Amount credited successfully.")
			found = true
		}
	}
	if !found {
		fmt.Println("Account not found.")
	}
}

func debit() {
	fmt.Print("Enter phone number: ")
	var phone string
	fmt.Scan(&phone)

	fmt.Print("Enter amount to debit: ")
	var amt int
	fmt.Scan(&amt)

	accounts, _ := readAccounts("accounts.csv")
	found := false
	for i, acc := range accounts {
		if acc.Phone == phone {
			if amt > acc.Balance {
				fmt.Println("Error: Insufficient balance.")
				return
			}
			accounts[i].Balance -= amt
			writeAccounts("accounts.csv", accounts)
			writeTransaction("transactions.csv", phone, amt, "Debit")
			fmt.Println("Amount debited successfully.")
			found = true
		}
	}
	if !found {
		fmt.Println("Account not found.")
	}
}

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
		bal, _ := strconv.Atoi(rec[1])
		accounts = append(accounts, Account{Phone: rec[0], Balance: bal})
	}
	return accounts, nil
}

func writeAccounts(fileName string, accounts []Account) {
	file, _ := os.Create(fileName)
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, acc := range accounts {
		writer.Write([]string{acc.Phone, strconv.Itoa(acc.Balance)})
	}
}

func writeTransaction(fileName, phone string, amt int, tType string) {
	file, _ := os.OpenFile(fileName, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	writer.Write([]string{phone, strconv.Itoa(amt), time.Now().Format("2006-01-02 15:04:05"), tType})
}
