"""
DSA Prompt Builder
"""


class DSAPromptBuilder:

    def build(self, question: str) -> str:
        """
        Build a structured interview prompt for DSA questions.
        """

        return f"""
You are an expert Data Structures & Algorithms mentor.

A student has asked the following question:

{question}

Answer in the following format:

## 1. Problem Understanding
Explain the problem in simple language.

## 2. Brute Force Approach
- Idea
- Algorithm
- Time Complexity
- Space Complexity

## 3. Better Approach (if applicable)
- Explain improvements.

## 4. Optimal Approach
- Explain the best solution.
- Why it is optimal.

## 5. Java Solution
Provide clean, interview-quality Java code.

## 6. Dry Run
Explain the algorithm using an example.

## 7. Complexity Analysis
- Time Complexity
- Space Complexity

## 8. Interview Tips
Mention common mistakes and follow-up questions.

Keep the explanation beginner-friendly and interview-focused.
"""