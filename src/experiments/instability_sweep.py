import asyncio
import httpx
import numpy as np

data = {'patient_weight': 37, 'fibroid_present': True, 'cycle_length_days': 32, 'symptom_duration_months': 13, 
'pain_level': 6, 'age_group': '30-44', 'prior_pregnancy': True, 'num_fibroids': None, 'fibroid_volume_ratio': None, 'ferritin_proxy': None, 
'flow_intensity': "heavy", 'treatment_type_hormonal': False, 'treatment_type_none': True, 'treatment_type_surgery': False, 'ethnicity_Asian': False, 
'ethnicity_Black': False, 'ethnicity_Hispanic': True, 'ethnicity_Other': False, 'ethnicity_White': False}

async def run():
    with open('docs/results/instability.csv', 'w') as f:
        f.write("missing rate,score variance,flip rate,abstention rate\n")
    for missing_rate in np.arange(0.0, 0.9, 0.1):
        # run 50 trials with different seeds
        results = await run_sweep(data, missing_rate.item()) # should not gather and run this concurrently because uvicorn won't be able to and it will increase noise
        init_score = results[0]["score"]
        scores = []
        flip_count = 0 # how many times label changes vs trial 0
        abstention_count = 0
        for res in results:
            if res["score"] != init_score:
                flip_count += 1
            if res["abstained"]:
                abstention_count += 1
            scores.append(res["score"])
        score_variance = np.var(scores)
        with open('docs/results/instability.csv', 'a') as f:
            f.write(f"{missing_rate:.2f},{score_variance},{flip_count/50},{abstention_count/50}\n")
        print(f"at missing_rate={missing_rate:.2f}, flip_rate={flip_count/50} — above this threshold decisions are unjustifiable")

async def run_sweep(data, missing_rate):
    async with httpx.AsyncClient() as client:
        responses = [run_trial(client, data, missing_rate, i) for i in range(50)] # creates 50 corountine objects
        results = await asyncio.gather(*responses) # executes all corountines concurrently
    results = [result["decision"] for result in results]
    return results

async def run_trial(client, payload, missing_rate, seed):
    payload["run_config"] = {"missing_rate": missing_rate, "seed": seed}
    response = await client.post("http://127.0.0.1:8000/predict", json=payload)
    return response.json()

if __name__ == "__main__":
    asyncio.run(run())