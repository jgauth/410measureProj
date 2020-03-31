Written using python 3.8, but should work with python >= 3.6.


Recommend using venv to run:
```bash
python3.8 -m venv env

source ./env/bin/activate

pip install -r requirements.txt

cd src

python demonstration.py
```

Files:

network_components.py - defines objects running simulation

baseline.py - baseline scenario
scrubbing.py - baseline scenario + scrubber
olad.py - scrubbing scenario + olad

demonstration.py - used in presentation, runs 4 scenarios and graphs results
