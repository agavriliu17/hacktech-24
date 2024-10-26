analyze_video_promp = """Analyze each screen capture thoroughly to explain the actions the user is taking in a detailed, step-by-step manner.

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