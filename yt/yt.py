import yt_dlp
import pandas as pd
import subprocess
import os
import sys

# Global variable to control text UI
T_UI = 0  # Default value: use the print_in_box function
# List of required packages and their install commands
REQUIRED_PACKAGES = {
    'yt_dlp': 'pip install yt-dlp',
    'pandas': 'pip install pandas',
}

def check_dependencies():
    """Check if all required libraries are installed."""
    for package, install_command in REQUIRED_PACKAGES.items():
        try:
            __import__(package)
        except ImportError:
            dynamic_print(
                f"The required library '{package}' is not installed.\n"
                f"You can install it using: {install_command}\n"
                f"Would you like to install it now? (y/n)",
                is_prompt=True
            )
            user_input = input("> ").strip().lower()
            if user_input == 'y':
                dynamic_print(f"Installing {package}...")
                result = subprocess.run(install_command, shell=True)
                if result.returncode == 0:
                    dynamic_print(f"Successfully installed {package}.")
                else:
                    dynamic_print(f"Failed to install {package}. Exiting.")
                    sys.exit()
            else:
                dynamic_print(f"'{package}' is required. Exiting.")
                sys.exit()

# Example function placeholders


def print_in_box(fortune):
    """Print the given text inside a box."""
    fortune = fortune.replace("\t", "    ")
    lines = fortune.split("\n")
    max_length = max(len(line) for line in lines)
    print("*" * (max_length + 5))
    for line in lines:
        print(f"*  {line.ljust(max_length)} *")
    print("*" * (max_length + 5))

def dynamic_print(message, is_prompt=False):
    """Print dynamically based on T_UI value, and handle user input."""
    if T_UI:
        print_in_box(message)
    else:
        print(message)
    if is_prompt:
        user_input = input("> ")
        if user_input.lower() == "exit":
            dynamic_print("Exiting the application. Goodbye!")
            sys.exit()  # Terminate the program
        return user_input

def search_youtube(query, max_results=10, page=1):
    """Search YouTube and return a list of videos, paginated."""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }
    search_url = f"ytsearch{max_results * page}:{query}"  # Adjust search query for pagination
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(search_url, download=False)
        if result and 'entries' in result:
            start_index = (page - 1) * max_results
            end_index = start_index + max_results
            video_list = []
            for entry in result['entries'][start_index:end_index]:
                video_list.append({
                    'Title': entry['title'],
                    'URL': entry['url']
                })
            return video_list
        else:
            dynamic_print("No videos found.")
            return []

def play_videos(video_urls):
    """Play a list of videos sequentially using mpv."""
    for url in video_urls:
        subprocess.run(['mpv', '--no-video', url])

def toggle_tui():
    """Toggle the T_UI variable and persist the change to the script."""
    global T_UI
    choice = dynamic_print("Set T_UI to 1 (on) or 0 (off):", is_prompt=True)
    if choice in ('1', '0'):
        T_UI = int(choice)
        # Update the script to persist the change
        script_path = os.path.abspath(__file__)
        with open(script_path, 'r') as file:
            script_lines = file.readlines()
        for i, line in enumerate(script_lines):
            if line.startswith("T_UI ="):
                script_lines[i] = f"T_UI = {T_UI}  # Default value: use the print_in_box function\n"
        with open(script_path, 'w') as file:
            file.writelines(script_lines)
        dynamic_print(f"T_UI is now set to {T_UI}.")
    else:
        dynamic_print("Invalid input. T_UI not changed.")

def main():
    global T_UI
    check_dependencies()  # Check for required packages before running the 
    dynamic_print("All dependencies are satisfied. Running the app...")
    page = 1  # Start at the first page
    query = ""

    while True:
        # Prompt for a query if none exists
        if not query:
            query = dynamic_print("Type the query (or 'tui' to toggle UI):", is_prompt=True)
            if query.lower() == 'tui':
                toggle_tui()
                query = ""  # Reset query to re-prompt
                continue

        video_list = search_youtube(query, max_results=10, page=page)
        if video_list:
            df = pd.DataFrame(video_list)
            result_text = "\n".join(f"{i + 1}. {title}" for i, title in enumerate(df['Title']))
            dynamic_print(f"Search Results (Page {page}):\n{result_text}")
        else:
            dynamic_print("No videos found for this page.")
            query = ""  # Reset query to prompt for a new search
            continue

        selection = dynamic_print(
            "Enter the numbers of the videos to select (e.g., 1, 2, 5), 'n' for next page, or 'r' to redo search:",
            is_prompt=True
        )

        if selection.lower() == 'n':
            page += 1
            continue
        elif selection.lower() == 'r':
            page = 1
            query = ""  # Reset query to prompt for a new search
            continue
        
        try:
            numbers = list(map(int, selection.split(',')))
            selected_urls = [df.loc[n - 1, 'URL'] for n in numbers if 1 <= n <= len(df)]
            
            if selected_urls:
                play_videos(selected_urls)
            else:
                dynamic_print("Invalid numbers selected.")
        except ValueError:
            dynamic_print("Please enter valid numbers separated by commas.")

        # After playing videos, offer to search or replay
        replay = dynamic_print(
            "Would you like to see the list again or perform another search? (l: list, s: search, q: quit):",
            is_prompt=True
        )
        if replay.lower() == 'l':
            continue
        elif replay.lower() == 's':
            page = 1
            query = ""  # Reset query to prompt for a new search
        elif replay.lower() == 'q':
            dynamic_print("Goodbye!")
            break

if __name__ == "__main__":
    main()
