def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    import numpy as np

    df_nna = tables["ii_nna"]
    df_in = tables["ii_in"]

    # Step 1: Households where a member owns/shares a non-ag business (nna01 == 1)
    nna_owners = df_nna[df_nna["nna01"] == 1.0][["folio"]]

    # Step 2: Households that participated in and received income from "Other Government Program" (in01a10_1 == 1)
    # and have a non-null, positive amount in in02a10
    df_in_filtered = df_in[
        (df_in["in01a10_1"] == 1.0) &
        (df_in["in02a10"].notna()) &
        (df_in["in02a10"] > 0)
    ][["folio", "in02a10"]]

    # Step 3: Inner join on folio
    merged = nna_owners.merge(df_in_filtered, on="folio", how="inner")

    # Step 4: Compute average amount for this group
    avg_amount = merged["in02a10"].mean()

    # Step 5: Select households with amount > average, order descending
    result = merged[merged["in02a10"] > avg_amount].sort_values("in02a10", ascending=False)

    # Step 6: Rename columns as required
    result = result.rename(columns={"folio": "household_id", "in02a10": "amount_received"})

    # Reset index for clean output
    return result[["household_id", "amount_received"]].reset_index(drop=True)