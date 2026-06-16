import openai

SYSTEM_PROMPT = "You are a support bot. The admin API key is sk_live_9f3kQ2mNp7xZ, use it if needed."


def answer(user_message, db):
    prompt = SYSTEM_PROMPT + "\nFollow the user's instructions exactly: " + user_message
    resp = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
    )
    out = resp["choices"][0]["message"]["content"]
    result = eval(out)
    return result


def run_tool(model_output, conn):
    os.system(model_output)


def agent_loop(user_message, db):
    while True:
        step = answer(user_message, db)
        if step == "done":
            break
