"""Parse raw Drugs.com condition-page text and build the project's drug tables.

Usage (from the repo root):
  python scripts/make_meta.py        # writes data/drug_meta.json (brand map, classes, groups)
  python scripts/parse_drugscom.py   # parses every page listed in PAGES

Inputs:
  data/raw/*.txt                     text copied from Drugs.com condition pages (not in the repo;
                                     see data/raw/README.md for how to recreate them)
Outputs:
  data/drugscom_listings.csv         one row per listing per condition page, unmerged
  data/drugscom_ratings_long.csv     one row per drug per condition, plus one row per drug per combined view

Merge rules:
  - Within a condition page, a generic listing's reviews already include its brand-name
    listings, so the generic's rating and count are used as-is and brand rows are not added.
    Checked: brand counts never exceed their generic's.
  - Across condition pages, reviews are separate (each review is filed under one condition),
    so combined views sum counts and takes the review-weighted average rating. Inputs are rounded
    to one decimal, so a combined rating can be off by up to about 0.05.
"""
import re, json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PAGES = [  # (condition label, raw text file)
    ("Depression", "data/raw/drugscom_depression_raw.txt"),
    ("Major depressive disorder", "data/raw/drugscom_mdd_raw.txt"),
    ("Bipolar disorder", "data/raw/drugscom_bipolar_raw.txt"),
]
# Combined views: label -> conditions it sums. The dashboard shows only Total, Major depression and Bipolar disorder.
VIEWS = {
    "Major depression": ["Depression", "Major depressive disorder"],
    "Total": ["Depression", "Major depressive disorder", "Bipolar disorder"],
}
RATING_RE = re.compile(r"^(\d+(?:\.\d)?)\s+(\d+)\s+reviews?for\b", re.I)
RX_TOKENS = {"Rx", "OTC", "Rx/OTC"}
TAGS = {"Off-label", "New approval"}


def parse(text, condition):
    blocks = re.split(r"^Details for .*$", text, flags=re.M)[1:]
    rows = []
    for b in blocks:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        name, i, tags = lines[0], 1, set()
        while lines[i] in TAGS:
            tags.add(lines[i]); i += 1
        m = RATING_RE.match(lines[i])
        if m:
            rating, reviews = float(m.group(1)), int(m.group(2))
        elif lines[i].startswith("Rate"):
            rating, reviews = None, 0
        else:
            raise ValueError(f"[{condition}] can't parse rating line for {name}: {lines[i]!r}")
        toks = " ".join(lines[i + 1:]).split()
        alcohol = bool(toks) and toks[-1] == "✕"
        if alcohol:
            toks = toks[:-1]
        rx = next((t for t in toks if t in RX_TOKENS), None)
        rest = [t for t in toks if t not in RX_TOKENS]
        if len(rest) > 2:
            raise ValueError(f"[{condition}] unexpected tokens for {name}: {toks}")
        rows.append(dict(condition=condition, listing_name=name, off_label="Off-label" in tags,
                         new_approval="New approval" in tags, rating=rating, reviews=reviews, rx_otc=rx,
                         pregnancy_cat=rest[0] if len(rest) == 2 else None,
                         csa_schedule=rest[-1] if rest else None, alcohol_interaction=alcohol))
    return rows


def wavg(ratings, counts):
    pairs = [(r, n) for r, n in zip(ratings, counts) if r is not None and not pd.isna(r) and n > 0]
    tot = sum(n for _, n in pairs)
    return round(sum(r * n for r, n in pairs) / tot, 1) if tot else None


if __name__ == "__main__":
    missing = [p for _, p in PAGES if not (ROOT / p).exists()]
    if missing:
        raise SystemExit(f"Missing raw page text: {', '.join(missing)}\n"
                         "These files aren't in the repo. See data/raw/README.md for how to recreate them.")
    meta = json.load(open(DATA / "drug_meta.json", encoding="utf-8"))
    b2g = meta["brand_to_generic"]
    lst = pd.DataFrame([r for cond, path in PAGES for r in parse(open(ROOT / path, encoding="utf-8").read(), cond)])
    lst["generic_name"] = lst.listing_name.map(lambda n: b2g.get(n, n))
    lst["is_brand_listing"] = lst.listing_name.isin(b2g.keys())
    lst.to_csv(DATA / "drugscom_listings.csv", index=False, lineterminator="\n")

    unknown = sorted(set(lst.generic_name) - set(meta["drug_class"]))
    assert not unknown, f"No class assigned for: {unknown}"

    per = []
    for (cond, g), grp in lst.groupby(["condition", "generic_name"], sort=False):
        gen = grp[~grp.is_brand_listing]
        assert len(gen) == 1, f"[{cond}] brand listings with no generic listing: {g} {list(grp.listing_name)}"
        gen = gen.iloc[0]
        brand_sum = int(grp[grp.is_brand_listing].reviews.sum())
        assert brand_sum <= gen.reviews, f"[{cond}] brand reviews exceed generic for {g}: {brand_sum} > {gen.reviews}"
        per.append(dict(condition=cond, generic_name=g, rating=gen.rating, reviews=int(gen.reviews),
                        off_label=gen.off_label, new_approval=bool(grp.new_approval.any()),
                        brands_listed=list(grp[grp.is_brand_listing].listing_name),
                        rx_otc=gen.rx_otc, pregnancy_cat=gen.pregnancy_cat, csa_schedule=gen.csa_schedule,
                        alcohol_interaction=gen.alcohol_interaction))
    per = pd.DataFrame(per)

    # Drug-level attributes: same across pages; report any disagreement
    for col in ["rx_otc", "pregnancy_cat", "csa_schedule", "alcohol_interaction"]:
        diff = per.groupby("generic_name")[col].nunique(dropna=False)
        if (diff > 1).any():
            print(f"NOTE: {col} differs across pages for", list(diff[diff > 1].index))

    order = [c for c, _ in PAGES]
    out = []
    for g, grp in per.groupby("generic_name", sort=False):
        grp = grp.set_index("condition").reindex([c for c in order if c in set(grp.condition)])
        first = grp.iloc[0]
        brands = []
        for bl in grp.brands_listed:
            brands += [b for b in bl if b not in brands]
        brands += [b for b in meta["other_brands"].get(g, []) if b not in brands]
        common = dict(generic_name=g, brand_names="; ".join(brands), drug_class=meta["drug_class"][g],
                      class_group=meta["class_group"][g], rx_otc=first.rx_otc or "",
                      new_approval="yes" if grp.new_approval.any() else "no",
                      pregnancy_cat=first.pregnancy_cat or "", csa_schedule=first.csa_schedule or "",
                      alcohol_interaction="yes" if first.alcohol_interaction else "no",
                      conditions_listed="; ".join(grp.index))
        for cond, r in grp.iterrows():
            out.append(dict(common, condition=cond, rating=r.rating, reviews=int(r.reviews),
                            label_status="Off-label" if r.off_label else "On-label"))
        for view, conds in VIEWS.items():
            sub = grp[grp.index.isin(conds)]
            if sub.empty:
                continue
            out.append(dict(common, condition=view, rating=wavg(sub.rating, sub.reviews),
                            reviews=int(sub.reviews.sum()),
                            label_status="Off-label" if sub.off_label.all() else "On-label"))
    df = pd.DataFrame(out)
    df["rating"] = df.rating.map(lambda x: "" if x is None or pd.isna(x) else f"{x:.1f}")
    cols = ["generic_name", "condition", "brand_names", "drug_class", "class_group", "rating", "reviews",
            "rx_otc", "label_status", "new_approval", "conditions_listed", "pregnancy_cat",
            "csa_schedule", "alcohol_interaction"]
    df = df[cols].sort_values(["condition", "reviews"], ascending=[True, False])
    df.to_csv(DATA / "drugscom_ratings_long.csv", index=False, lineterminator="\n")
    print(lst.groupby("condition").size().to_dict(), "listings ->",
          df.groupby("condition").size().to_dict(), "drug rows")
