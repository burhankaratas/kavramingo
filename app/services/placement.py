# Ön test sonucuna göre öğrencinin başlangıç yerini belirler


def determine_placement(user, test_results: list) -> dict:
    """
    test_results: [{"unite_id": 1, "is_correct": True}, ...]
    Dönüş: {"completed": [1, 2], "needs_work": [3], "locked": [4, 5]}
    """
    completed = []
    needs_work = []

    for result in test_results:
        if result["is_correct"]:
            completed.append(result["unite_id"])
        else:
            needs_work.append(result["unite_id"])

    return {
        "completed": completed,
        "needs_work": needs_work,
    }
