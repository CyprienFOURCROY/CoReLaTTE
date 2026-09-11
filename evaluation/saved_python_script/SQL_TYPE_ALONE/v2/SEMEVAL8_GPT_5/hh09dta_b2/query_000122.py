import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"]
    df_in = tables["ii_in"]

    # Compute overall average among all recipients (positive amounts)
    recipients = df_in["in02a10"].dropna()
    recipients = recipients[recipients > 0]
    if recipients.empty:
        return pd.DataFrame({"folio": pd.Series(dtype=object), "in02a10": pd.Series(dtype="float64")})
    avg_amount = recipients.mean()

    # Map household to state and filter Oaxaca (ent == 20)
    ent_by_folio = df_portad[["folio", "ent"]].dropna(subset=["ent"]).drop_duplicates(subset=["folio"])

    merged = pd.merge(df_in[["folio", "in02a10"]], ent_by_folio, on="folio", how="left")

    result = merged[
        (merged["ent"] == 20.0) &
        (merged["in02a10"].notna()) &
        (merged["in02a10"] > avg_amount)
    ][["folio", "in02a10"]].copy()

    result = result.sort_values(by="in02a10", ascending=False).reset_index(drop=True)
    return result