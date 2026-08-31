import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_inr = tables["ii_inr"].copy()
    df_nna = tables["ii_nna"].copy()

    # Household-level state and size
    hh_portad = (
        df_portad.groupby("folio")
        .agg(ent=("ent", "first"), household_size=("ls", "count"))
        .reset_index()
    )

    # Household-level eggs production/sales in last 12 months
    inr_eggs = df_inr[["folio", "inr02d"]].copy()
    inr_eggs["eggs_yes"] = (inr_eggs["inr02d"] == 1.0).fillna(False)
    hh_inr = inr_eggs.groupby("folio")["eggs_yes"].any().reset_index(name="eggs_12m")

    # Household-level non-ag business ownership
    nna_nonag = df_nna[["folio", "nna01"]].copy()
    nna_nonag["nonag_yes"] = (nna_nonag["nna01"] == 1.0).fillna(False)
    hh_nna = nna_nonag.groupby("folio")["nonag_yes"].any().reset_index(name="nonag_business")

    # Merge household characteristics and filters
    hh = (
        hh_portad.merge(hh_inr, on="folio", how="left")
        .merge(hh_nna, on="folio", how="left")
    )
    hh["eggs_12m"] = hh["eggs_12m"].fillna(False)
    hh["nonag_business"] = hh["nonag_business"].fillna(False)

    eligible = hh[hh["eggs_12m"] & hh["nonag_business"]].copy()
    if eligible.empty:
        return pd.DataFrame(
            {
                "ent": pd.Series(dtype="Int64"),
                "household_size": pd.Series(dtype="Int64"),
                "num_households": pd.Series(dtype="Int64"),
            }
        )

    agg = (
        eligible.groupby(["ent", "household_size"], dropna=False)
        .size()
        .reset_index(name="num_households")
    )

    # Cast types
    agg["ent"] = pd.to_numeric(agg["ent"], errors="coerce").round().astype("Int64")
    agg["household_size"] = pd.to_numeric(agg["household_size"], errors="coerce").astype("Int64")
    agg["num_households"] = pd.to_numeric(agg["num_households"], errors="coerce").astype("Int64")

    max_n = agg["num_households"].max()
    top = agg[agg["num_households"] == max_n].sort_values(
        ["num_households", "ent", "household_size"], ascending=[False, True, True]
    ).reset_index(drop=True)

    return top