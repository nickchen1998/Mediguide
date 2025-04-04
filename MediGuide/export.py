import json


def combine_user_ai_messages(history):
    combined_history = []

    for i in range(0, len(history), 2):
        user_message = history[i]['content'] if i < len(history) and history[i]['role'] == "user" else ""
        ai_message = history[i + 1]['content'] if i + 1 < len(history) and history[i + 1]['role'] == "ai" else ""
        references = history[i + 1].get('references', []) if i + 1 < len(history) and history[i + 1][
            'role'] == "ai" else []

        combined_history.append({
            "user": user_message,
            "ai": ai_message,
            "references": references
        })

    return combined_history


def export_history_to_json(history):
    combined_history = combine_user_ai_messages(history)
    # 返回 JSON 格式字串
    return json.dumps(combined_history, ensure_ascii=False, indent=2)