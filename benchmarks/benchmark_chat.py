import json
import time
import statistics
from typing import List

import httpx

GATEWAY_URL = "http://localhost:8000/chat"

PROMPT = "Explain vector databases in two sentences."


def percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    data_sorted = sorted(data)
    k = int((len(data_sorted) - 1) * p)
    return data_sorted[k]


def main():
    latencies = []
    total = 50
    start_all = time.time()
    for _ in range(total):
        payload = {"messages": [{"role": "user", "content": PROMPT}], "top_k": 4, "stream": False}
        t0 = time.time()
        r = httpx.post(GATEWAY_URL, json=payload, timeout=120)
        r.raise_for_status()
        latencies.append(time.time() - t0)
    total_time = time.time() - start_all
    p50 = percentile(latencies, 0.5)
    p95 = percentile(latencies, 0.95)
    qps = total / total_time

    result = {
        "requests": total,
        "p50_latency_s": p50,
        "p95_latency_s": p95,
        "qps": qps,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
