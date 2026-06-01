import asyncio
import getopt, sys
import httpx

args = sys.argv[1:]
options = "cr:u:"
long_options = ["concurrency", "requests=", "url="]

async def run_request(client, url, payload):
    # payload["run_config"] = {"missing_rate": missing_rate, "seed": seed}
    response = await client.post(url, json=payload)
    return response.json()

def get_cli_args():
    concurrency = False
    num_requests = 0
    url = "http://127.0.0.1:8000/predict"
    print("here")
    try:
        arguments, values = getopt.getopt(args, options, long_options)
        for currentArg, currentVal in arguments:
            if currentArg in ("-c", "--concurrency"):
                concurrency = True
            elif currentArg in ("-r", "--requests"):
                requests = int(currentVal)
            elif currentArg in ("-u", "--url"):
                url = currentVal
    except getopt.error as err:
        print(str(err))
    return concurrency, num_requests, url

async def concurrence(num_requests, url, payload):
    print("in concurrence")
    async with httpx.AsyncClient() as client:
        requests = [run_request(client, url, payload) for i in range(num_requests)]
        responses = await asyncio.gather(*requests)
    results = [response["decision"] for response in responses]
    return results

def main():
    payload = {'patient_weight': 37, 'fibroid_present': True, 'cycle_length_days': 32, 'symptom_duration_months': 13, 
    'pain_level': 6, 'age_group': '30-44', 'prior_pregnancy': True, 'num_fibroids': None, 'fibroid_volume_ratio': None, 'ferritin_proxy': None, 
    'flow_intensity': "heavy", 'treatment_type_hormonal': False, 'treatment_type_none': True, 'treatment_type_surgery': False, 'ethnicity_Asian': False, 
    'ethnicity_Black': False, 'ethnicity_Hispanic': True, 'ethnicity_Other': False, 'ethnicity_White': False}
    print("hi")
    concurrency, num_requests, url = get_cli_args()
    if concurrency:
        res = concurrence(num_requests, url, payload)
        print(res)

if __name__ == "__main__":
    main()