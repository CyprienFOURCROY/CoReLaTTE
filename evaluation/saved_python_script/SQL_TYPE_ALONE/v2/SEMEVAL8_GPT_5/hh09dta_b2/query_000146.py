import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_vlh = tables["ii_vlh"]
    df_ah = tables["ii_ah"]

    # Households where at least one member owns a motor vehicle
    ah = df_ah[["folio", "ah03d"]].copy()
    ah["owns_motor_vehicle"] = ah["ah03d"] == 1
    hh_vehicle = ah.groupby("folio", as_index=False)["owns_motor_vehicle"].any()

    # Merge with 'Feel safe at home?' score
    vlh = df_vlh[["folio", "vlh04"]].copy()
    eligible = hh_vehicle.merge(vlh, on="folio", how="left")
    eligible = eligible[eligible["owns_motor_vehicle"] & eligible["vlh04"].notna()]

    # Attach state
    ent_by_folio = df_portad[["folio", "ent"]].dropna(subset=["ent"]).drop_duplicates("folio")
    eligible = eligible.merge(ent_by_folio, on="folio", how="left")
    eligible = eligible[eligible["ent"].notna()]

    # Overall average score among eligible households
    overall_avg = eligible["vlh04"].mean()

    # State-level aggregation
    result = (
        eligible.groupby("ent")
        .agg(average_score=("vlh04", "mean"), household_count=("folio", "nunique"))
        .reset_index()
    )

    # Filter and rank
    result = result[(result["household_count"] >= 30) & (result["average_score"] > overall_avg)]
    result = result.sort_values(by="average_score", ascending=False).reset_index(drop=True)

    return result