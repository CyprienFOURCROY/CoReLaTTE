import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_nna = tables["ii_nna"]
    df_su = tables["ii_su"]

    # Households with non-ag business
    hh_nna = (
        df_nna.loc[df_nna["nna01"] == 1.0, ["folio"]]
        .dropna(subset=["folio"])
        .drop_duplicates()
    )

    # Households that use a plot/land for farming
    hh_su = (
        df_su.loc[df_su["su01"] == 1.0, ["folio"]]
        .dropna(subset=["folio"])
        .drop_duplicates()
    )

    # Households that satisfy both conditions
    eligible_hh = hh_nna.merge(hh_su, on="folio", how="inner")

    # Individuals in eligible households
    ind = df_portad.merge(eligible_hh, on="folio", how="inner")

    # Compute average age and count per state
    result = (
      ind.groupby("ent", dropna=True)
         .agg(average_age=("edad", "mean"), num_individuals=("edad", "count"))
         .sort_values("average_age", ascending=False)
         .head(10)
         .reset_index()
    )

    # Ensure state codes are integer-like where possible
    if "ent" in result.columns:
        result["ent"] = result["ent"].astype("Int64")

    return result