import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_nna = tables["ii_nna"][["folio", "nna01"]].copy()
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_in = tables["ii_in"][["folio", "in02a10"]].copy()

    # Households with non-ag business
    nna_hh = df_nna[df_nna["nna01"] == 1.0][["folio"]].drop_duplicates()

    # Households that use a plot of land
    su_hh = df_su[df_su["su01"] == 1.0][["folio"]].drop_duplicates()

    # Eligible households: intersection
    eligible = nna_hh.merge(su_hh, on="folio", how="inner")

    # Merge with payments
    eligible_pay = eligible.merge(df_in, on="folio", how="left")

    # Positive direct payments from Other Government Program
    paid_pos = eligible_pay[eligible_pay["in02a10"] > 0].copy()

    # Average among such households (those with positive payments)
    avg_payment = paid_pos["in02a10"].mean()

    # Above average
    result = (
        paid_pos[paid_pos["in02a10"] > avg_payment][["folio", "in02a10"]]
        .sort_values(by="in02a10", ascending=False)
        .reset_index(drop=True)
    )

    return result