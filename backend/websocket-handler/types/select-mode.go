package types

type EMode string

const (
	Automatic     EMode = "automatic"
	SemiAutomatic EMode = "semi-automatic"
	Manual        EMode = "manual"
)

type SelectModeData struct {
	Mode EMode `json:"mode"`
}
