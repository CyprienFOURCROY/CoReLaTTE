import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_su = tables["ii_su"]
    df_in = tables["ii_in"]

    # Household-level average age and state
    hh_age = (
        df_portad.groupby("folio", as_index=False)
        .agg(average_household_age=("edad", "mean"), ent=("ent", "first"))
    )

    # Households that use plot/land
    hh_use_plot = df_su.loc[df_su["su01"] == 1, ["folio"]].drop_duplicates()

    # Households with positive direct amount from Other Government Program
    hh_pos_othergov = df_in.loc[df_in["in02a10"] > 0, ["folio"]].drop_duplicates()

    # Eligible households: both conditions
    eligible = hh_use_plot.merge(hh_pos_othergov, on="folio", how="inner")

    # Merge with household age/state
    merged = eligible.merge(hh_age, on="folio", how="inner").dropna(subset=["ent", "average_household_age"])

    # Aggregate by state
    result = (
        merged.groupby("ent", as_index=False)
        .agg(average_household_age=("average_household_age", "mean"), households=("folio", "nunique"))
        .sort_values(by="average_household_age", ascending=False)
        .head(10)
    )

    # Cast state code to integer
    result["ent"] = result["ent"].astype("int64")

    return result[["ent", "average_household_age", "households"]]