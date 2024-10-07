import pyautogui, subprocess, os


# Take a screenshot
screenshot = pyautogui.screenshot()

# Save the screenshot to a file
screenshot_path = os.path.join(os.path.dirname(__file__), '../figures/screenshot.png')
screenshot.save(screenshot_path)

commit_message = 'Add screenshot'
commands = [
    ['git', 'add', '.'],
    ['git', 'commit', '-m', commit_message],
    ['git', 'push'],
]


try:
    for command in commands:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f'An error occurred: {e.stderr}')



