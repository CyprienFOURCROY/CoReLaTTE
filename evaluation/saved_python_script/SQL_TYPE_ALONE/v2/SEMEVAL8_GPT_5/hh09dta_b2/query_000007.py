import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()

    # Filter interviewed individuals (assuming rel == 20 indicates successful interview)
    df_portad = df_portad[df_portad["rel"] == 20.0]

    # Merge individuals with household safety perception
    df = pd.merge(df_portad, df_vlh, on="folio", how="inner")

    # Households that feel unsafe or very unsafe at home
    df = df[df["vlh04"].isin([3.0, 4.0])]

    # Valid ages and states
    df = df.dropna(subset=["edad", "ent"])

    grouped = (
        df.groupby("ent")
        .agg(n_individuals=("edad", "size"), average_age=("edad", "mean"))
        .reset_index()
    )

    # Only states with at least 10 such individuals
    grouped = grouped[grouped["n_individuals"] >= 10]

    # Rank from highest to lowest average age
    grouped = grouped.sort_values(by="average_age", ascending=False)

    return grouped[["ent", "average_age"]].reset_index(drop=True)