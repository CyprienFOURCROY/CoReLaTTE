import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_su = tables["ii_su"].copy()

    ent_map = (
        df_portad[["folio", "ent"]]
        .dropna(subset=["folio", "ent"])
        .drop_duplicates(subset=["folio"])
    )
    # Convert to nullable integer for clarity; ignore if it fails
    try:
        ent_map["ent"] = ent_map["ent"].astype("Int64")
    except Exception:
        pass

    df_in_subset = (
        df_in.loc[df_in["in03a"] == 1, ["folio", "in02a10"]]
        .dropna(subset=["folio"])
        .drop_duplicates(subset=["folio"])
    )

    df_su_subset = (
        df_su.loc[df_su["su01"] == 1, ["folio"]]
        .dropna(subset=["folio"])
        .drop_duplicates(subset=["folio"])
    )

    df_valid = pd.merge(df_in_subset, df_su_subset, on="folio", how="inner")
    df_valid = df_valid.merge(ent_map, on="folio", how="left")
    df_valid = df_valid[~df_valid["ent"].isna()]

    agg_df = (
        df_valid.groupby("ent", as_index=False)
        .agg(
            avg_in02a10=("in02a10", "mean"),
            household_count=("folio", "nunique"),
        )
    )

    result = (
        agg_df.sort_values(by="avg_in02a10", ascending=False, na_position="last")
        .head(10)
        .reset_index(drop=True)
    )

    return result