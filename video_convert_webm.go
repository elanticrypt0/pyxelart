package main

import (
	"errors"
	"flag"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"
)

// VideoInfo almacena información sobre un archivo de video
type VideoInfo struct {
	Width    int
	Height   int
	Duration float64
	HasAudio bool
}

// ConversionOptions almacena opciones para convertir un video
type ConversionOptions struct {
	Quality int
	Resize  string
	Crop    string
	Threads int
	Verbose bool
}

// ConversionStats almacena estadísticas de la conversión por lotes
type ConversionStats struct {
	Total int
	Exito int
	Error int
	mu    sync.Mutex
}

// Método para incrementar estadísticas de forma segura
func (stats *ConversionStats) incrementarExito() {
	stats.mu.Lock()
	defer stats.mu.Unlock()
	stats.Exito++
}

func (stats *ConversionStats) incrementarError() {
	stats.mu.Lock()
	defer stats.mu.Unlock()
	stats.Error++
}

// snakeCaseFilename convierte un nombre de archivo a snake_case
func snakeCaseFilename(filename string) string {
	base := filepath.Base(filename)
	ext := filepath.Ext(base)
	name := strings.TrimSuffix(base, ext)

	// Reemplazar caracteres no alfanuméricos con guiones bajos
	re := regexp.MustCompile(`[^a-zA-Z0-9]`)
	name = re.ReplaceAllString(name, "_")

	// Convertir camelCase a snake_case
	re = regexp.MustCompile(`([a-z0-9])([A-Z])`)
	name = re.ReplaceAllString(name, "${1}_${2}")

	// Convertir a minúsculas
	name = strings.ToLower(name)

	// Eliminar guiones bajos múltiples
	re = regexp.MustCompile(`_+`)
	name = re.ReplaceAllString(name, "_")

	// Eliminar guiones bajos al inicio o final
	name = strings.Trim(name, "_")

	return name
}

// getVideoInfo obtiene información del video usando ffprobe
func getVideoInfo(videoPath string) (*VideoInfo, error) {
	// Obtener dimensiones y duración
	cmd := exec.Command(
		"ffprobe", "-v", "error", "-select_streams", "v:0",
		"-show_entries", "stream=width,height,duration",
		"-of", "csv=p=0", videoPath,
	)

	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("error al ejecutar ffprobe: %w", err)
	}

	parts := strings.Split(strings.TrimSpace(string(output)), ",")
	if len(parts) < 3 {
		return nil, errors.New("la salida de ffprobe no contiene suficiente información")
	}

	width, err := strconv.Atoi(parts[0])
	if err != nil {
		return nil, fmt.Errorf("error al convertir ancho: %w", err)
	}

	height, err := strconv.Atoi(parts[1])
	if err != nil {
		return nil, fmt.Errorf("error al convertir alto: %w", err)
	}

	duration, err := strconv.ParseFloat(parts[2], 64)
	if err != nil {
		duration = 0
	}

	// Verificar si tiene audio
	cmdAudio := exec.Command(
		"ffprobe", "-v", "error", "-select_streams", "a",
		"-show_entries", "stream=codec_type", "-of", "csv=p=0",
		videoPath,
	)

	audioOutput, _ := cmdAudio.Output()
	hasAudio := len(strings.TrimSpace(string(audioOutput))) > 0

	return &VideoInfo{
		Width:    width,
		Height:   height,
		Duration: duration,
		HasAudio: hasAudio,
	}, nil
}

// convertToWebm convierte un video a formato WebM
func convertToWebm(inputVideo, outputPath string, opts ConversionOptions) error {
	// Verificar si el video existe
	if _, err := os.Stat(inputVideo); os.IsNotExist(err) {
		return fmt.Errorf("el archivo '%s' no existe", inputVideo)
	}

	// Obtener información del video
	videoInfo, err := getVideoInfo(inputVideo)
	if err != nil {
		return fmt.Errorf("error al obtener información del video: %w", err)
	}

	// Determinar ruta de salida
	if outputPath == "" {
		dir := filepath.Dir(inputVideo)
		filename := snakeCaseFilename(filepath.Base(inputVideo)) + ".webm"
		outputPath = filepath.Join(dir, filename)
	}

	// Preparar directorio de salida
	if err := os.MkdirAll(filepath.Dir(outputPath), 0755); err != nil {
		return fmt.Errorf("error al crear directorio de salida: %w", err)
	}

	// Convertir calidad (0-100) a bitrate aproximado (kbps)
	var bitrate int
	if opts.Quality < 30 {
		// Calidades muy bajas: 100-500 kbps
		bitrate = 100 + (400*opts.Quality)/30
	} else if opts.Quality < 70 {
		// Calidades medias: 500-2000 kbps
		bitrate = 500 + (1500*(opts.Quality-30))/40
	} else {
		// Calidades altas: 2000-6000 kbps
		bitrate = 2000 + (4000*(opts.Quality-70))/30
	}

	// Construir comando ffmpeg
	args := []string{"-y"}

	// Reducir verbosidad si no está en modo verbose
	if !opts.Verbose {
		args = append(args, "-v", "warning")
	}

	args = append(args, "-i", inputVideo)

	// Aplicar filtros si es necesario
	var filters []string

	// Filtro de recorte
	if opts.Crop != "" {
		parts := strings.Split(opts.Crop, ":")
		if len(parts) == 4 {
			x, y, w, h := parts[0], parts[1], parts[2], parts[3]
			filters = append(filters, fmt.Sprintf("crop=%s:%s:%s:%s", w, h, x, y))
		}
	}

	// Filtro de redimensionamiento
	if opts.Resize != "" {
		parts := strings.Split(opts.Resize, "x")
		if len(parts) == 2 {
			width, height := parts[0], parts[1]
			filters = append(filters, fmt.Sprintf("scale=%s:%s:force_original_aspect_ratio=decrease", width, height))
		}
	}

	// Agregar filtros al comando
	if len(filters) > 0 {
		args = append(args, "-vf", strings.Join(filters, ","))
	}

	// Configuración de codificación
	args = append(args,
		"-c:v", "libvpx-vp9",
		"-b:v", fmt.Sprintf("%dk", bitrate),
		"-deadline", "good",
		"-cpu-used", "4",
		"-pix_fmt", "yuv420p",
	)

	// Configurar número de hilos
	if opts.Threads > 0 {
		args = append(args, "-threads", strconv.Itoa(opts.Threads))
	}

	// Configuración de audio
	if videoInfo.HasAudio {
		args = append(args,
			"-c:a", "libopus",
			"-b:a", "96k",
		)
	}

	// Archivo de salida
	args = append(args, outputPath)

	// Mensaje inicial
	fmt.Printf("Convirtiendo: %s\n", filepath.Base(inputVideo))
	if opts.Verbose {
		fmt.Printf("Comando: ffmpeg %s\n", strings.Join(args, " "))
	}

	// Ejecutar comando
	cmd := exec.Command("ffmpeg", args...)
	if opts.Verbose {
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
	}

	if err := cmd.Run(); err != nil {
		return fmt.Errorf("error durante la conversión: %w", err)
	}

	// Verificar tamaños para comparación
	inputInfo, err := os.Stat(inputVideo)
	if err != nil {
		return fmt.Errorf("error al obtener tamaño del archivo original: %w", err)
	}

	outputInfo, err := os.Stat(outputPath)
	if err != nil {
		return fmt.Errorf("error al obtener tamaño del archivo convertido: %w", err)
	}

	inputSize := float64(inputInfo.Size()) / (1024 * 1024) // MB
	outputSize := float64(outputInfo.Size()) / (1024 * 1024) // MB
	ratio := (outputSize / inputSize) * 100

	// Mostrar información de tamaño
	fmt.Printf("✓ %s - %.2f MB (%.1f%% del original)\n", filepath.Base(outputPath), outputSize, ratio)

	return nil
}

// processDirectory procesa todos los videos en un directorio
func processDirectory(inputDir, outputDir string, opts ConversionOptions, recursive bool, maxWorkers int) (*ConversionStats, error) {
	// Verificar directorio de entrada
	if _, err := os.Stat(inputDir); os.IsNotExist(err) {
		return nil, fmt.Errorf("el directorio '%s' no existe", inputDir)
	}

	// Determinar directorio de salida
	if outputDir == "" {
		outputDir = filepath.Join(inputDir, "webm")
	}

	// Crear directorio de salida si no existe
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return nil, fmt.Errorf("error al crear directorio de salida: %w", err)
	}

	// Extensiones de video soportadas
	videoExtensions := map[string]bool{
		".mp4":  true,
		".avi":  true,
		".mov":  true,
		".mkv":  true,
		".flv":  true,
		".wmv":  true,
		".webm": true,
	}

	// Encontrar todos los videos
	var videos []string

	if recursive {
		// Buscar en subdirectorios
		err := filepath.Walk(inputDir, func(path string, info fs.FileInfo, err error) error {
			if err != nil {
				return err
			}
			if !info.IsDir() && videoExtensions[strings.ToLower(filepath.Ext(path))] {
				videos = append(videos, path)
			}
			return nil
		})
		if err != nil {
			return nil, fmt.Errorf("error al buscar videos: %w", err)
		}
	} else {
		// Buscar solo en el directorio principal
		entries, err := os.ReadDir(inputDir)
		if err != nil {
			return nil, fmt.Errorf("error al leer directorio: %w", err)
		}

		for _, entry := range entries {
			if !entry.IsDir() && videoExtensions[strings.ToLower(filepath.Ext(entry.Name()))] {
				videos = append(videos, filepath.Join(inputDir, entry.Name()))
			}
		}
	}

	if len(videos) == 0 {
		fmt.Printf("No se encontraron videos en '%s'\n", inputDir)
		return &ConversionStats{}, nil
	}

	fmt.Printf("Encontrados %d videos para procesar\n", len(videos))

	stats := &ConversionStats{
		Total: len(videos),
	}

	// Preparar canal de trabajo
	type workItem struct {
		videoPath string
		index     int
	}

	workChan := make(chan workItem, len(videos))
	for i, video := range videos {
		workChan <- workItem{video, i}
	}
	close(workChan)

	var wg sync.WaitGroup
	numWorkers := maxWorkers
	if numWorkers <= 0 {
		numWorkers = 1
	}
	if numWorkers > len(videos) {
		numWorkers = len(videos)
	}

	// Función para procesar un video
	processVideo := func(item workItem) bool {
		videoPath := item.videoPath
		relPath, err := filepath.Rel(inputDir, videoPath)
		if err != nil {
			relPath = filepath.Base(videoPath)
		}

		outputSubdir := filepath.Dir(relPath)
		fullOutputDir := filepath.Join(outputDir, outputSubdir)

		// Asegurar que existe el subdirectorio de salida
		if err := os.MkdirAll(fullOutputDir, 0755); err != nil {
			fmt.Printf("Error al crear subdirectorio: %s\n", err)
			return false
		}

		outputFile := filepath.Join(
			fullOutputDir,
			snakeCaseFilename(filepath.Base(videoPath))+".webm",
		)

		// Comprobar si el archivo ya existe y es más reciente que el original
		if info, err := os.Stat(outputFile); err == nil {
			inputInfo, err := os.Stat(videoPath)
			if err == nil {
				if info.ModTime().After(inputInfo.ModTime()) {
					fmt.Printf("Omitiendo %s - ya procesado\n", filepath.Base(videoPath))
					return true
				}
			}
		}

		// Convertir video
		err = convertToWebm(videoPath, outputFile, opts)
		if err != nil {
			fmt.Printf("Error al convertir %s: %s\n", filepath.Base(videoPath), err)
			return false
		}

		return true
	}

	// Iniciar trabajadores
	if numWorkers <= 1 {
		// Modo secuencial
		for item := range workChan {
			success := processVideo(item)
			if success {
				stats.Exito++
			} else {
				stats.Error++
			}
		}
	} else {
		// Modo paralelo
		wg.Add(numWorkers)
		for i := 0; i < numWorkers; i++ {
			go func() {
				defer wg.Done()
				for item := range workChan {
					success := processVideo(item)
					if success {
						stats.incrementarExito()
					} else {
						stats.incrementarError()
					}
				}
			}()
		}
		wg.Wait()
	}

	// Mostrar estadísticas
	fmt.Printf("\nProceso completado:\n")
	fmt.Printf("- Total procesados: %d\n", stats.Total)
	fmt.Printf("- Conversiones exitosas: %d\n", stats.Exito)
	fmt.Printf("- Errores: %d\n", stats.Error)

	return stats, nil
}

func main() {
	// Definir comandos
	fileCmd := flag.NewFlagSet("file", flag.ExitOnError)
	dirCmd := flag.NewFlagSet("dir", flag.ExitOnError)

	// Variables comunes
	var quality int
	var resize, crop string
	var verbose bool

	// Variables para comando 'file'
	fileInput := fileCmd.String("input", "", "Archivo de video de entrada")
	fileOutput := fileCmd.String("output", "", "Ruta de salida (opcional)")
	fileCmd.IntVar(&quality, "quality", 30, "Calidad del video (0-100)")
	fileCmd.StringVar(&resize, "resize", "", "Redimensionar video (formato: widthxheight)")
	fileCmd.StringVar(&crop, "crop", "", "Recortar video (formato: x:y:width:height)")
	fileCmd.BoolVar(&verbose, "verbose", false, "Mostrar información detallada")
	fileCmd.BoolVar(&verbose, "v", false, "Mostrar información detallada (forma corta)")

	// Variables para comando 'dir'
	dirInput := dirCmd.String("input", "", "Directorio de entrada")
	dirOutput := dirCmd.String("output", "", "Directorio de salida (opcional)")
	dirCmd.IntVar(&quality, "quality", 30, "Calidad del video (0-100)")
	dirCmd.StringVar(&resize, "resize", "", "Redimensionar video (formato: widthxheight)")
	dirCmd.StringVar(&crop, "crop", "", "Recortar video (formato: x:y:width:height)")
	recursive := dirCmd.Bool("recursive", false, "Buscar videos en subdirectorios")
	workers := dirCmd.Int("workers", 1, "Número máximo de trabajos en paralelo")
	dirCmd.BoolVar(&verbose, "verbose", false, "Mostrar información detallada")
	dirCmd.BoolVar(&verbose, "v", false, "Mostrar información detallada (forma corta)")

	// Verificar si hay argumentos
	if len(os.Args) < 2 {
		fmt.Println("Se requiere un subcomando: 'file' o 'dir'")
		fmt.Println("Uso:")
		fmt.Println("  webm_converter file -input <archivo> [opciones]")
		fmt.Println("  webm_converter dir -input <directorio> [opciones]")
		os.Exit(1)
	}

	// Mostrar banner
	fmt.Println("╔═══════════════════════════════════════╗")
	fmt.Println("║          WebM Converter v1.0          ║")
	fmt.Println("╚═══════════════════════════════════════╝")

	// Analizar argumentos según el subcomando
	switch os.Args[1] {
	case "file":
		fileCmd.Parse(os.Args[2:])
		if *fileInput == "" {
			fmt.Println("Error: Se requiere especificar un archivo de entrada")
			fileCmd.PrintDefaults()
			os.Exit(1)
		}

		// Validar argumentos
		if quality < 0 || quality > 100 {
			fmt.Println("Error: La calidad debe estar entre 0 y 100")
			os.Exit(1)
		}

		// Configurar opciones
		opts := ConversionOptions{
			Quality: quality,
			Resize:  resize,
			Crop:    crop,
			Verbose: verbose,
		}

		// Convertir archivo
		start := time.Now()
		err := convertToWebm(*fileInput, *fileOutput, opts)
		if err != nil {
			fmt.Printf("Error: %s\n", err)
			os.Exit(1)
		}
		elapsed := time.Since(start)
		fmt.Printf("Tiempo de conversión: %.2f segundos\n", elapsed.Seconds())

	case "dir":
		dirCmd.Parse(os.Args[2:])
		if *dirInput == "" {
			fmt.Println("Error: Se requiere especificar un directorio de entrada")
			dirCmd.PrintDefaults()
			os.Exit(1)
		}

		// Validar argumentos
		if quality < 0 || quality > 100 {
			fmt.Println("Error: La calidad debe estar entre 0 y 100")
			os.Exit(1)
		}

		// Configurar opciones
		opts := ConversionOptions{
			Quality: quality,
			Resize:  resize,
			Crop:    crop,
			Verbose: verbose,
		}

		// Procesar directorio
		start := time.Now()
		_, err := processDirectory(*dirInput, *dirOutput, opts, *recursive, *workers)
		if err != nil {
			fmt.Printf("Error: %s\n", err)
			os.Exit(1)
		}
		elapsed := time.Since(start)
		fmt.Printf("Tiempo total: %.2f segundos\n", elapsed.Seconds())

	default:
		fmt.Printf("Comando desconocido: %s\n", os.Args[1])
		fmt.Println("Use 'file' o 'dir'")
		os.Exit(1)
	}
}