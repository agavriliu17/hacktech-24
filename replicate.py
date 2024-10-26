import os

import pyautogui
from anthropic import Anthropic
import base64
from PIL import Image, ImageGrab
import time
from typing import Dict, List, Tuple, Optional
import json
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
GRID_SIZE = 10
maxWidth = 1456
maxHeight = 819

screen_width, screen_height = pyautogui.size()

API_KEY = os.environ.get("ANTHROPIC_KEY")


@dataclass
class UIAction:
    coordinates: Tuple[int, int]
    confidence: float
    element_description: str
    action: str
    hover_duration: int
    hover_feedback_expected: str
    text_input: str


class AutomationSystem:
    def __init__(self, anthropic_api_key: str):
        self.client = Anthropic(api_key=anthropic_api_key)
        self.max_retries = 3
        pyautogui.PAUSE = 0.5  # Add small delay between actions

    def take_screenshot(self) -> Image.Image:
        """Capture the current screen."""
        screenshot = ImageGrab.grab()
        return screenshot

    def encode_image_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        import io
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def get_element_location(self, screenshot: Image.Image, element_description: str) -> Optional[UIAction]:
        """
        Use Claude 3.5 API to analyze screenshot and find precise element coordinates.
        Returns coordinates normalized to current screen resolution.
        """
        encoded_image = self.encode_image_base64(screenshot)
        system = f"""You are a computer vision system specialized in GUI automation.
        You need to find the EXACT location of an element to interact with.

        CRITICAL INSTRUCTIONS:
        1. Look at the screenshot very carefully
        2. Find the EXACT element that matches the action description
        3. For text elements, look for the exact text match
        4. For folders/files, ensure the name matches exactly
        5. For buttons/menus, ensure it's the exact UI element needed
        6. Provide coordinates at the CENTER of the element. PROVIDE THE EXACT COORDINATE.
        Use the entire screen for coordinates do not provide them relative to the open window
        7. For hover actions, ensure the coordinates are precise!
        8. If you're not 100% certain, set confidence below 0.7
        Opening a folder is a double click
        Return your response in this exact JSON format:
        DO NOT TYPE ANYTHING ELSE AS THE OUTPUT NEEDS TO BE PARSED AS A JSON
        {{
            "coordinates": [x, y],
            "action_type": "click/double_click/right_click/type/hover",
            "text_input": "text to type if needed",
            "hover_duration": number of seconds to hover (if hover action),
            "confidence": 0.0 to 1.0,
            "element_description": "Detailed description of what you found and why you're confident it's correct",
            "hover_feedback_expected": "Description of expected visual feedback during hover (tooltip, highlight, etc.)"
        }}"""
        message = self.client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1000,
            temperature=1,
            system=system,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Find the exact coordinates of this element: {element_description}"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encoded_image}}
                ]
            }]
        )
        print("HELO")
        print(message.content[0].text)
        result = json.loads(message.content[0].text)
        print(result)

        return UIAction(
            coordinates=(result["coordinates"][0], result["coordinates"][1]),
            confidence=result["confidence"],
            element_description=result["element_description"],
            action=result["action_type"],
            hover_duration=result["hover_duration"],
            hover_feedback_expected=result["hover_feedback_expected"],
            text_input=result["text_input"],
        )

    def verify_action(self, screenshot: Image.Image, expected_outcome: str) -> bool:
        """
        Verify if the action produced the expected outcome by analyzing the screenshot.
        """
        encoded_image = self.encode_image_base64(screenshot)

        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                system="You are a computer vision system that verifies UI states. Return ONLY 'true' or 'false'.",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text": f"Does this screenshot show the following outcome: {expected_outcome}?"},
                        {"type": "image",
                         "source": {"type": "base64", "media_type": "image/png", "data": encoded_image}}
                    ]
                }]
            )

            result = message.content[0].text.lower().strip()
            return result == "true"

        except Exception as e:
            logger.error(f"Error verifying action: {str(e)}")
            return False

    def perform_action(self, action_dict: Dict[str, str]) -> bool:
        """
        Perform a single action and verify its outcome.
        Returns True if action was successful, False otherwise.
        """
        for attempt in range(self.max_retries):
            # Take screenshot and get element location
            screenshot = self.take_screenshot()
            element = self.get_element_location(screenshot, action_dict)

            if not element or element.confidence < 0.8:
                logger.warning(f"Low confidence or no element found. Attempt {attempt + 1}/{self.max_retries}")
                continue

            # Scale coordinates to current screen resolution
            x = int(element.coordinates[0]) * (screen_width / maxWidth)
            y = int(element.coordinates[1]) * (screen_height / maxHeight)
            action = element.action
            expected = element.hover_feedback_expected

            # Perform the action based on action type
            if action == 'click':
                pyautogui.click(x, y)
            elif action == 'double_click':
                pyautogui.doubleClick(x, y)
            elif action == 'right_click':
                print(f"rightclick at {x, y}")
                pyautogui.rightClick(x, y)
            elif action == 'type':
                pyautogui.click(x, y)
                pyautogui.write(element.text_input)
                pyautogui.press('enter')
            elif action == 'hover':
                pyautogui.moveTo(x, y)

            # Verify the outcome
            time.sleep(0.05)  # Wait for UI to update
            verification_screenshot = self.take_screenshot()
            return True
            # TODO: verify
            # if self.verify_action(verification_screenshot, expected):
            #     logger.info(f"Action successful: {expected}")
            #     return True

            # logger.warning(f"Action verification failed. Attempt {attempt + 1}/{self.max_retries}")

        logger.error(f"Action failed after {self.max_retries} attempts: {action_dict}")
        return False

    def execute_steps(self, steps: List[Dict[str, str]]) -> bool:
        """
        Execute a sequence of steps.
        Returns True if all steps completed successfully, False otherwise.
        """
        for step in steps:
            if not self.perform_action(step):
                return False
        return True


# Example usage
if __name__ == "__main__":
    steps = [
        {
            "action": "Hover over the folder named 'Dataset'",
            "outcome": "Tooltip appears showing folder details"
        },
        {
            "action": "Double click to open the folder",
            "outcome": "Dataset folder opens showing 'cv' and 'job_descriptions' folders"
        },
        {
            "action": "Hover over 'job_descriptions' folder",
            "outcome": "Tooltip shows folder information"
        },
        {
            "action": "Double click to open the folder",
            "outcome": "job_descriptions folder opens"
        },
        {
            "action": "Right click inside the file explorer UI, away from any elements",
            "outcome": "Settings open"
        },
        {
            "action": "Hover over create new",
            "outcome": "A dialog opens"
        },
        {
            "action": "Click on 'Folder' next to create new",
            "outcome": "A dialog opens"
        },

        {"action": "Type aaaabbb",
         "outcome": "New folder appears"}
    ]
    automation = AutomationSystem(
        API_KEY)
    success = automation.execute_steps(steps)
    print(f"Automation {'completed successfully' if success else 'failed'}")
