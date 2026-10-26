"""
Day 1 - API Data Analysis Using Python Structures
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"


def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, list):
            print("Unexpected response format: expected a list of customers.")
            return []
        return data

    except ValueError as exc:  
        print(f"Failed to decode the API response: {exc}")
        return []

    except requests.RequestException as exc:  
        print(f"Failed to retrieve customers: {exc}")
        return []


def explore(record: dict, indent: int = 0) -> None:
    """Print every key in a (possibly nested) record with its type, indented by depth."""
    for key, value in record.items():
        print(" " * indent + f"{key}: {type(value).__name__}")

        if isinstance(value, dict):
            explore(value, indent + 2)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):  
                    explore(item, indent + 2)



def extract_attributes(customers: list[dict]) -> list[dict]:
    
    rows = []

    for customer in customers:
        email = customer["email"]

        row = {
            "customer_id": customer["id"],
            "name": customer["name"],
            "username": customer["username"],
            "email": email,
            "email_domain": email.split(".")[-1].lower(),
            "phone": customer["phone"],
            "city": customer["address"]["city"],
            "zipcode": customer["address"]["zipcode"],
            "latitude": float(customer["address"]["geo"]["lat"]),
            "longitude": float(customer["address"]["geo"]["lng"]),
            "company": customer["company"]["name"],
            "website": customer["website"],
        }

        rows.append(row)

    return rows



def unique_cities(customers: list[dict]) -> set[str]:
    cities = set()

    for customer in customers:
        city = customer["address"]["city"]
        cities.add(city)

    return cities



def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city using a loop and dictionary."""

    counts = {}

    for customer in customers:
        city = customer["address"]["city"]

        if city in counts:
            counts[city] += 1
        else:
            counts[city] = 1

    return counts

def sort_counts(counts: dict[str, int]) -> dict[str, int]:
    """Sort by count (highest first), then alphabetically for ties."""
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per email top-level domain, sorted from most to least common."""
    domains = [
        customer["email"].rsplit(".", 1)[-1].lower()
        for customer in customers
    ]

    counts = {
        domain: domains.count(domain)
        for domain in set(domains)
    }

    return sort_counts(counts)


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)



def plot_distribution(
    counts: dict[str, int],
    path: Path,
    title: str = "Customer Distribution",
    xlabel: str = "Category",
) -> None:
    """Plot a labelled bar chart and save it to the specified path."""
    path.parent.mkdir(parents=True, exist_ok=True)

    ordered = sort_counts(counts)

    plt.figure(figsize=(10, 6))
    plt.bar(list(ordered.keys()), list(ordered.values()))

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Number of Customers")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(range(0, max(ordered.values()) + 1))

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


if __name__ == "__main__":
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # 1. Fetch the data (stop cleanly if it failed)
    customers = get_customers()
    if not customers:
        raise SystemExit("No customer data retrieved; stopping.")

    # 2. Explore the structure of one record
    print("Structure of one customer record:")
    explore(customers[0])
    print()

    # 3. Extract flat attributes
    rows = extract_attributes(customers)

    # 4. Unique cities
    cities = unique_cities(customers)
    print(f"{len(cities)} unique cities for {len(customers)} customers")

    # 5. Counts, sorted from most to least common
    by_city = sort_counts(city_counts(customers))
    by_domain = email_domain_counts(customers)  
    print("City counts:", by_city)
    print("Email domain counts:", by_domain)
    print()

    # 6. DataFrame and cross-check against the hand-written counts
    df = to_dataframe(rows)
    print("DataFrame shape:", df.shape)
    print(df.dtypes)

    pandas_cities = df["city"].value_counts().to_dict()
    pandas_domains = df["email_domain"].value_counts().to_dict()
    print("City counts match pandas:", pandas_cities == by_city)
    print("Domain counts match pandas:", pandas_domains == by_domain)
    print()

    # 7. Export CSVs (no index)
    df.to_csv(output_dir / "customers.csv", index=False)

    city_df = pd.DataFrame(list(by_city.items()), columns=["city", "customer_count"])
    city_df = city_df.sort_values(["customer_count", "city"], ascending=[False, True])
    city_df.to_csv(output_dir / "city_counts.csv", index=False)

    # 8. Charts
    plot_distribution(
        by_city,
        output_dir / "customer_distribution.png",
        title="Customers by City",
        xlabel="City",
    )
    plot_distribution(
        by_domain,
        output_dir / "email_domain_distribution.png",
        title="Customers by Email Domain",
        xlabel="Email Domain",
    )

    # Findings summary (format from the brief)
    top_city, top_count = next(iter(by_city.items()))
    print("=== Findings ===")
    print(f"Customers retrieved : {len(customers)}")
    print(f"Unique cities       : {len(cities)}")
    print(f"Most common city    : {top_city} ({top_count})")
    print(f"Email domains       : {by_domain}")
    print("Chart saved to      : output/customer_distribution.png")
