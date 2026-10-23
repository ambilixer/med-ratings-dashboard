"""Drug metadata: brand -> generic map, drug classes and class groups.

Classes and groups are this project's own annotation (drafted with AI assistance), not Drugs.com's.
Run from anywhere: python scripts/make_meta.py  ->  data/drug_meta.json
"""
import json
from pathlib import Path

brand_to_generic = {
 "Cymbalta":"duloxetine","Irenka":"duloxetine","Lexapro":"escitalopram","Zoloft":"sertraline",
 "Wellbutrin XL":"bupropion","Wellbutrin SR":"bupropion","Forfivo XL":"bupropion","Budeprion SR":"bupropion","Aplenzin":"bupropion",
 "Prozac":"fluoxetine","Celexa":"citalopram","Rexulti":"brexpiprazole","Abilify":"aripiprazole",
 "Effexor XR":"venlafaxine","Effexor":"venlafaxine","Pristiq":"desvenlafaxine","Paxil":"paroxetine","Paxil CR":"paroxetine",
 "Remeron":"mirtazapine","Remeron SolTab":"mirtazapine","Viibryd":"vilazodone","Seroquel XR":"quetiapine",
 "Deplin":"l-methylfolate","XaQuil XR":"l-methylfolate","L-Methylfolate Forte":"l-methylfolate",
 "Zyprexa":"olanzapine","Zyprexa Zydis":"olanzapine","Raldesy":"trazodone","Fetzima":"levomilnacipran",
 "Methylin ER":"methylphenidate","Norpramin":"desipramine","Nardil":"phenelzine","Parnate":"tranylcypromine",
 "Symbyax":"fluoxetine / olanzapine","Emsam":"selegiline","Pamelor":"nortriptyline","Marplan":"isocarboxazid",
 "Spravato":"esketamine","Tofranil":"imipramine",
 # Major Depressive Disorder page
 "Trintellix":"vortioxetine","Auvelity":"bupropion / dextromethorphan","Caplyta":"lumateperone",
 "Vraylar":"cariprazine","Opipza":"aripiprazole","Exxua":"gepirone",
 # Bipolar Disorder page
 "Lamictal":"lamotrigine","Lamictal ODT":"lamotrigine","Lamictal CD":"lamotrigine","Lamlique":"lamotrigine","Subvenite":"lamotrigine",
 "Seroquel":"quetiapine","Abilify Maintena":"aripiprazole","Abilify Asimtufii":"aripiprazole",
 "Lybalvi":"olanzapine / samidorphan","Latuda":"lurasidone","Fanapt":"iloperidone","Bysanti":"milsaperidone",
 "Depakote":"divalproex sodium","Depakote ER":"divalproex sodium","Risperdal":"risperidone","Risperdal Consta":"risperidone",
 "Rykindo":"risperidone","Uzedy":"risperidone","Geodon":"ziprasidone","Saphris":"asenapine","Equetro":"carbamazepine",
 "Lithobid":"lithium",
}
classes = {
 "SSRI":["sertraline","fluoxetine","citalopram","escitalopram","paroxetine","fluvoxamine"],
 "SNRI":["venlafaxine","desvenlafaxine","duloxetine","levomilnacipran"],
 "NDRI":["bupropion"],
 "Serotonin modulator":["trazodone","nefazodone","vilazodone","vortioxetine","gepirone"],
 "Tetracyclic (NaSSA)":["mirtazapine"],
 "TCA":["amitriptyline","nortriptyline","desipramine","doxepin","imipramine","clomipramine","protriptyline","trimipramine","amoxapine"],
 "MAOI":["phenelzine","tranylcypromine","isocarboxazid","selegiline"],
 "NMDA antagonist":["ketamine","esketamine","bupropion / dextromethorphan"],
 "Antidepressant combination":["fluoxetine / olanzapine","amitriptyline / chlordiazepoxide","amitriptyline / perphenazine"],
 "Atypical antipsychotic":["brexpiprazole","aripiprazole","quetiapine","olanzapine","risperidone","paliperidone","cariprazine",
                           "lumateperone","lurasidone","ziprasidone","asenapine","iloperidone","milsaperidone","olanzapine / samidorphan"],
 "Typical antipsychotic":["perphenazine"],
 "Mood stabilizer":["lithium","lamotrigine","divalproex sodium","valproic acid","carbamazepine"],
 "Other anticonvulsant":["gabapentin","oxcarbazepine","topiramate","levetiracetam","tiagabine"],
 "Stimulant / wakefulness / ADHD":["methylphenidate","lisdexamfetamine","modafinil","armodafinil","atomoxetine"],
 "Benzodiazepine":["alprazolam","clonazepam"],
 "Thyroid hormone":["thyroid desiccated"],
 "Opioid":["tramadol"],
 "Blood pressure medicine":["clonidine","verapamil"],
 "Vitamin / medical food":["l-methylfolate","niacin"],
 "Herbal":["st. john's wort","gotu kola","valerian"],
}
# Condition-neutral groups (bipolar data made "adjunct" a depression-only framing)
groups = {
 "Antidepressant":["SSRI","SNRI","NDRI","Serotonin modulator","Tetracyclic (NaSSA)","TCA","MAOI","NMDA antagonist","Antidepressant combination"],
 "Antipsychotic":["Atypical antipsychotic","Typical antipsychotic"],
 "Mood stabilizer / anticonvulsant":["Mood stabilizer","Other anticonvulsant"],
 "Other prescription":["Stimulant / wakefulness / ADHD","Benzodiazepine","Thyroid hormone","Opioid","Blood pressure medicine"],
 "Supplement":["Vitamin / medical food","Herbal"],
}
group_of = {c:g for g,cs in groups.items() for c in cs}
drug_class = {d:c for c,ds in classes.items() for d in ds}
assert len(drug_class) == sum(len(v) for v in classes.values()), "a drug is in two classes"
class_group = {d:group_of[c] for d,c in drug_class.items()}
other_brands = {
 "bupropion":["Wellbutrin","Zyban"],"duloxetine":["Drizalma Sprinkle"],"fluoxetine":["Sarafem"],
 "desvenlafaxine":["Khedezla"],"armodafinil":["Nuvigil"],"trazodone":["Desyrel","Oleptro"],
 "amitriptyline":["Elavil"],"lamotrigine":["Lamictal XR"],"paroxetine":["Pexeva"],"alprazolam":["Xanax"],
 "tramadol":["Ultram"],"methylphenidate":["Ritalin","Concerta"],
 "nefazodone":["Serzone"],"nortriptyline":["Aventyl"],
 "modafinil":["Provigil"],"doxepin":["Sinequan"],"fluvoxamine":["Luvox"],"niacin":["Niaspan"],
 "amitriptyline / chlordiazepoxide":["Limbitrol"],"amoxapine":["Asendin"],"ketamine":["Ketalar"],
 "lisdexamfetamine":["Vyvanse"],"atomoxetine":["Strattera"],"clomipramine":["Anafranil"],
 "imipramine":["Tofranil-PM"],"amitriptyline / perphenazine":["Etrafon","Triavil"],"paliperidone":["Invega"],
 "protriptyline":["Vivactil"],"selegiline":["Eldepryl","Zelapar"],"thyroid desiccated":["Armour Thyroid","NP Thyroid"],
 "trimipramine":["Surmontil"],
 "valproic acid":["Depakene"],"carbamazepine":["Tegretol","Carbatrol"],"gabapentin":["Neurontin","Gralise"],
 "oxcarbazepine":["Trileptal","Oxtellar XR"],"topiramate":["Topamax","Trokendi XR","Qudexy XR"],
 "levetiracetam":["Keppra"],"tiagabine":["Gabitril"],"clonazepam":["Klonopin"],"clonidine":["Catapres","Kapvay"],
 "verapamil":["Calan","Verelan"],"perphenazine":["Trilafon"],
}
json.dump(dict(brand_to_generic=brand_to_generic,drug_class=drug_class,class_group=class_group,
               groups=list(groups),other_brands=other_brands),
          open(Path(__file__).resolve().parent.parent / "data" / "drug_meta.json", "w", encoding="utf-8"),indent=1)
