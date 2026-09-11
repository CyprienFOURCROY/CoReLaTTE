import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_nna = tables["ii_nna"][["folio", "nna01"]].drop_duplicates(subset=["folio"]).copy()

    # Oaxaca households
    df_portad_oxa = df_portad[df_portad["ent"] == 20.0]

    # Merge household-level non-ag business ownership
    df = df_portad_oxa.merge(df_nna, on="folio", how="left")
    df = df[df["nna01"] == 1.0]

    if df.empty:
        return pd.DataFrame({"pair_count": [0]})

    # Overall average age among individuals in selected households
    avg_age = df["edad"].dropna().mean()
    if pd.isna(avg_age):
        return pd.DataFrame({"pair_count": [0]})

    # Conditions for A and B
    df["is_A"] = df["rel"] == 20.0
    df["is_B"] = df["edad"] > avg_age
    df["is_overlap"] = df["is_A"] & df["is_B"]

    # Count ordered pairs within each household
    grp = df.groupby("folio").agg(
        nA=("is_A", "sum"),
        nB=("is_B", "sum"),
        nOverlap=("is_overlap", "sum"),
    )
    pair_count = int((grp["nA"] * grp["nB"] - grp["nOverlap"]).sum())

    return pd.DataFrame({"pair_count": [pair_count]})