def handle_extract_audio():
    """Maneja la extracción de audio de videos"""
    print(f"\n{Colors.HEADER}Extract Audio from Video{Colors.ENDC}")
    mode = get_user_input("Process (s)ingle video or (b)atch directory?", "s")
    
    if mode.lower() == 's':
        input_path = get_user_input("Enter video path")
        output_path = get_user_input("Enter output audio path (optional)", "")
        
        # Opciones de audio
        format_audio = get_user_input("Audio format (mp3/wav/aac/flac/ogg)", "mp3")
        quality = get_user_input("Audio quality/bitrate", "192k")
        
        # Construir comando
        cmd = f"python {get_script_path('extract_audio.py')} single \"{input_path}\""
        if output_path:
            cmd += f" --output \"{output_path}\""
        cmd += f" --format {format_audio} --quality {quality}"
        
        # Opciones adicionales
        if get_yes_no("Customize sample rate?"):
            sample_rate = get_user_input("Sample rate (e.g., 44100, 48000)")
            cmd += f" --sample-rate {sample_rate}"
        
        if get_yes_no("Change channels?"):
            channels = get_user_input("Channels (1=mono, 2=stereo)", "2")
            cmd += f" --channels {channels}"
    else:
        input_dir = get_user_input("Enter directory path")
        output_dir = get_user_input("Enter output directory (optional)", "")
        
        # Opciones de audio
        format_audio = get_user_input("Audio format (mp3/wav/aac/flac/ogg)", "mp3")
        quality = get_user_input("Audio quality/bitrate", "192k")
        
        # Construir comando
        cmd = f"python {get_script_path('extract_audio.py')} batch \"{input_dir}\""
        if output_dir:
            cmd += f" --output-dir \"{output_dir}\""
        cmd += f" --format {format_audio} --quality {quality}"
    
    print(f"\n{Colors.CYAN}Executing: {cmd}{Colors.ENDC}")
    return run_command(cmd)

def handle_video_processing_pipeline():
    """Maneja el pipeline completo de procesamiento de video con audio"""
    print(f"\n{Colors.HEADER}Video Processing Pipeline (Audio + Frames + Background Removal){Colors.ENDC}")
    input_path = get_user_input("Enter video path")
    
    # Crear directorio base para el proyecto
    video_name = Path(input_path).stem
    project_dir = get_user_input("Project directory name", f"{video_name}_project")
    os.makedirs(project_dir, exist_ok=True)
    
    # Paso 1: Extraer audio
    print(f"\n{Colors.GREEN}Step 1: Extracting audio...{Colors.ENDC}")
    audio_format = get_user_input("Audio format (mp3/wav/aac/flac/ogg)", "mp3")
    audio_quality = get_user_input("Audio quality/bitrate", "192k")
    audio_output = f"{project_dir}/{video_name}_audio.{audio_format}"
    
    cmd1 = f"python {get_script_path('extract_audio.py')} single \"{input_path}\" --output \"{audio_output}\" --format {audio_format} --quality {audio_quality}"
    if run_command(cmd1) != 0:
        print(f"{Colors.FAIL}Error extracting audio{Colors.ENDC}")
        return 1
    
    # Paso 2: Extraer frames
    print(f"\n{Colors.GREEN}Step 2: Extracting frames...{Colors.ENDC}")
    frames_dir = f"{project_dir}/frames_original"
    frame_format = get_user_input("Frame format (png/webp)", "webp")
    
    fps_option = ""
    if get_yes_no("Extract at specific FPS?"):
        fps = get_user_input("FPS")
        fps_option = f" --fps {fps}"
    
    cmd2 = f"python {get_script_path('extract_frames.py')} \"{input_path}\" --output-dir \"{frames_dir}\" --format {frame_format}{fps_option}"
    if run_command(cmd2) != 0:
        print(f"{Colors.FAIL}Error extracting frames{Colors.ENDC}")
        return 1
    
    # Paso 3: Remover fondos
    print(f"\n{Colors.GREEN}Step 3: Removing backgrounds...{Colors.ENDC}")
    nobg_dir = f"{project_dir}/frames_nobg"
    model = get_user_input("Background removal model (u2net/u2netp/u2net_human_seg)", "u2net_human_seg")
    
    alpha_matting = ""
    if get_yes_no("Use alpha matting for better edges?"):
        alpha_matting = " --alpha-matting"
    
    cmd3 = f"python {get_script_path('nobg.py')} images \"{frames_dir}\" --output-dir \"{nobg_dir}\" --model {model} --format {frame_format}{alpha_matting}"
    if run_command(cmd3) != 0:
        print(f"{Colors.FAIL}Error removing backgrounds{Colors.ENDC}")
        return 1
    
    # Opcional: Aplicar efecto retro
    if get_yes_no("\nApply retro effect to frames?"):
        print(f"\n{Colors.GREEN}Step 4: Applying retro effect...{Colors.ENDC}")
        retro_dir = f"{project_dir}/frames_retro"
        colors = get_user_input("Number of colors", "16")
        pixel_size = get_user_input("Pixel size", "4")
        
        cmd4 = f"python {get_script_path('pyxelart.py')} batch \"{nobg_dir}\" --output-dir \"{retro_dir}\" --colors {colors} --pixel-size {pixel_size} --format {frame_format}"
        if run_command(cmd4) != 0:
            print(f"{Colors.FAIL}Error applying retro effect{Colors.ENDC}")
            return 1
        
        final_frames_dir = retro_dir
    else:
        final_frames_dir = nobg_dir
    
    # Resumen final
    print(f"\n{Colors.GREEN}Pipeline completed successfully!{Colors.ENDC}")
    print(f"\nProject structure:")
    print(f"  {project_dir}/")
    print(f"  ├── {video_name}_audio.{audio_format}")
    print(f"  ├── frames_original/")
    print(f"  ├── frames_nobg/")
    if get_yes_no("Apply retro effect to frames?"):
        print(f"  └── frames_retro/")
    
    print(f"\nAudio file: {audio_output}")
    print(f"Processed frames: {final_frames_dir}")
    
    # Limpieza opcional
    if get_yes_no("\nDelete original frames to save space?"):
        import shutil
        shutil.rmtree(frames_dir)
        print(f"Original frames deleted.")
    
    print(f"\n{Colors.CYAN}You can now use these assets in your game engine or video editor!{Colors.ENDC}")
    return 0#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
from pathlib import Path

# ANSI color codes para mejor visualización
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Imprime el banner principal"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║            Retro Media Processing Tools Suite v1.0            ║")
    print("║                                                               ║")
    print("║   Tools for creating retro-style images, videos and sprites   ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

def print_menu():
    """Imprime el menú principal"""
    print(f"{Colors.HEADER}Select an operation:{Colors.ENDC}")
    print(f"{Colors.BLUE}1.{Colors.ENDC} Apply retro effect to image(s)")
    print(f"{Colors.BLUE}2.{Colors.ENDC} Convert video to retro GIF")
    print(f"{Colors.BLUE}3.{Colors.ENDC} Apply retro effect to video (preserving audio)")
    print(f"{Colors.BLUE}4.{Colors.ENDC} Extract frames from video/GIF")
    print(f"{Colors.BLUE}5.{Colors.ENDC} Remove background from image(s)")
    print(f"{Colors.BLUE}6.{Colors.ENDC} Remove background from video frames")
    print(f"{Colors.BLUE}7.{Colors.ENDC} Extract audio from video")
    print(f"{Colors.BLUE}8.{Colors.ENDC} Complete pipeline (background removal + retro effect)")
    print(f"{Colors.BLUE}9.{Colors.ENDC} Video processing pipeline (audio + frames + background removal)")
    print(f"{Colors.BLUE}10.{Colors.ENDC} Show help for a specific tool")
    print(f"{Colors.BLUE}11.{Colors.ENDC} Exit")
    print()

def get_script_path(script_name):
    """Obtiene la ruta completa del script"""
    current_dir = Path(__file__).parent
    return current_dir / script_name

def run_command(command):
    """Ejecuta un comando y muestra su salida en tiempo real"""
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        # Mostrar salida en tiempo real
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        return process.returncode
    except Exception as e:
        print(f"{Colors.FAIL}Error executing command: {e}{Colors.ENDC}")
        return 1

def get_user_input(prompt, default=None):
    """Obtiene entrada del usuario con valor por defecto opcional"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def get_yes_no(prompt):
    """Obtiene una respuesta sí/no del usuario"""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please answer 'y' or 'n'")

def handle_retro_image():
    """Maneja la aplicación de efectos retro a imágenes"""
    print(f"\n{Colors.HEADER}Apply Retro Effect to Image(s){Colors.ENDC}")
    mode = get_user_input("Process (s)ingle image or (b)atch directory?", "s")
    
    if mode.lower() == 's':
        input_path = get_user_input("Enter image path")
        output_path = get_user_input("Enter output path (optional)", "")
        
        # Opciones comunes
        colors = get_user_input("Number of colors", "16")
        pixel_size = get_user_input("Pixel size", "4")
        format_output = get_user_input("Output format (png/jpg/webp)", "")
        quality = get_user_input("Quality (1-100)", "95")
        
        # Construir comando
        cmd = f"python {get_script_path('pyxelart.py')} single \"{input_path}\""
        if output_path:
            cmd += f" --output \"{output_path}\""
        cmd += f" --colors {colors} --pixel-size {pixel_size}"
        if format_output:
            cmd += f" --format {format_output}"
        cmd += f" --quality {quality}"
        
        # Opciones adicionales
        if get_yes_no("Add dialog box?"):
            cmd += " --dialog"
            text = get_user_input("Dialog text")
            cmd += f" --text \"{text}\""
        
        if get_yes_no("Change aspect ratio?"):
            aspect = get_user_input("Aspect ratio (4:3/1:1/original)", "original")
            cmd += f" --aspect-ratio {aspect}"
            if aspect != "original":
                method = get_user_input("Method (resize/crop)", "resize")
                cmd += f" --aspect-method {method}"
        
    else:
        input_dir = get_user_input("Enter directory path")
        output_dir = get_user_input("Enter output directory (optional)", "")
        
        # Opciones comunes
        colors = get_user_input("Number of colors", "16")
        pixel_size = get_user_input("Pixel size", "4")
        format_output = get_user_input("Output format (png/jpg/webp)", "")
        quality = get_user_input("Quality (1-100)", "95")
        
        # Construir comando
        cmd = f"python {get_script_path('pyxelart.py')} batch \"{input_dir}\""
        if output_dir:
            cmd += f" --output-dir \"{output_dir}\""
        cmd += f" --colors {colors} --pixel-size {pixel_size}"
        if format_output:
            cmd += f" --format {format_output}"
        cmd += f" --quality {quality}"
    
    print(f"\n{Colors.CYAN}Executing: {cmd}{Colors.ENDC}")
    return run_command(cmd)

def handle_video_to_gif():
    """Maneja la conversión de video a GIF retro"""
    print(f"\n{Colors.HEADER}Convert Video to Retro GIF{Colors.ENDC}")
    mode = get_user_input("Process (s)ingle video or (b)atch directory?", "s")
    
    if mode.lower() == 's':
        input_path = get_user_input("Enter video path")
        output_path = get_user_input("Enter output path (optional)", "")
        
        # Opciones comunes
        colors = get_user_input("Number of colors", "16")
        pixel_size = get_user_input("Pixel size", "4")
        frame_skip = get_user_input("Frame skip", "2")
        fps = get_user_input("Output FPS", "10")
        
        # Construir comando
        cmd = f"python {get_script_path('pyxelart_gif.py')} single \"{input_path}\""
        if output_path:
            cmd += f" --output \"{output_path}\""
        cmd += f" --colors {colors} --pixel-size {pixel_size} --frame-skip {frame_skip} --fps {fps}"
        
        # Opciones adicionales
        if get_yes_no("Change aspect ratio?"):
            aspect = get_user_input("Aspect ratio (4:3/1:1/original)", "original")
            cmd += f" --aspect-ratio {aspect}"
            if aspect != "original":
                method = get_user_input("Method (resize/crop)", "resize")
                cmd += f" --aspect-method {method}"
    else:
        input_dir = get_user_input("Enter directory path")
        output_dir = get_user_input("Enter output directory (optional)", "")
        
        # Opciones comunes
        colors = get_user_input("Number of colors", "16")
        pixel_size = get_user_input("Pixel size", "4")
        frame_skip = get_user_input("Frame skip", "2")
        fps = get_user_input("Output FPS", "10")
        
        # Construir comando
        cmd = f"python {get_script_path('pyxelart_gif.py')} batch \"{input_dir}\""
        if output_dir:
            cmd += f" --output-dir \"{output_dir}\""
        cmd += f" --colors {colors} --pixel-size {pixel_size} --frame-skip {frame_skip} --fps {fps}"
    
    print(f"\n{Colors.CYAN}Executing: {cmd}{Colors.ENDC}")
    return run_command(cmd)

def handle_retro_video():
    """Maneja la aplicación de efectos retro a videos"""
    print(f"\n{Colors.HEADER}Apply Retro Effect to Video{Colors.ENDC}")
    mode = get_user_input("Process (s)ingle video or (b)atch directory?", "s")
    
    if mode.lower() == 's':
        input_path = get_user_input("Enter video path")
        output_path = get_user_input("Enter output path (optional)", "")
        
        # Opciones comunes
        colors = get_user_input("Number of colors", "16")
        pixel_size = get_user_input("Pixel size", "4")
        format_output = get_user_input("Output format (.mp4/.avi/.mov/.mkv)", ".mp4")
        quality = get_user_input("Quality (1-51, lower is better)", "23")
        preset = get_user_input("Preset (ultrafast/fast/medium/slow/veryslow)", "medium")
        
        # Construir comando
        cmd = f"python {get_script_path('pyxelart_video.py')} single \"{input_path}\""
        if output_path:
            cmd += f" --output \"{output_path}\""
        cmd += f" --colors {colors} --pixel-size {pixel_size} --format {format_output}"
        cmd += f" --quality {quality} --preset {preset}"
        
        # Opciones adicionales
        if get_yes_no("Change aspect ratio?"):
            aspect = get_user_input("Aspect ratio (4:3/1:1/original)", "original")
            cmd += f" --aspect-ratio {aspect}"
            if aspect != "original":
                method = get_user_input("Method (resize/crop)", "resize")
                cmd += f" --aspect-method {method}"
    else:
        input_dir = get_user_input("Enter directory path")
        output_dir = get_user_input("Enter output directory (optional)", "")
        
        # Opciones comunes
        colors = get_user_input("Number of colors", "16")
        pixel_size = get_user_input("Pixel size", "4")
        format_output = get_user_input("Output format (.mp4/.avi/.mov/.mkv)", ".mp4")
        quality = get_user_input("Quality (1-51, lower is better)", "23")
        preset = get_user_input("Preset (ultrafast/fast/medium/slow/veryslow)", "medium")
        
        # Construir comando
        cmd = f"python {get_script_path('pyxelart_video.py')} batch \"{input_dir}\""
        if output_dir:
            cmd += f" --output-dir \"{output_dir}\""
        cmd += f" --colors {colors} --pixel-size {pixel_size} --format {format_output}"
        cmd += f" --quality {quality} --preset {preset}"
    
    print(f"\n{Colors.CYAN}Executing: {cmd}{Colors.ENDC}")
    return run_command(cmd)

def handle_extract_frames():
    """Maneja la extracción de frames"""
    print(f"\n{Colors.HEADER}Extract Frames from Video/GIF{Colors.ENDC}")
    input_path = get_user_input("Enter video/GIF path")
    output_dir = get_user_input("Enter output directory (optional)", "")
    
    # Opciones
    format_output = get_user_input("Output format (png/webp)", "webp")
    quality = get_user_input("Quality for WebP (1-100)", "80")
    
    # Construir comando
    cmd = f"python {get_script_path('extract_frames.py')} \"{input_path}\""
    if output_dir:
        cmd += f" --output-dir \"{output_dir}\""
    cmd += f" --format {format_output} --quality {quality}"
    
    # Opciones adicionales para video
    if input_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
        if get_yes_no("Extract at specific FPS?"):
            fps = get_user_input("FPS")
            cmd += f" --fps {fps}"
    
    if get_yes_no("Disable transparency preservation?"):
        cmd += " --no-alpha"
    
    print(f"\n{Colors.CYAN}Executing: {cmd}{Colors.ENDC}")
    return run_command(cmd)

def handle_remove_background():
    """Maneja la eliminación de fondos de imágenes"""
    print(f"\n{Colors.HEADER}Remove Background from Image(s){Colors.ENDC}")
    mode = get_user_input("Process (s)ingle image or (b)atch directory?", "s")
    
    if mode.lower() == 's':
        input_path = get_user_input("Enter image path")
        output_path = get_user_input("Enter output path (optional)", "")
        
        # Opciones
        model = get_user_input("Model (u2net/u2netp/u2net_human_seg/silueta)", "u2net_human_seg")
        format_output = get_user_input("Output format (png/webp/tiff)", "png")
        quality = get_user_input("Quality (1-100)", "95")
        
        # Construir comando
        cmd = f"python {get_script_path('nobg.py')} image \"{input_path}\""
        if output_path:
            cmd += f" --output \"{output_path}\""
        cmd += f" --model {model} --format {format_output} --quality {quality}"
        
        if get_yes_no("Use alpha matting for better edges?"):
            cmd += " --alpha-matting"
    else:
        input_dir = get_user_input("Enter directory path")
        output_dir = get_user_input("Enter output directory (optional)", "")
        
        # Opciones
        model = get_user_input("Model (u2net/u2netp/u2net_human_seg/silueta)", "u2net_human_seg")
        format_output = get_user_input("Output format (png/webp/tiff)", "png")
        quality = get_user_input("Quality (1-100)", "95")
        
        # Construir comando
        cmd = f"python {get_script_path('nobg.py')} images \"{input_dir}\""
        if output_dir:
            cmd += f" --output-dir \"{output_dir}\""
        cmd += f" --model {model} --format {format_output} --quality {quality}"
        
        if get_yes_no("Use alpha matting for better edges?"):
            cmd += " --alpha-matting"
    
    print(f"\n{Colors.CYAN}Executing: {cmd}{Colors.ENDC}")
    return run_command(cmd)

def handle_remove_background_video():
    """Maneja la eliminación de fondos de video"""
    print(f"\n{Colors.HEADER}Remove Background from Video{Colors.ENDC}")
    input_path = get_user_input("Enter video path")
    output_dir = get_user_input("Enter output directory (optional)", "")
    
    # Opciones
    model = get_user_input("Model (u2net/u2netp/u2net_human_seg/silueta)", "u2net_human_seg")
    format_output = get_user_input("Output format (png/webp/tiff)", "webp")
    quality = get_user_input("Quality (1-100)", "80")
    
    # Construir comando
    cmd = f"python {get_script_path('nobg_video.py')} \"{input_path}\""
    if output_dir:
        cmd += f" --output-dir \"{output_dir}\""
    cmd += f" --model {model} --format {format_output} --quality {quality}"
    
    if get_yes_no("Extract at specific FPS?"):
        fps = get_user_input("FPS")
        cmd += f" --fps {fps}"
    
    if get_yes_no("Use alpha matting for better edges?"):
        cmd += " --alpha-matting"
    
    if get_yes_no("Keep original frames?"):
        cmd += " --keep-frames"
    
    print(f"\n{Colors.CYAN}Executing: {cmd}{Colors.ENDC}")
    return run_command(cmd)

def handle_complete_pipeline():
    """Maneja el pipeline completo de procesamiento"""
    print(f"\n{Colors.HEADER}Complete Pipeline (Background Removal + Retro Effect){Colors.ENDC}")
    input_type = get_user_input("Process (i)mage or (v)ideo?", "i")
    
    if input_type.lower() == 'i':
        input_path = get_user_input("Enter image path")
        temp_dir = "temp_pipeline"
        
        # Paso 1: Remover fondo
        print(f"\n{Colors.GREEN}Step 1: Removing background...{Colors.ENDC}")
        nobg_output = f"{temp_dir}/nobg_{Path(input_path).name}"
        os.makedirs(temp_dir, exist_ok=True)
        
        cmd1 = f"python {get_script_path('nobg.py')} image \"{input_path}\" --output \"{nobg_output}\" --format webp"
        if run_command(cmd1) != 0:
            print(f"{Colors.FAIL}Error in background removal{Colors.ENDC}")
            return 1
        
        # Paso 2: Aplicar efecto retro
        print(f"\n{Colors.GREEN}Step 2: Applying retro effect...{Colors.ENDC}")
        colors = get_user_input("Number of colors", "16")
        pixel_size = get_user_input("Pixel size", "4")
        final_output = get_user_input("Final output path", f"output_retro_{Path(input_path).name}")
        
        cmd2 = f"python {get_script_path('pyxelart.py')} single \"{nobg_output}\" --output \"{final_output}\" --colors {colors} --pixel-size {pixel_size}"
        if run_command(cmd2) != 0:
            print(f"{Colors.FAIL}Error in retro effect{Colors.ENDC}")
            return 1
        
        # Limpiar archivos temporales
        import shutil
        shutil.rmtree(temp_dir)
        
        print(f"\n{Colors.GREEN}Pipeline completed successfully!{Colors.ENDC}")
    else:
        input_path = get_user_input("Enter video path")
        temp_dir = "temp_pipeline"
        
        # Paso 1: Remover fondo del video
        print(f"\n{Colors.GREEN}Step 1: Removing background from video...{Colors.ENDC}")
        nobg_dir = Path(input_path).stem + "_nobg"
        
        cmd1 = f"python {get_script_path('nobg_video.py')} \"{input_path}\" --output-dir \"{nobg_dir}\" --format webp"
        if run_command(cmd1) != 0:
            print(f"{Colors.FAIL}Error in background removal{Colors.ENDC}")
            return 1
        
        # Paso 2: Aplicar efecto retro a los frames
        print(f"\n{Colors.GREEN}Step 2: Applying retro effect to frames...{Colors.ENDC}")
        colors = get_user_input("Number of colors", "16")
        pixel_size = get_user_input("Pixel size", "4")
        
        frames_dir = f"{nobg_dir}/frames_nobg"
        retro_dir = f"{nobg_dir}/frames_retro"
        
        cmd2 = f"python {get_script_path('pyxelart.py')} batch \"{frames_dir}\" --output-dir \"{retro_dir}\" --colors {colors} --pixel-size {pixel_size}"
        if run_command(cmd2) != 0:
            print(f"{Colors.FAIL}Error in retro effect{Colors.ENDC}")
            return 1
        
        print(f"\n{Colors.GREEN}Pipeline completed successfully!{Colors.ENDC}")
        print(f"Processed frames are in: {retro_dir}")

def show_help():
    """Muestra ayuda para un script específico"""
    print(f"\n{Colors.HEADER}Show Help for a Tool{Colors.ENDC}")
    print("1. pyxelart.py (Retro image effects)")
    print("2. pyxelart_gif.py (Video to retro GIF)")
    print("3. pyxelart_video.py (Retro video effects)")
    print("4. extract_frames.py (Frame extraction)")
    print("5. nobg.py (Background removal for images)")
    print("6. nobg_video.py (Background removal for videos)")
    print("7. extract_audio.py (Audio extraction from videos)")
    
    choice = get_user_input("Select tool (1-7)")
    
    scripts = {
        "1": "pyxelart.py",
        "2": "pyxelart_gif.py",
        "3": "pyxelart_video.py",
        "4": "extract_frames.py",
        "5": "nobg.py",
        "6": "nobg_video.py",
        "7": "extract_audio.py"
    }
    
    if choice in scripts:
        cmd = f"python {get_script_path(scripts[choice])} --help"
        run_command(cmd)
    else:
        print(f"{Colors.FAIL}Invalid choice{Colors.ENDC}")

def main():
    """Función principal del CLI"""
    print_banner()
    
    while True:
        print_menu()
        choice = get_user_input("Enter your choice (1-11)")
        
        try:
            if choice == "1":
                handle_retro_image()
            elif choice == "2":
                handle_video_to_gif()
            elif choice == "3":
                handle_retro_video()
            elif choice == "4":
                handle_extract_frames()
            elif choice == "5":
                handle_remove_background()
            elif choice == "6":
                handle_remove_background_video()
            elif choice == "7":
                handle_extract_audio()
            elif choice == "8":
                handle_complete_pipeline()
            elif choice == "9":
                handle_video_processing_pipeline()
            elif choice == "10":
                show_help()
            elif choice == "11":
                print(f"\n{Colors.GREEN}Thank you for using Retro Media Processing Tools!{Colors.ENDC}")
                sys.exit(0)
            else:
                print(f"{Colors.FAIL}Invalid choice. Please try again.{Colors.ENDC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Operation cancelled by user{Colors.ENDC}")
            continue
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")
            continue
        
        print()
        if not get_yes_no("Do you want to perform another operation?"):
            print(f"\n{Colors.GREEN}Thank you for using Retro Media Processing Tools!{Colors.ENDC}")
            break

if __name__ == "__main__":
    main()