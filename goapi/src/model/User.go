package model

// email: user.email,
// name: user.name,
// hasSub: hasSub,
// expireDate: hasSub ? subscriptions?.data[0].current_period_end : null,
type User struct {
	Email       string `json:"email"`
	Name        string `json:"name"`
	HasSub      bool   `json:"hasSub"`
	ExpireDate  int64  `json:"expireDate"`
	Uuid        string `json:"uuid"`
	User_Secret string `json:"user_secret"`
}
