# Raw page text (not published)

`scripts/parse_drugscom.py` reads plain text copied from three Drugs.com condition pages. That text is Drugs.com's content, so it isn't committed: everything in this folder except this file is git-ignored.

To recreate it:

1. Open each page in a browser:
   - Depression: https://www.drugs.com/condition/depression.html
   - Major Depressive Disorder: https://www.drugs.com/condition/major-depressive-disorder.html
   - Bipolar Disorder: https://www.drugs.com/condition/bipolar-disorder.html
2. Make sure the whole drug list is showing, not just the first page of results.
3. Select the drug table, from its header row (`Drug name`, `Rating`, `Reviews`...) through the last drug, copy it, and paste it into a plain-text file here:
   - `drugscom_depression_raw.txt`
   - `drugscom_mdd_raw.txt`
   - `drugscom_bipolar_raw.txt`
4. Run `python scripts/parse_drugscom.py` from the repo root.

The parser expects each drug to start with a `Details for <name>` line, which is how the table copies out of the page. If Drugs.com changes its layout, the parser stops with an error that names the line it couldn't read. It also stops if a drug name isn't in `scripts/make_meta.py`; add new drugs there first.

The published CSVs were built from copies taken on October 22 (Depression) and October 23, 2026 (the other two).
