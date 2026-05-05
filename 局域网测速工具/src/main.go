package main

import (
	"embed"
	"io/fs"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"netspeed/backend/handler"
	"netspeed/backend/loglib"
)

//go:embed frontend/dist/*
var frontendFS embed.FS

func getEnv(key, defaultVal string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultVal
}

func main() {
	logDir := getEnv("LOG_DIR", "logs")
	if err := loglib.Init(logDir); err != nil {
		log.Fatalf("Failed to init logger: %v", err)
	}
	defer loglib.Close()

	port := getEnv("PORT", "7777")

	loglib.Info("NetSpeed server starting on port %s", port)
	loglib.Info("Log directory: %s", logDir)

	wsHandler := handler.NewWSHandler()

	http.Handle("/ws", wsHandler)

	subFS, err := fs.Sub(frontendFS, "frontend/dist")
	if err != nil {
		log.Fatalf("Failed to get sub filesystem: %v", err)
	}
	fileServer := http.FileServer(http.FS(subFS))
	http.Handle("/", fileServer)

	addr := ":" + port
	loglib.Info("Listening on http://0.0.0.0%s", addr)
	loglib.Info("Open http://localhost%s in your browser", addr)
	loglib.Info("Server started at %s", time.Now().Format(time.RFC3339))

	if err := http.ListenAndServe(addr, nil); err != nil {
		loglib.Error("Server failed: %v", err)
	}
}

func init() {
	if p := os.Getenv("PORT"); p != "" {
		if _, err := strconv.Atoi(p); err != nil {
			log.Fatalf("Invalid PORT value: %s", p)
		}
	}
}
