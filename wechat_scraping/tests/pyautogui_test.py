import pyautogui
import time
import os

# Path to the screenshot image file (template to match on the screen)
account = input("Please input account name: ")
account_fig_path = os.path.join(os.path.dirname(__file__), f'../figures/{account}.png')

try:
    # Locate the screenshot element on the screen
    location = pyautogui.locateOnScreen(account_fig_path)
    print(location)
    if location is not None:
        # Get the center coordinates of the located element
        center_x, center_y = pyautogui.center(location)
        
        # Move the mouse to the center of the located element
        pyautogui.moveTo(center_x, center_y, duration=0.5)  # duration adds a smooth movement effect
        print(f"Mouse moved to {center_x}, {center_y}")
    else:
        print("Element not found on the screen. Make sure the element is visible.")
except Exception as e:
    print(f"An error occurred: {e}")

