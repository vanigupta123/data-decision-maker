import asyncio
async def run_trial(client, payload, missing_rate, seed):
    payload["run_config"] = {"missing_rate": missing_rate, "seed": seed}
    response = await client.post("http://127.0.0.1:8000/predict", json=payload)
    return response.json()

