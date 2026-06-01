import asyncio
import getopt, sys
import httpx
from ..utils.timer import timer

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
    try:
        arguments, values = getopt.getopt(args, options, long_options)
        for currentArg, currentVal in arguments:
            if currentArg in ("-c", "--concurrency"):
                concurrency = True
            elif currentArg in ("-r", "--requests"):
                num_requests = int(currentVal)
            elif currentArg in ("-u", "--url"):
                url = currentVal
    except getopt.error as err:
        print(str(err))
    return concurrency, num_requests, url

async def concurrence(num_requests, url, payload):
    async with httpx.AsyncClient() as client:
            requests = [run_request(client, url, payload) for i in range(num_requests)]
            responses = await asyncio.gather(*requests)
    decisions = [response["decision"] for response in responses]
    times = [response["timing_ms"]["total"] for response in responses]
    return decisions, times

async def main():
    payload = {'patient_weight': 37, 'fibroid_present': True, 'cycle_length_days': 32, 'symptom_duration_months': 13, 
    'pain_level': 6, 'age_group': '30-44', 'prior_pregnancy': True, 'num_fibroids': None, 'fibroid_volume_ratio': None, 'ferritin_proxy': None, 
    'flow_intensity': "heavy", 'treatment_type_hormonal': False, 'treatment_type_none': True, 'treatment_type_surgery': False, 'ethnicity_Asian': False, 
    'ethnicity_Black': False, 'ethnicity_Hispanic': True, 'ethnicity_Other': False, 'ethnicity_White': False}
    concurrency, num_requests, url = get_cli_args()
    if concurrency:
        with timer() as t:
            decisions, times = await concurrence(num_requests, url, payload)
            print(f"sent {num_requests} requests in {t.ms:.4f}ms")
        avg_latency = sum(times) / len(times) if times else 0
        p50 = percentiles(times, 50)
        p90 = percentiles(times, 90)
        p99 = percentiles(times, 99)
        print(f"avg_latency: {avg_latency:.4f}ms")
        print(f"p50: {p50:.4f}ms")
        print(f"p90: {p90:.4f}ms")
        print(f"p99: {p99:.4f}ms")


def percentiles(times, p):
    times.sort()
    if not times:
        return 0
    k = (len(times) - 1) * (p/100.0) # actual linear interpolation of percentile
    f = int(k) # floor of k
    c = min(f + 1, len(times) - 1) # ceil of k
    if f == c:
        return times[f]
    d0 = times[f] * (c - k)
    d1 = times[c] * (k - f)
    return d0 + d1

if __name__ == "__main__":
    asyncio.run(main())
    