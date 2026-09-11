import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_portad = tables["ii_portad"].copy()
    df_in = tables["ii_in"].copy()
    df_nna = tables["ii_nna"].copy()

    # Household size from ii_portad (count individuals per household)
    hh_size = (
        df_portad.groupby("folio")
        .agg(hh_size=("ls", "count"))
        .reset_index()
    )

    # State (ent) per household
    ent_per_folio = (
        df_portad.groupby("folio", as_index=False)
        .agg(ent=("ent", "first"))
    )

    # Oaxaca households (ent == 20)
    oaxaca_folios = ent_per_folio[ent_per_folio["ent"] == 20][["folio"]]

    # Households that received a positive direct amount from Other Government Program
    recipients = df_in[df_in["in02a10"] > 0][["folio", "in02a10"]]

    # Oaxaca recipients
    oax_recipients = recipients.merge(oaxaca_folios, on="folio", how="inner")

    if oax_recipients.empty:
        return pd.DataFrame({"owns_nonag_business": [], "avg_household_size": []})

    # Oaxaca average among such recipients
    oax_avg = oax_recipients["in02a10"].mean()

    # Households with amount exceeding Oaxaca average
    above_avg = oax_recipients[oax_recipients["in02a10"] > oax_avg][["folio"]]

    if above_avg.empty:
        return pd.DataFrame({"owns_nonag_business": [], "avg_household_size": []})

    # Merge with non-ag business ownership and household size
    merged = (
        above_avg
        .merge(df_nna[["folio", "nna01"]], on="folio", how="left")
        .merge(hh_size, on="folio", how="left")
    )

    # Keep only valid ownership categories 1 (Yes) and 2 (No)
    merged = merged[merged["nna01"].isin([1, 2])]

    if merged.empty:
        return pd.DataFrame({"owns_nonag_business": [], "avg_household_size": []})

    # Compute average household size by ownership
    result = (
        merged.groupby("nna01", as_index=False)["hh_size"]
        .mean()
        .rename(columns={"hh_size": "avg_household_size"})
    )

    # Map ownership to labels
    mapping = {1: "Yes", 2: "No"}
    result["owns_nonag_business"] = result["nna01"].map(mapping)

    return result[["owns_nonag_business", "avg_household_size"]]