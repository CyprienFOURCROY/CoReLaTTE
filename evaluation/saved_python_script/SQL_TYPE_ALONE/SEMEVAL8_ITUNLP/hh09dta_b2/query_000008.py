import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()
    df_vlh = tables["ii_vlh"][["folio", "vlh04"]].copy()

    # Households that own/share a non-ag business
    df_nna_yes = df_nna[df_nna["nna01"] == 1.0]

    # Interviewed individuals (assumed rel == 20 indicates completed interview)
    df_interviewed = df_portad[df_portad["rel"] == 20.0]

    # Keep only individuals in qualifying households
    df_merged = df_interviewed.merge(df_nna_yes[["folio"]], on="folio", how="inner")

    # Merge with 'Feel safe at home?' responses
    df_merged = df_merged.merge(df_vlh, on="folio", how="inner")
    df_merged = df_merged[df_merged["vlh04"].notna()]

    # Group by response category
    g = df_merged.groupby("vlh04", dropna=False)
    avg = g["edad"].mean().reset_index(name="average_age")
    cnt = g.size().reset_index(name="n_individuals")

    result = avg.merge(cnt, on="vlh04")
    result = result.sort_values("average_age", ascending=False).reset_index(drop=True)
    return result