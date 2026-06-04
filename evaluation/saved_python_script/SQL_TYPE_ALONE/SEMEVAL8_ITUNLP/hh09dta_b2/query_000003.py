import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_su = tables["ii_su"]

    # Households that use a plot/land for farming
    su_yes = df_su.loc[df_su["su01"] == 1.0, ["folio"]].dropna().drop_duplicates()

    # Households that produced/sold meat in last 12 months
    inr_meat_yes = df_inr.loc[df_inr["inr02c"] == 1.0, ["folio"]].dropna().drop_duplicates()

    # Intersection of eligible households
    eligible_folios = pd.merge(su_yes, inr_meat_yes, on="folio", how="inner")

    # Individuals in eligible households
    df_indiv = df_portad[df_portad["folio"].isin(eligible_folios["folio"])].copy()

    # Drop rows where state is missing
    df_indiv = df_indiv[df_indiv["ent"].notna()]

    # Aggregate: average age and count of individuals (with non-missing age) by state
    result = (
        df_indiv.groupby("ent", as_index=False)
        .agg(average_age=("edad", "mean"), n_individuals=("edad", "count"))
        .sort_values(by="average_age", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    return result