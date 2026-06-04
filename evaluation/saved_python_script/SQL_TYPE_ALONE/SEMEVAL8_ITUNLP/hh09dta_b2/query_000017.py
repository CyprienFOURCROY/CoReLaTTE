import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()

    # Households that feel unsafe or very unsafe at home
    df_vlh_unsafe = df_vlh[df_vlh["vlh04"].isin([3.0, 4.0])]

    # Link individuals to those households
    df_merged = df_portad.merge(df_vlh_unsafe, on="folio", how="inner")

    # Group by state and compute metrics
    result = (
        df_merged.groupby("ent", dropna=False)
        .agg(
            average_age=("edad", "mean"),
            n_interviewed=("edad", "size"),
        )
        .reset_index()
        .sort_values(by="average_age", ascending=False)
    )

    # Optional: present state code as integer if possible
    try:
        result["ent"] = result["ent"].astype("Int64")
    except Exception:
        pass

    return result