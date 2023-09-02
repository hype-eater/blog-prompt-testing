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
p9e run prompt_cases.py --key intro-kitty
```

```shell
p9e run prompt_cases.py --output report.yaml 
```

## View reports

```
$ p9e report report.yaml       
# Reading report @ report.yaml
+--------+--------+
| weight |   2.00 |
| score  |   2.00 |
| perc   | 100.00 |
+--------+--------+
+------------+----------+---------+--------+
| category   |   weight |   score |   perc |
|------------+----------+---------+--------|
| greeting   |        1 |    1.00 | 100.00 |
| intro      |        1 |    1.00 | 100.00 |
+------------+----------+---------+--------+
```

Grouped results:
```
$ p9e report report.yaml --groupby key
# Reading report @ report.yaml
+--------+--------+
| weight |   2.00 |
| score  |   2.00 |
| perc   | 100.00 |
+--------+--------+
+-------------+----------+---------+--------+
| key         |   weight |   score |   perc |
|-------------+----------+---------+--------|
| greeting    |        1 |    1.00 | 100.00 |
| intro-kitty |        1 |    1.00 | 100.00 |
+-------------+----------+---------+--------+
```

```
$ p9e report report.yaml --groupby prompt
# Reading report @ report.yaml
+--------+--------+
| weight |   2.00 |
| score  |   2.00 |
| perc   | 100.00 |
+--------+--------+
+--------------------------+----------+---------+--------+
| prompt                   |   weight |   score |   perc |
|--------------------------+----------+---------+--------|
| A greeting:              |        1 |    1.00 | 100.00 |
| Hello, my name is Kitty. |        1 |    1.00 | 100.00 |
+--------------------------+----------+---------+--------+
```