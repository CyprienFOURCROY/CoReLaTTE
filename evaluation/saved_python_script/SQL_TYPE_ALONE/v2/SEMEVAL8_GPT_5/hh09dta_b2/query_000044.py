import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_se = tables["ii_se"].copy()

    # Create age flags
    df_portad["is65plus"] = df_portad["edad"] >= 65
    df_portad["isunder18"] = df_portad["edad"] < 18

    age_flags = (
        df_portad.groupby("folio")
        .agg(has_65plus=("is65plus", "any"), has_under18=("isunder18", "any"))
        .reset_index()
    )

    # Households reporting a death in last five years
    death_hh = df_se[df_se["se01a"] == 1.0][["folio"]].drop_duplicates()

    merged = death_hh.merge(age_flags, on="folio", how="inner")
    eligible = merged[merged["has_65plus"] & merged["has_under18"]]

    count = eligible["folio"].nunique()
    return pd.DataFrame({"households_count": [int(count)]})