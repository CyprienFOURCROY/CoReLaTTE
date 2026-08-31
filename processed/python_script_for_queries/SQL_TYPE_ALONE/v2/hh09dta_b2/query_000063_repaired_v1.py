import pandas as pd


def run_query(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # Load tables
    portad = tables['ii_portad'].copy()
    nna = tables['ii_nna'].copy()
    inc = tables['ii_in'].copy()

    # Ensure numeric types where needed
    portad['edad'] = pd.to_numeric(portad.get('edad'), errors='coerce')
    nna['nna01'] = pd.to_numeric(nna.get('nna01'), errors='coerce')
    inc['in02a10'] = pd.to_numeric(inc.get('in02a10'), errors='coerce')

    # Filter adults (18+) in Oaxaca
    adults_oax = portad[(portad.get('ent') == 20) & (portad['edad'] >= 18)].copy()

    # Households that explicitly reported owning/sharing a non-agricultural business (nna01 == 1)
    business_folios = nna.loc[nna['nna01'] == 1, 'folio'].dropna().unique()

    # Adults in those business-owning households
    business_adults = adults_oax[adults_oax['folio'].isin(business_folios)].copy()

    # Compute average age within this Oaxaca business-owning adult group
    avg_age = business_adults['edad'].mean()

    # Restrict to those older than the average age
    above_avg = business_adults[business_adults['edad'] > avg_age].copy()

    # Households that received a strictly positive direct amount from Other Government Program
    positive_prog_folios = inc.loc[inc['in02a10'] > 0, 'folio'].dropna().unique()

    # Count individuals (rows) whose households are in the positive set
    count_individuals = above_avg[above_avg['folio'].isin(positive_prog_folios)].shape[0]

    return pd.DataFrame({
        'n_individuals_above_avg_with_benefit': [int(count_individuals)]
    })
