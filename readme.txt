package main

import (
	"fmt"
	"net/http"
)

// Struct for cookie data
type UserCookie struct {
	Name  string
	Value string
}

// 1. Set Cookie
func setCookie(w http.ResponseWriter, r *http.Request) {
	user := UserCookie{
		Name:  "username",
		Value: "MohammedAadil",
	}

	cookie := http.Cookie{
		Name:  user.Name,
		Value: user.Value,
	}

	http.SetCookie(w, &cookie)
	fmt.Fprintln(w, "Cookie set using struct!")
}

// 2. Get Cookie
func getCookie(w http.ResponseWriter, r *http.Request) {
	cookie, err := r.Cookie("username")
	if err != nil {
		fmt.Fprintln(w, "Cookie not found!")
		return
	}

	user := UserCookie{
		Name:  cookie.Name,
		Value: cookie.Value,
	}

	fmt.Fprintf(w, "Cookie from struct → Name: %s, Value: %s\n", user.Name, user.Value)
}

// 3. Delete Cookie
func deleteCookie(w http.ResponseWriter, r *http.Request) {
	user := UserCookie{
		Name:  "username",
		Value: "",
	}

	// To delete: just overwrite with empty value
	cookie := http.Cookie{
		Name:  user.Name,
		Value: user.Value,
	}

	http.SetCookie(w, &cookie)
	fmt.Fprintln(w, "Cookie deleted using struct!")
}

func main() {
	http.HandleFunc("/set", setCookie)
	http.HandleFunc("/get", getCookie)
	http.HandleFunc("/delete", deleteCookie)

	fmt.Println("Server started at http://localhost:8080")
	http.ListenAndServe(":8080", nil)
}
