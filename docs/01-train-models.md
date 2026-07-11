# 01 — Train the models

> **Docker beginners:** skip ahead to nothing here — this step is plain Python, no Docker yet. That's intentional: training happens *before* Docker enters the picture. The container's only job is to *serve* an already-trained model, not train one.

Each model service has its own `train.py`. Running it produces the `.pkl` artifact(s) that the service's `app.py` loads at startup.

```bash
cd models/iris-service
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python train.py          # prints test accuracy, writes model.pkl
deactivate
cd ../..
```

Repeat for the other two services:

```bash
cd models/diabetes-service
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python train.py          # prints test MSE, writes model.pkl
deactivate
cd ../..

cd models/spam-service
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python train.py          # prints test accuracy, writes model.pkl + vectorizer.pkl
deactivate
cd ../..
```

After this step you should have:

```
models/iris-service/model.pkl
models/diabetes-service/model.pkl
models/spam-service/model.pkl
models/spam-service/vectorizer.pkl
```

**Why this split matters:** in a real project, training can take hours and needs GPUs, large datasets, experiment tracking. None of that belongs in the serving container. The container just needs the finished artifact — that's the whole reason `train.py` and `app.py` are separate files, and why the Dockerfile only `COPY`s the `.pkl`, never runs `train.py`.

Next: [02 — Build the images](02-build-images.md)
