# Kicking the prompt testing tires

## Create and activate environment

Create:
```shell
mamba env create
```

Activate:
```shell
mamba activate prompt-testing-blog
```

## Run the app


```shell
python app.py hello
```

```shell
python app.py intro --name Bob  
```

## Run the tests

```shell
p9e run prompt_cases.py
```

```shell
p9e run prompt_cases.py --output report.yaml 
```