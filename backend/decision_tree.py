class DecisionNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, result=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.result = result

    def is_leaf(self):
        return self.result is not None


class AdaptiveDecisionTree:
    def __init__(self):
        self.root = self.build_tree()

    def build_tree(self):
        return DecisionNode(
            feature="attention",
            threshold=0.7,

            # if attention < 0.7 -> user seems less focused -> easy
            left=DecisionNode(result="easy"),

            # else continue checking performance
            right=DecisionNode(
                feature="correct_streak",
                threshold=2,

                # if correct_streak < 2 -> check wrong_streak
                left=DecisionNode(
                    feature="wrong_streak",
                    threshold=2,

                    # if wrong_streak < 2 -> medium
                    left=DecisionNode(result="medium"),

                    # if wrong_streak >= 2 -> easy
                    right=DecisionNode(result="easy"),
                ),

                # if correct_streak >= 2 -> hard
                right=DecisionNode(result="hard"),
            ),
        )

    def evaluate(self, state):
        node = self.root

        while not node.is_leaf():
            value = state.get(node.feature, 0)

            if value < node.threshold:
                node = node.left
            else:
                node = node.right

        return node.result