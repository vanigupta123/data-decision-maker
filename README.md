# data decision maker

women's healthcare has many data-related gaps, in part because clinical signals are sparse, delayed, inconsistent, and self-reported. cycle length, pain intensity, flow severity, and hormonal proxies are all noisy. real-world clinical data in this domain is scarce. existing ml approaches tend to either force predictions on incomplete inputs or ignore the data quality problem entirely.

this system is a direct response to that gap. it models when it's appropriate to make a prediction vs. when the data is too incomplete, noisy, or unstable to justify one.

this also serves as the inference and data quality layer for the [digital twin project](https://github.com/vanigupta123/uf_digital_twin/tree/main). the digital twin needs a way to reason about when its synthetic and real data is trustworthy enough to drive a decision, which is the focus of this project.

## the architecture, in greater depth
\<tbd\>

## how to run locally
to run the inference api and retrieve the decision with timing metrics:
```
uvicorn src.app.main:app
```
then navigate to the localhost provided. use the `\input` endpoint to input patient data (real or dummy) and see output posted in the gray box on the screen.


to run the instability sweep, feel free to modify the `data` variable in `src/experiments/instability_sweep.py` with a different input features dictionary.
then, run `instability_sweep.py`, making sure to start the server first in a separate terminal:
```
uvicorn src.app.main:app
python src/experiments/instability_sweep.py
```
