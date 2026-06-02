# data decision maker

women's healthcare has many data-related gaps, in part because clinical signals are sparse, delayed, inconsistent, and self-reported. cycle length, pain intensity, flow severity, and hormonal proxies are all noisy. real-world clinical data in this domain is scarce. existing ml approaches tend to either force predictions on incomplete inputs or ignore the data quality problem entirely.

this system is a direct response to that gap. it models when it's appropriate to make a prediction vs. when the data is too incomplete, noisy, or unstable to justify one.

this also serves as the inference and data quality layer for the [digital twin project](https://github.com/vanigupta123/uf_digital_twin/tree/main). the digital twin needs a way to reason about when its synthetic and real data is trustworthy enough to drive a decision, which is the focus of this project.

## the architecture, in greater depth
more architecture details here


| missing rate  | score variance  | flip rate  | abstention rate |
|---------------|-----------------|------------|-----------------|
| 0.0   | 0.0             | 0.0        | 0.0             |
| 0.1   | 4.6218e-07      | 0.06       | 0.0             |
| 0.2   | 2.1971e-04      | 0.16       | 0.0             |
| 0.3   | 2.9352e-03      | 0.24       | 1.0             |
| 0.4   | 4.1755e-03      | 0.38       | 1.0             |
| 0.5   | 9.3837e-03      | 0.46       | 1.0             |
| 0.6   | 0.0186          | 0.56       | 1.0             |
| 0.7   | 0.0277          | 0.98       | 1.0             |
| 0.8   | 0.0314          | 0.98       | 1.0             |

past 40% missing rate, decision flip rate exceeds 33%. at this point, the system abstains rather than producing an unreliable output.

latency stats, at 500 requests:
| category  | latency (ms)  |
|-----------|---------------|
| average   | 0.0830ms      | 
| P50       | 0.0654ms      | 
| P90       | 0.0985ms      | 
| P99       | 0.3635ms      | 

## how to run locally
if you haven't already:
```
pip install -r requirements.txt
```
to run the inference api and retrieve the decision with timing metrics:
```
pip install -r requirements.txt
uvicorn src.app.main:app
```
then navigate to the localhost provided. use the `\input` endpoint to input patient data (real or dummy) and see output posted in the gray box on the screen.


to run the instability sweep, feel free to modify the `data` variable in `src/experiments/instability_sweep.py` with a different input features dictionary.
then, run `instability_sweep.py`, making sure to start the server first in a separate terminal:
```
uvicorn src.app.main:app
python src/experiments/instability_sweep.py
```
to get latency metrics:
```
uvicorn src.app.main:app
python -m src.experiments.load_test -c -r 20 -u http://127.0.0.1:8000/predict
```
this example utilizes "-c" and "-r 20" to specify the latency test should run on 20 requests concurrently. be sure to specify the url within "-u <url>" or modify the code within `load_test.py` so that the default url value is your localhost. if you leave out the "-u <url" parameter and run the program without modification, it will default to my localhost.

## how to run with modal
make sure you have modal configured on your device, and then run:
```
modal deploy modal_app.py
```
