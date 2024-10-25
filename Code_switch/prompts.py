def get_conversion_prompt(source_language, target_language, code):
    examples = [
        {
            "source": "Python",
            "target": "Java",
            "input": "def add(a, b):\n    return a + b",
            "output": "public class Main {\n    public static int add(int a, int b) {\n        return a + b;\n    }\n}",
        },
        {
            "source": "Java",
            "target": "Python",
            "input": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
            "output": "if __name__ == '__main__':\n    print(\"Hello, World!\")",
        },
        {
            "source": "C++",
            "target": "Python",
            "input": '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!";\n    return 0;\n}',
            "output": "if __name__ == '__main__':\n    print(\"Hello, World!\")",
        },
    ]

    prompt = "you are an excellent programming code writer. Convert the following {source_language} code to {target_language} accurately without any errors. Follow the code standards and convert the code with appropriate indentation as well and do not write any explanation. code:\n{code}\n\nHere are some examples of {source_language} to {target_language} code conversions:\n"

    for example in examples:
        if (
            example["source"] == source_language
            and example["target"] == target_language
        ):
            prompt += f"\nExample:\nSource ({source_language}):\n{example['input']}\n\nTarget ({target_language}):\n{example['output']}\n"

    prompt += f"\nNow, convert the following {source_language} code to {target_language}:\n{code}, and do not write any explanation"
    return prompt


def get_documentation_prompt(language, code):
    return f"""
Documentation:

Generate an explanation for the following {language} code, strictly adhering to the template described below.
Do not include sections like "Input," "Output," or "Example."

{code}
Strictly adhere to the below template:

Documentation:

**Code Name**: Provide a descriptive name for the code or function.

**Purpose**: Explain neatly what the entire code is about in 4-5 lines, explaining what the code does, including its main functionality.

**Variables**: List and describe the key variables used in the code.

**Functions**: List and explain each function present in the code.

Ensure that each section starts on a new line and that the output is formatted exactly as above.
"""
