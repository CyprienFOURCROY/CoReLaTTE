import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04", "vlh18a"]].copy()

    # Households that own/share a non-ag business
    own_share = df_nna[df_nna["nna01"] == 1.0]

    # Merge with safety and robbery info
    merged = own_share.merge(df_vlh, on="folio", how="inner")

    # Average total entries/robberies since 2005 among owners
    avg_count = merged["vlh18a"].mean()

    # Filter: unsafe or very unsafe and count above average
    result = (
        merged[
            merged["vlh04"].isin([3.0, 4.0])
            & merged["vlh18a"].notna()
            & (merged["vlh18a"] > avg_count)
        ][["folio", "vlh04", "vlh18a"]]
        .sort_values(by="vlh18a", ascending=False)
        .reset_index(drop=True)
    )

    return result