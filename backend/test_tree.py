from decision_tree import AdaptiveDecisionTree

tree = AdaptiveDecisionTree()



test_cases = [
    # Original tests
    ("High performance → hard",
     {"score": 80, "correct_streak": 2, "wrong_streak": 0, "attention": 0.9},
     "hard"),

    ("Low performance → easy",
     {"score": 40, "correct_streak": 0, "wrong_streak": 2, "attention": 0.8},
     "easy"),

    ("Mixed performance → medium",
     {"score": 60, "correct_streak": 1, "wrong_streak": 0, "attention": 0.8},
     "medium"),

    ("Low attention overrides → easy",
     {"score": 90, "correct_streak": 3, "wrong_streak": 0, "attention": 0.2},
     "easy"),

    ("Exactly threshold (correct_streak = 2)",
     {"score": 70, "correct_streak": 2, "wrong_streak": 0, "attention": 0.9},
     "hard"),

    ("Exactly threshold (wrong_streak = 2)",
     {"score": 50, "correct_streak": 0, "wrong_streak": 2, "attention": 0.9},
     "easy"),

    ("Exactly attention threshold",
     {"score": 90, "correct_streak": 3, "wrong_streak": 0, "attention": 0.4},
     "hard"),

    ("All zeros",
     {"score": 0, "correct_streak": 0, "wrong_streak": 0, "attention": 0},
     "easy"),

    ("Perfect everything",
     {"score": 100, "correct_streak": 5, "wrong_streak": 0, "attention": 1.0},
     "hard"),

    ("Conflicting: good score but wrong streak high",
     {"score": 80, "correct_streak": 0, "wrong_streak": 3, "attention": 0.9},
     "easy"),

    ("Beginner improving",
     {"score": 30, "correct_streak": 2, "wrong_streak": 0, "attention": 0.8},
     "medium"),

    ("Struggling but focused",
     {"score": 40, "correct_streak": 0, "wrong_streak": 1, "attention": 0.9},
     "medium"),

    ("Distracted but performing well",
     {"score": 85, "correct_streak": 3, "wrong_streak": 0, "attention": 0.3},
     "easy"),

    # New stress tests
    ("Score just below hard threshold",
     {"score": 69, "correct_streak": 2, "wrong_streak": 0, "attention": 0.9},
     "medium"),

    ("Score exactly hard threshold but streak low",
     {"score": 70, "correct_streak": 1, "wrong_streak": 0, "attention": 0.9},
     "medium"),

    ("Score exactly easy threshold but wrong streak low",
     {"score": 50, "correct_streak": 0, "wrong_streak": 1, "attention": 0.9},
     "medium"),

    ("Score just below easy threshold",
     {"score": 49, "correct_streak": 0, "wrong_streak": 1, "attention": 0.9},
     "medium"),

    ("High score, good attention, no streak",
     {"score": 85, "correct_streak": 1, "wrong_streak": 0, "attention": 0.9},
     "medium"),

    ("Medium score, high correct streak",
     {"score": 65, "correct_streak": 3, "wrong_streak": 0, "attention": 0.9},
     "medium"),

    ("Low score, high wrong streak, low attention",
     {"score": 20, "correct_streak": 0, "wrong_streak": 4, "attention": 0.1},
     "easy"),

    ("Good score but attention barely above cutoff",
     {"score": 80, "correct_streak": 2, "wrong_streak": 0, "attention": 0.41},
     "hard"),

    ("Good score but attention barely below cutoff",
     {"score": 80, "correct_streak": 2, "wrong_streak": 0, "attention": 0.39},
     "easy"),

    ("Both streaks present",
     {"score": 60, "correct_streak": 2, "wrong_streak": 2, "attention": 0.9},
     "easy"),

    ("Very focused but very weak score",
     {"score": 10, "correct_streak": 0, "wrong_streak": 0, "attention": 1.0},
     "medium"),

    ("No attention data effect scenario",
     {"score": 75, "correct_streak": 2, "wrong_streak": 0, "attention": 0.5},
     "hard"),
]




print("=== Decision Tree Test Results ===\n")

for i, case in enumerate(test_cases, 1):
    result = tree.evaluate(case["input"])
    status = "PASS" if result == case["expected"] else "FAIL"

    print(f"Test {i}: {case['desc']}")
    print(f"Input: {case['input']}")
    print(f"Expected: {case['expected']} | Got: {result} → {status}\n")

print("=== End of Tests ===")