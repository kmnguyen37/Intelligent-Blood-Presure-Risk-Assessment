# Data Issues Log

This document records all data-related issues discovered during Project 1.

Each issue includes:

- Observation
- Investigation
- Root Cause
- Resolution
- Justification

---

# D001 — RIDAGEYR Imported as Extremely Small Floating-Point Value

**Status:** Resolved

## Observation

Several participants had the following value for `RIDAGEYR`:

```
5.397605e-79
```

This value appeared in place of an expected age.

## Investigation

- Verified that `RIDAGEYR` was imported as `float64`.
- Inspected affected rows.
- Confirmed that the values corresponded to infant participants.
- Determined that the value was produced during the SAS (`.XPT`) to pandas import process rather than originating from NHANES.

## Root Cause

A pandas `read_sas()` import artifact caused zero values to be represented as extremely small floating-point numbers.

The original NHANES data were not corrupted.

## Resolution

Within the working modeling dataframe (`model_v1_df`), replace:

```
RIDAGEYR < 0.5
```

with:

```
RIDAGEYR = 0
```

The original NHANES files remain unchanged.

## Justification

Age is recorded in completed years.

Values smaller than 0.5 years represent infants younger than one year and should be encoded as age 0.

The correction is applied only to the processed modeling dataframe to preserve the integrity of the raw source data.

---

## Lessons Learned

- Always inspect imported values before performing transformations.
- Never modify the raw source files.
- Document every correction applied to the processed dataset.