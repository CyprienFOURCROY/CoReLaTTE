import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_inr = tables["ii_inr"].copy()
    df_se = tables["ii_se"].copy()

    # Filter individuals in Oaxaca (ent == 20)
    df_oax = df_portad[df_portad["ent"] == 20]

    if df_oax.empty:
        return pd.DataFrame(columns=["folio", "average_age", "num_individuals"])

    # Aggregate average age and number of individuals per household
    agg = (
        df_oax.groupby("folio")
        .agg(
            average_age=("edad", "mean"),
            num_individuals=("ls", pd.Series.nunique),
        )
        .reset_index()
    )

    # Households with disease/accident/hospitalization in last 5 years
    se_yes = df_se[df_se["se01b"] == 1][["folio"]].drop_duplicates()

    # Households that produced/sold eggs in last 12 months
    inr_yes = df_inr[df_inr["inr02d"] == 1][["folio"]].drop_duplicates()

    # Merge conditions with Oaxaca households
    eligible = agg.merge(se_yes, on="folio", how="inner").merge(inr_yes, on="folio", how="inner")

    # Drop households with NaN average age (if any)
    eligible = eligible[~eligible["average_age"].isna()]

    # Sort and take top 5 by highest average age
    result = eligible.sort_values(by="average_age", ascending=False).head(5)

    return result[["folio", "average_age", "num_individuals"]]