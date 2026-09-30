"""
Shared helpers for loading and cleaning 2021 Census Dissemination Area (DA) data.

Used by both the hex-grid distribution step (Section 1) and the census-tract
aggregation step (Section 3) in the DA analysis file so the column mapping and cleaning logic only
live in one place.
"""
import pandas as pd
import geopandas as gpd

# Raw column names as they appear in the Statistics Canada DA export.
CENSUS_COLUMNS = {
    'pop_total':
        'Population and dwelling counts / Population, 2021',
    'visible_minority':
        ' Indigenous and Visible Minorities - Total Sex / Total - Visible minority for '
        'the population in private households - 25% sample data ; Both sexes / '
        'Total visible minority population ; Both sexes ',
    'first_gen_immigrants':
        'Immigration - Total Sex / Total - Generation status for the population in '
        'private households - 25% sample data ; Both sexes / First generation ; Both sexes ',
    'seniors':
        'Age & Sex - Both sexes / Total - Age groups of the population - 100% data ; '
        'Both sexes / 65 years and over ; Both sexes',
    'children':
        'Age & Sex - Both sexes / Total - Age groups of the population - 100% data ; '
        'Both sexes / 0 to 14 years ; Both sexes',
    'low_income_1':
        'Income - Total Sex / Total - After-tax income groups in 2020 for the population '
        'aged 15 years and over in private households - 100% data ; Both sexes / '
        'With after-tax income ; Both sexes / Under $10,000 (including loss) ; Both sexes',
    'low_income_2':
        'Income - Total Sex / Total - After-tax income groups in 2020 for the population '
        'aged 15 years and over in private households - 100% data ; Both sexes / '
        'With after-tax income ; Both sexes / $10,000 to $19,999 ; Both sexes ',
    'low_income_3':
        'Income - Total Sex / Total - After-tax income groups in 2020 for the population '
        'aged 15 years and over in private households - 100% data ; Both sexes / '
        'With after-tax income ; Both sexes / $20,000 to $29,999 ; Both sexes',
}

# Standardized demographic count columns produced by load_da_census()
COUNT_COLS = ['pop_total', 'visible_minority', 'first_gen_immigrants',
              'seniors', 'children', 'low_income']


def safe_float(col):
    """Convert a raw census column (commas, blanks, 'x' suppression codes, etc.) to numeric."""
    return pd.to_numeric(
        col.astype(str).str.replace(',', '', regex=False).str.strip()
        .replace({'': '0', 'nan': '0', 'NaN': '0', '...': '0', 'x': '0'}),
        errors='coerce'
    ).fillna(0)


def load_da_census(path):
    """
    Load a DA-level census file (GeoPackage/Shapefile) and add standardized,
    numeric demographic count columns:
        pop_total, visible_minority, first_gen_immigrants,
        seniors, children, low_income

    Missing raw columns are filled with 0 and flagged with a warning, rather
    than raising, since suppressed/renamed columns are common across exports.
    """
    da = gpd.read_file(path)

    for raw_col in CENSUS_COLUMNS.values():
        if raw_col not in da.columns:
            print(f"  WARNING: column not found — {raw_col[:60]}...")
            da[raw_col] = 0

    da['pop_total']            = safe_float(da[CENSUS_COLUMNS['pop_total']])
    da['visible_minority']     = safe_float(da[CENSUS_COLUMNS['visible_minority']])
    da['first_gen_immigrants'] = safe_float(da[CENSUS_COLUMNS['first_gen_immigrants']])
    da['seniors']              = safe_float(da[CENSUS_COLUMNS['seniors']])
    da['children']             = safe_float(da[CENSUS_COLUMNS['children']])
    da['low_income'] = (
        safe_float(da[CENSUS_COLUMNS['low_income_1']]) +
        safe_float(da[CENSUS_COLUMNS['low_income_2']]) +
        safe_float(da[CENSUS_COLUMNS['low_income_3']])
    )
    return da
