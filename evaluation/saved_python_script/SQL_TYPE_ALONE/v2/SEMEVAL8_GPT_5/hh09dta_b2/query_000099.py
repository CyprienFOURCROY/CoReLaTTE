import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_inr = tables["ii_inr"]
    df_in = tables["ii_in"]

    adults = df_portad.loc[df_portad["edad"] >= 18, ["folio", "ent"]].copy()

    hh = df_inr[["folio", "inr02j"]].merge(df_in[["folio", "in01a10_1"]], on="folio", how="inner")
    hh["eligible_hh"] = (hh["inr02j"] == 1.0) & (hh["in01a10_1"] == 1.0)

    adults = adults.merge(hh[["folio", "eligible_hh"]], on="folio", how="left")
    adults["eligible_hh"] = adults["eligible_hh"].fillna(False)
    adults["eligible"] = adults["eligible_hh"].astype(int)

    state_counts = adults.groupby("ent", dropna=False)["eligible"].sum().reset_index()
    state_counts = state_counts[state_counts["ent"].notna()].copy()

    avg_count = state_counts["eligible"].mean()

    above = state_counts[state_counts["eligible"] > avg_count].copy()
    above = above.sort_values(by="eligible", ascending=False)
    above = above.rename(columns={"eligible": "num_adults"})
    above["ent"] = above["ent"].astype(int)

    return above[["ent", "num_adults"]]