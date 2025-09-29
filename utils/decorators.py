import os
from datetime import datetime

def capture_screenshot(driver, test_name):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshots_dir = os.path.join("reports", "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshots_dir, f"{test_name}_{timestamp}.png")
    
    try:
        driver.save_screenshot(screenshot_path)
        return screenshot_path
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        return None