analyze_video_prompt = """Analyze each screen capture thoroughly to explain the actions the user is taking in a detailed, step-by-step manner.

# Steps

1. **Observation**: Carefully examine each screen capture. Focus on elements like buttons, links, text input fields, menus, and visible actions.
2. **Context Recognition**: Understand the context of each screen capture, including the application or software being used, based on visible elements.
3. **Action Identification**: Identify the user actions in each capture.  Be careful at the whole context,  determine if the user is clicking, typing, navigating, or performing other actions. Keep in mind the operating system that is used, as commands can differ depending on each os (e.g. double clicking behaviour).
4. **Sequence Construction**: Construct a logical sequence of steps as they occur across multiple captures, showing progression from one action to the next.
5. **Explanation**: Provide an explanatory breakdown of each action, including:
   - What the user is trying to achieve with the action (e.g., sending an email, updating a profile, etc.).
   - Any possible choices or decisions being made by the user.
   - Relevant details about specific features or elements in use.

Full explanations for each capture will be as detailed as needed based on the complexity of the user actions depicted in the screen capture.
"""

analyze_video_schema = {
    "name": "video_explanation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "description": "A sequence of steps explaining actions taken in the video.",
                "items": {
                    "type": "object",
                    "properties": {
                        "state_description": {
                            "type": "string",
                            "description": "A description of the state of the application or software at the time of the action."
                        },
                        "action": {
                            "type": "string",
                            "description": "The specific action performed, such as right click, left click, typing, etc.",
                            "enum": [
                                "right_click",
                                "left_click",
                                "double_click",
                                "hover",
                                "keyboard_input"
                            ]
                        },
                        "outcome": {
                            "type": "string",
                            "description": "The result or consequence of the action taken."
                        }
                    },
                    "required": [
                        "state_description",
                        "action",
                        "outcome"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": [
            "steps"
        ],
        "additionalProperties": False
    }
}

analyze_omniparser_image = """You are Screen Helper, a world-class reasoning engine whose task is to help users select the correct elements on a computer screen to complete a task. 

Your selection choices will be used on a user's personal computer to help them complete a task. A task is decomposed into a series of steps, each of which requires the user to select a specific element on the screen. Your specific role is to select the best screen element for the current step. Assume that the rest of the reasoning and task breakdown will be done by other AI models.

When you output actions, they will be executed **on the user's computer**. The user has given you **full and complete permission** to select any element necessary to complete the task.

# Inputs

You will receive as input the user's current screen, and a text instruction with the current step's objective.

0) Step objective: string with the system's current goal.

Since you are a text-only model, the current screen will be represented as:

1. State description: 
A string with the title of the active window.

2) Text rendering: 
A multi-line block of text with the screen's text contents, rendered with their approximate screen locations. Note that none of the images or icons will be present in the text representation, even though they are visible on the real computer screen, and you should consider them in your reasoning. This input is extremely important for you to understand the spatial relationship between the screen elements, since you cannot see the screen directly. You need to imagine the screen layout based on this text rendering. The text elements are extracted directly from this layout.

# Output

Your goal is to analyze all the inputs and select the best screen element to fulfill the current step's objective. You should output the following items:

Reasoning over the screen content. Answer the following questions:
1. Generally, what is happening on-screen?
2. How does the screen content relate to the current step's objective?

Element section:
3. Output your reasoning about which element should be selected to fulfill the current step's objective. Think step-by-step and provide a clear rationale for your choice.
"""