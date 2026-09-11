import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_in = tables["ii_in"]

    # Map household to state (ent)
    ent_map = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"], keep="first")

    # Households where any member produced/sold dairy products in last 12 months
    dairy_hh = df_inr.loc[df_inr["inr02a"] == 1.0, ["folio"]].drop_duplicates()

    # Attach state
    dairy_hh = dairy_hh.merge(ent_map, on="folio", how="left")

    # Attach Liconsa receipt info
    liconsa = df_in[["folio", "in03a"]].drop_duplicates(subset=["folio"], keep="first")
    dairy_hh = dairy_hh.merge(liconsa, on="folio", how="left")

    # Flag households that received Liconsa milk
    dairy_hh["liconsa"] = dairy_hh["in03a"].eq(1.0).fillna(False)

    # Aggregate by state
    res = (
        dairy_hh.dropna(subset=["ent"])
        .groupby("ent", as_index=False)
        .agg(
            households_produce_dairy=("folio", "nunique"),
            households_produce_dairy_and_liconsa=("liconsa", "sum"),
        )
        .sort_values("ent")
        .reset_index(drop=True)
    )

    # Ensure integer types for counts and state codes
    res["ent"] = res["ent"].astype("int64")
    res["households_produce_dairy"] = res["households_produce_dairy"].astype("int64")
    res["households_produce_dairy_and_liconsa"] = res["households_produce_dairy_and_liconsa"].astype("int64")

    return res