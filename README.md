# Pesa Pulse – Customer Directory Analysis

Pesa Pulse, a Nairobi fintech start-up, has a new partner that shares its customer directory through an API. Before marketing plans regional campaigns, they want to know the basics: how many customers there are, where they are, and what the data looks like.

This project pulls the data from `https://jsonplaceholder.typicode.com/users`, explores its nested structure, extracts the key attributes, and answers "where are our customers?" first with plain Python structures (sets and dictionaries) and then with pandas. It finishes with charts that can go straight into a slide.

## Approach

1. **Fetch the data.** `get_customers` calls the API with `requests`, using a 10-second timeout. It checks the status code with `raise_for_status()` and parses the JSON into a list of dictionaries. If anything fails (no connection, timeout, bad status, invalid JSON, or an unexpected format) it prints a clear message and returns an empty list, so the script never shows a traceback.
2. **Explore the structure.** `explore` walks one customer record recursively and prints every key with its Python type, indented by depth.
3. **Extract attributes.** `extract_attributes` builds one flat dictionary per customer with 12 fields. Latitude and longitude are converted from strings to floats.
4. **Unique cities.** `unique_cities` collects the cities in a set, which automatically drops duplicates.
5. **Counting.** `city_counts` uses a loop and a dictionary. `email_domain_counts` uses a dictionary comprehension. Neither uses `collections.Counter` or pandas. `sort_counts` orders results from most to least common, with ties broken alphabetically.
6. **pandas.** `to_dataframe` turns the rows into a DataFrame. The script checks that pandas `value_counts()` gives the same answers as the hand-written counts.
7. **Export.** The results are saved as two CSV files, without the pandas index.
8. **Charts.** `plot_distribution` saves a titled bar chart with labelled axes and rotated labels. It is used for both the city and the email domain distributions.

## Project setup (uv)

The project is managed with [uv](https://docs.astral.sh/uv/). These are the steps used to create it:

```bash
mkdir pesa_pulse_customer_analysis
cd pesa_pulse_customer_analysis
uv init                                  # creates pyproject.toml, .python-version, main.py, README.md, .gitignore and a git repo
uv add requests pandas matplotlib        # installs the packages, creates .venv and uv.lock
mv main.py analysis.py                   # (Windows PowerShell: Rename-Item main.py analysis.py)
```

`pyproject.toml` records the dependencies, and `uv.lock` pins the exact versions so the environment can be rebuilt exactly. `.venv/` is listed in `.gitignore` and is not committed.

## How to run

```bash
git clone https://github.com/datawithian/pesa_pulse_customer_analysis
cd pesa_pulse_customer_analysis
uv sync                      # builds the environment from uv.lock
uv run python analysis.py    # runs the analysis
```

## Dependencies

This project does not use a `requirements.txt`. Its dependencies are declared in `pyproject.toml` and pinned to exact versions in `uv.lock`.

| Package | Used for |
|---|---|
| `requests` | Fetching the customer data from the API |
| `pandas` | Building the DataFrame, cross-checking counts and exporting CSVs |
| `matplotlib` | Drawing and saving the distribution charts |

To install them, run this from the project folder:

```bash
uv sync
```

This reads `pyproject.toml` and `uv.lock` and creates a `.venv` with the same package versions used to build the project. To add a package later, run `uv add <package>`, which updates both files.

The script needs an internet connection to reach the API. It creates an `output/` folder containing:

| File | Contents |
|---|---|
| `customers.csv` | One row per customer with the 12 extracted attributes |
| `city_counts.csv` | Customers per city, sorted by `customer_count` descending, then city |
| `customer_distribution.png` | Bar chart of customers by city |
| `email_domain_distribution.png` | Bar chart of customers by email domain |

## Nested structure

Each customer record looks like this (output of `explore(customers[0])`):

```
id: int
name: str
username: str
email: str
address: dict
  street: str
  suite: str
  city: str
  zipcode: str
  geo: dict
    lat: str
    lng: str
phone: str
website: str
company: dict
  name: str
  catchPhrase: str
  bs: str
```

- **Nested attributes:** `address` is a dictionary, and it contains another dictionary, `geo`. `company` is also a dictionary.
- **Deepest attribute:** latitude and longitude, three levels down: `customer["address"]["geo"]["lat"]` and `customer["address"]["geo"]["lng"]`.
- The API sends coordinates as text (`str`), so they are converted to numbers with `float()`.

## Findings

Console output from `uv run python analysis.py`:

```
10 unique cities for 10 customers
City counts: {'Aliyaview': 1, 'Bartholomebury': 1, 'Gwenborough': 1, 'Howemouth': 1, 'Lebsackbury': 1, 'McKenziehaven': 1, 'Roscoeview': 1, 'South Christy': 1, 'South Elvis': 1, 'Wisokyburgh': 1}
Email domain counts: {'biz': 3, 'ca': 1, 'info': 1, 'io': 1, 'me': 1, 'net': 1, 'org': 1, 'tv': 1}

DataFrame shape: (10, 12)
customer_id       int64
name                str
username            str
email               str
email_domain        str
phone               str
city                str
zipcode             str
latitude        float64
longitude       float64
company             str
website             str
dtype: object
City counts match pandas: True
Domain counts match pandas: True

=== Findings ===
Customers retrieved : 10
Unique cities       : 10
Most common city    : Aliyaview (1)
Email domains       : {'biz': 3, 'ca': 1, 'info': 1, 'io': 1, 'me': 1, 'net': 1, 'org': 1, 'tv': 1}
Chart saved to      : output/customer_distribution.png
```

### What this means

- **There are 10 customers, and each one is in a different city.** With 10 unique cities for 10 customers, no two customers share a city. Every city count is 1, so "most common city" is only a tie broken alphabetically (Aliyaview comes first).
- **What this tells marketing:** city-level campaigns would each reach just one customer, so the cities are too fine-grained for planning regional campaigns. Marketing would need a broader grouping, such as region or country, or more customers.
- **Email domains show a pattern.** `biz` is the most common, with 3 customers. The other seven domains (`ca`, `info`, `io`, `me`, `net`, `org`, `tv`) have one each.
- **The two ways of counting agree.** The hand-written dictionary counts match pandas `value_counts()` for both cities and domains, so the counts can be trusted.
- **The DataFrame has 10 rows and 12 columns.** Latitude and longitude are `float64`, and `customer_id` is `int64`. The text columns show as `str` because of the pandas version installed (older pandas versions show `object` for the same columns).

### Which chart is more useful?

The **email domain chart** is more useful. The city chart has ten bars of exactly the same height, so it shows no pattern and gives marketing nothing to act on. The email domain chart has real variation, with `biz` clearly taller than the rest, so it shows which category stands out.

## Assumptions

- The email domain is the part after the last dot in the address (for example `biz` from `Sincere@april.biz`), which is what the brief's examples (`biz`, `tv`) suggest. It is lowercased so that `BIZ` and `biz` would count together.
- When counts are tied, results are sorted alphabetically so the output is the same on every run.
- City names are used exactly as the API gives them, with no cleaning, because the values are already tidy.
- Zipcodes are stored as text because they contain hyphens and could have leading zeros.
- Every record has the fields the code expects (`address`, `geo`, `company`). That is true for this API, but a record with a missing field would raise a `KeyError`.
- The API is a public test dataset with placeholder data, so these findings show the method rather than real customer behaviour.

## Repository contents

```
analysis.py
README.md
pyproject.toml
uv.lock
.python-version
.gitignore
output/
  customers.csv
  city_counts.csv
  customer_distribution.png
  email_domain_distribution.png
```
