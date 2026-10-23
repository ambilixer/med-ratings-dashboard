# Methodology

## Scope

The data covers three Drugs.com condition pages: Depression, Major Depressive Disorder and Bipolar Disorder. Other depression subtypes (postpartum, persistent depressive disorder and so on) are deliberately left out. Drugs.com's Bipolar Disorder category covers bipolar disorder as a whole, not only its depressive episodes.

No drugs or rows are dropped. Drugs with no reviews yet stay in the table, and the dashboard's filters handle the rest.

## Brand and generic listings

Drugs.com lists generics and brands separately, but **a generic's listing already includes the reviews of its brand-name versions**. Sertraline's count, for example, includes Zoloft's. So each drug's rating and review count come from its generic listing alone, and brand listings are never added on top, which would double-count. The parser checks that no brand's count is larger than its generic's.

## Combining conditions

Each review is filed under one condition, so the condition pages are separate pools of reviews. (Checked against sertraline's per-condition breakdown on Drugs.com: Depression 1,296, Major Depressive Disorder 240, Bipolar Disorder 55, which match the copied pages.) A combined view therefore:

- adds the review counts, and
- averages the ratings weighted by review count.

Drugs.com rounds ratings to one decimal, so a combined rating can differ from an exact recount by about 0.05.

Views:

- **Major depression** = Depression + Major Depressive Disorder
- **Bipolar disorder** = Bipolar Disorder
- **Total** = all three

## Adjusted rating

A drug with five glowing reviews shouldn't outrank one with a thousand good ones. The adjusted rating is a simple Bayesian average. It treats every drug as if it also had 25 reviews at the view's average rating:

```
adjusted = (n × rating + 25 × view_average) / (n + 25)
```

`n` is the drug's review count, and `view_average` is the review-weighted mean of all rated drugs in that view. A drug with a handful of reviews moves most of the way toward the average, while one with hundreds barely moves. The dashboard computes this in the page (see the `adjusted` calculation in `dashboard/page.html`).

Class averages in the "Ratings by drug class" chart are review-weighted too.

## Drug classes

Drug class and group are this project's own annotation, drafted with AI assistance, not taken from Drugs.com. Groups are condition-neutral. Calls worth knowing about:

- amoxapine: TCA
- mirtazapine: tetracyclic (NaSSA)
- trazodone, nefazodone, vilazodone, vortioxetine, gepirone: serotonin modulator
- selegiline: MAOI
- bupropion / dextromethorphan (Auvelity), ketamine, esketamine: NMDA antagonist
- lithium, lamotrigine, divalproex sodium, valproic acid, carbamazepine: mood stabilizer
- gabapentin, oxcarbazepine, topiramate, levetiracetam, tiagabine: other anticonvulsant
- clonidine, verapamil: blood pressure medicine

Corrections are welcome; they live in `scripts/make_meta.py`.

## Off-label

Off-label follows Drugs.com's flag for that condition. In a combined view, a drug counts as off-label only if it is off-label for every condition included.

## Caveats

- Reviews are self-selected and lean toward strong reactions. With antidepressants, that often means early side-effect complaints. Treat ratings as patient sentiment, not efficacy.
- Controlled substances (tramadol, benzodiazepines, stimulants) rate highest. That may reflect how they feel to take as much as how well they treat the condition.
- Review counts are heavily skewed, so the dashboard uses a log scale for counts by default.
- Ratings are a snapshot from October 2026 and will drift as new reviews arrive.
