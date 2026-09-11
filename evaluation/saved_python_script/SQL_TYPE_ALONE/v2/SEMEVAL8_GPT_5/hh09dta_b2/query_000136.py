import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]
    df_inr = tables["ii_inr"]

    # Map household to state
    df_state = df_portad[["folio", "ent"]].drop_duplicates(subset=["folio"])

    # Households with positive amount directly from Other Government Program
    df_pos = df_in[["folio", "in02a10"]].copy()
    df_pos = df_pos[df_pos["in02a10"].fillna(0) > 0]

    # Dairy production/selling indicator
    df_dairy = df_inr[["folio", "inr02a"]].copy()

    # Merge to get state and dairy info
    df_pos_state = df_pos.merge(df_state, on="folio", how="left").merge(df_dairy, on="folio", how="left")
    df_pos_state["dairy_flag"] = (df_pos_state["inr02a"] == 1.0).astype(int)

    # Aggregate by state
    res = (
        df_pos_state.groupby("ent", as_index=False)
        .agg(
            total_households=("folio", pd.Series.nunique),
            dairy_producers=("dairy_flag", "sum"),
        )
    )

    # Filter states with at least 30 such households
    res = res[res["total_households"] >= 30].sort_values("ent").reset_index(drop=True)
    return res