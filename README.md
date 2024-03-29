This is the classifier backend for https://github.com/LiteralGenie/jobber-site

## About

Skill labels are currently generated via regex. All other labels are generated with structured output from an LLM.

## Setup

Install dependencies
```sh
git clone git@github.com:LiteralGenie/jobber-classifier.git
cd ./jobber-classifier

python3 -m venv venv
. ./venv/bin/activate
python -m pip install -r requirements.txt
```

(optional) Configure llama-cpp-python to [use the GPU](https://github.com/abetlen/llama-cpp-python/issues/576#issuecomment-1766003289)
<br> Remember to also set `use_gpu = true` in the config file described in the next step.
```
CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 python -m pip install --force-reinstall --upgrade --no-cache-dir llama-cpp-python
```

Create a config file using the example template.
```
cp ./src/config/config_example.toml ./src/config/config.toml
nano ./src/config/config.toml
```

Add the skills / duties from the config to the SQLite database.
<br> (At least one skill and one duty need to be defined.)
```
python ./src/bin/apply_config.py
```

Populate the `posts` table [in the database](https://github.com/LiteralGenie/jobber-classifier/blob/master/src/db.py#L10) with job data (left as an exercise for the reader).
Or alternatively download a copy of the current Jobber database.
```
curl https://jobber.velchees.dev/api/export/sqlite
mv db.sqlite /path/in/config/db.sqlite
```

Generate labels for each post.
```
python ./src/bin/run_extract.py
```
