import pandas as pd

def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df_su = tables["ii_su"][["folio", "su01"]].copy()
    df_in = tables["ii_in"][["folio", "in01a10_1", "in02a10"]].copy()

    # Households where a member uses land for farming
    su_farm = df_su[df_su["su01"] == 1.0][["folio"]].drop_duplicates()

    # Participants in Other Government Program (codes 1 or 2)
    participants = df_in[df_in["in01a10_1"].isin([1.0, 2.0])].drop_duplicates(subset=["folio"])

    # Merge to keep only farming households that participated
    merged = su_farm.merge(participants, on="folio", how="inner")

    # Keep positive direct payments
    positive = merged[merged["in02a10"] > 0].copy()

    if positive.empty:
        return positive[["folio", "in02a10"]].reset_index(drop=True)

    avg_payment = positive["in02a10"].mean()

    result = positive[positive["in02a10"] > avg_payment][["folio", "in02a10"]].reset_index(drop=True)
    return result