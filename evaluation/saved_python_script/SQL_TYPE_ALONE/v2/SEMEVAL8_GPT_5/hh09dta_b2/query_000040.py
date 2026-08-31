import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_vlh = tables["ii_vlh"].copy()

    # Households in Oaxaca
    hh_ent = (
        df_portad[["folio", "ent"]]
        .dropna(subset=["ent"])
        .groupby("folio", as_index=False)
        .first()
    )

    # Adult count (age 18+) per household
    adults = df_portad[df_portad["edad"].notna() & (df_portad["edad"] >= 18)]
    adult_counts = adults.groupby("folio").size().reset_index(name="adult_count")

    # Valid responses to "Feel safe at home?"
    valid_vlh = df_vlh[df_vlh["vlh04"].isin([1.0, 2.0, 3.0, 4.0])]

    # Merge and filter to Oaxaca
    df = valid_vlh.merge(hh_ent, on="folio", how="left")
    df = df[df["ent"] == 20.0]

    # Merge adult counts
    df = df.merge(adult_counts, on="folio", how="left")
    df["adult_count"] = df["adult_count"].fillna(0).astype(float)

    # Compute average adults per response category
    res = df.groupby("vlh04", as_index=False)["adult_count"].mean()
    res = res.rename(columns={"vlh04": "response_code", "adult_count": "avg_adults"})

    # Map response labels
    label_map = {1.0: "Very safe", 2.0: "Safe", 3.0: "Unsafe", 4.0: "Very unsafe"}
    res["response"] = res["response_code"].map(label_map)

    res = res[["response_code", "response", "avg_adults"]].sort_values("response_code").reset_index(drop=True)
    return res