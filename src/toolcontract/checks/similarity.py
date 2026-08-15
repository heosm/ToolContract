import re


def tokenize(text):
    return set(
        re.findall(r"[가-힣A-Za-z0-9_]+", text.lower())
    )


def calculate_similarity(text1, text2):
    words1 = tokenize(text1)
    words2 = tokenize(text2)

    if not words1 or not words2:
        return 0.0

    common = words1 & words2
    total = words1 | words2

    return len(common) / len(total)


def check_similarity(tools):
    errors = []

    for i in range(len(tools)):
        for j in range(i + 1, len(tools)):
            tool1 = tools[i]
            tool2 = tools[j]

            name1 = tool1.get("name", "unknown")
            name2 = tool2.get("name", "unknown")

            desc1 = tool1.get("description", "")
            desc2 = tool2.get("description", "")

            score = calculate_similarity(desc1, desc2)

            if score >= 0.6:
                errors.append(
                    f"⚠️[TC301] [{name1} ↔ {name2}] "
                    f"두 Tool의 description이 너무 유사합니다. "
                    f"(유사도: {score:.2f})"
                )

    return errors