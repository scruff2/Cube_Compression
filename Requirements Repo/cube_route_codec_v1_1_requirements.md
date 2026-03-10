# CODEX 5.4 Change Request
## Cube Route Codec v1.1
### Diagnostic-Focused Iteration

## Objective

The v1.0 prototype is operational and lossless, but the first benchmark did **not** validate the geometric route idea against the most relevant baseline.

Observed outcome from the first benchmark:
- cube codec achieved full route coverage and exact reconstruction
- flat phrase dictionary baseline dramatically outperformed the cube codec
- likely cause: route descriptors are too expensive relative to phrase ids, and the test corpus is too small and too exact-match friendly for region geometry to show an advantage

The purpose of v1.1 is **not** to add complexity broadly.
The purpose is to answer, with high diagnostic value:

> Can the cube and region structure outperform a flat phrase dictionary on corpora containing structured phrase families with shared prefixes, middles, and controlled variants?

---

## Top-level requirements

v1.1 shall focus on four things only:

1. **Explain where route cost comes from**
2. **Create more diagnostic source corpora**
3. **Add fairer and more informative baselines**
4. **Test whether structured overlap helps the cube design**

Do not broaden scope beyond this.

---

# 1) Required new diagnostics

## 1.1 Token cost breakdown report

Add detailed reporting for cube-route token cost.

For every benchmark run, report:

- route token count
- literal token count
- average emitted bits per route token
- average estimated route token cost
- average estimated literal token cost
- per-field route cost breakdown:
  - region id bits
  - middle id bits
  - suffix id bits
  - token type overhead bits
  - optional length field bits
- effective cost per emitted source bit for:
  - route tokens only
  - literal tokens only
  - overall stream

Also report:
- number of unique route descriptors used
- frequency distribution of route usage
- top 10 most-used route descriptors

This is mandatory.

## 1.2 Flat dictionary baseline breakdown

For the flat phrase dictionary baseline, report:

- dictionary size
- phrase id width or average phrase id code length
- literal usage fraction
- average phrase length covered
- average code length per covered phrase
- number of unique dictionary entries used
- top 10 most-used dictionary entries

This is mandatory.

## 1.3 Comparative structural efficiency report

For every benchmark, produce a section that compares:

- cube route average descriptor bits per covered phrase
- flat dictionary average descriptor bits per covered phrase
- savings gap between them

The report shall explicitly say whether the cube is paying more than the flat dictionary because of:
- route field overhead
- low region reuse
- low branch reuse
- too many unique route descriptors
- poor clustering structure

---

# 2) Required synthetic corpus generator

Add a corpus-generation module and CLI command to create controlled experimental data.

Command example:

```bash
python -m cube_codec.cli generate-corpus --mode <mode> --output-dir <dir> --config <config>
```

Support at least these modes.

## 2.1 Exact-repeat mode

Generate corpora from repeated exact fixed-length phrases.

Purpose:
- should favor flat dictionary strongly
- used as a control

## 2.2 Prefix-variant mode

Generate phrases with:
- long common prefix
- several middle variants
- several suffix variants

Purpose:
- should favor cube region trunk-and-branch design

## 2.3 Middle-variant mode

Generate phrases with:
- common prefix
- highly variable middle
- common suffix

Purpose:
- test whether current region layout helps or needs redesign

## 2.4 Family-mixture mode

Generate corpora consisting of several phrase families with different frequencies.

Purpose:
- test region allocation and reuse

## 2.5 Shifted-overlap mode

Generate corpora where useful repeated structure exists but is not always aligned to the phrase stride.

Purpose:
- test whether stride and extraction assumptions are hiding recoverable structure

Each mode shall support:
- phrase length
- number of families
- family frequencies
- number of variants
- train/test split generation
- deterministic random seed

---

# 3) Required benchmark matrix support

Add a CLI or script to run a small benchmark matrix automatically.

Command example:

```bash
python -m cube_codec.cli benchmark-matrix --config <config> --train <train> --test <test> --sweep <json>
```

Initial supported sweep dimensions:
- phrase length
- extraction stride
- max regions
- max middle variants
- max suffix variants
- literal block size

Do not add more sweep dimensions in v1.1.

The benchmark matrix output shall include:
- per-run JSON metrics
- one markdown summary table
- one CSV summary file

---

# 4) Required training and data diagnostics

## 4.1 Phrase extraction diagnostics

Report:
- total extracted phrases
- unique extracted phrases
- selected phrases
- phrase frequency histogram
- coverage of selected phrases over train corpus

## 4.2 Cluster quality diagnostics

For each region or cluster, report:
- cluster size
- common prefix length
- number of middle variants
- number of suffix variants
- average intra-cluster similarity
- total source mass assigned to the cluster

## 4.3 Region utilization diagnostics

During encoding, report:
- regions built
- regions actually used
- per-region usage counts
- per-region emitted bits
- per-region average route cost

This is essential. If many regions are built but only a few are used, that needs to be obvious.

---

# 5) Required new baselines

Add two additional comparison baselines.

## 5.1 Family-aware explicit dictionary baseline

Implement a baseline that explicitly stores phrase families in structured form:
- shared prefix
- variant ids
- suffix ids

This is important because the current flat phrase dictionary baseline may already be close to the real optimum for the present corpus. We need a baseline that captures structured overlap explicitly without using the cube.

Purpose:
- test whether the 3D cube adds value beyond a non-geometric structured phrase model

## 5.2 Phrase-family oracle baseline

Add an analysis-only baseline, not necessarily a full codec, that computes the idealized cost if a phrase family could be represented by:
- family id
- middle id
- suffix id

without extra cube routing overhead.

Purpose:
- estimate the headroom available to the cube design

This can be approximate, but it must be clearly labeled as an oracle or analysis baseline.

---

# 6) Required experiments for v1.1

v1.1 shall include a scripted experiment suite that runs at least:

## Experiment A: exact-repeat control
Expectation:
- flat dictionary should dominate
- cube probably loses

## Experiment B: prefix-variant synthetic corpus
Expectation:
- cube should become more competitive
- if it still loses badly, region geometry is not buying enough

## Experiment C: family-mixture synthetic corpus
Expectation:
- test whether region partitioning and route reuse help

## Experiment D: shifted-overlap synthetic corpus
Expectation:
- identify whether stride is currently suppressing useful structure

## Experiment E: real narrow corpus rerun
Use the original small train/test pair and at least one somewhat larger pair.

Expectation:
- compare v1.1 diagnostic output against v1.0 conclusions

---

# 7) Required implementation restraint

Do **not** implement the following in v1.1:
- arithmetic coding
- neural models
- arbitrary 3D path walks
- cross-region continuation logic
- adaptive online cube mutation
- complicated multi-token optimizers
- production performance tuning

These are intentionally excluded.

The purpose of v1.1 is diagnosis, not sophistication.

---

# 8) Allowed small design changes

The following narrow changes are allowed if needed for diagnosis:

## 8.1 Overlapping extraction stride

Allow stride smaller than phrase length.

## 8.2 Variable common-prefix detection

Improve cluster formation if it remains simple and interpretable.

## 8.3 Optional route field packing tweaks

If route cost accounting is currently pessimistic or awkward, you may clean it up, but preserve transparent reporting.

## 8.4 Optional simple entropy estimate mode

You may add an **analysis-only estimated entropy mode** that estimates how much route cost would drop under ideal entropy coding, but do not implement a full entropy-coded stream yet.

If added, it must be clearly marked as an estimate, not an actual compressed stream result.

---

# 9) Required outputs

For every benchmark run, produce:

1. `metrics.json`
2. `metrics.md`
3. `diagnostics.json`
4. `diagnostics.md`

Where diagnostics include:
- cost breakdowns
- cluster summaries
- region utilization
- baseline comparisons
- interpretation notes

For benchmark matrix runs, also produce:
- `summary.csv`
- `summary.md`

---

# 10) Required interpretation section

Every markdown benchmark report shall end with an automatically generated interpretation section that answers:

1. Did the cube beat raw literals?
2. Did the cube beat the flat dictionary baseline?
3. Did the cube beat the family-aware structured baseline?
4. Was route coverage high enough?
5. Was route cost too high?
6. Were enough regions meaningfully used?
7. Is the result encouraging, discouraging, or inconclusive for the geometric hypothesis?

This is required so each run is immediately intelligible.

---

# 11) Required success criteria for v1.1

v1.1 is successful if it produces **clear evidence**, one way or the other.

Success does **not** require the cube to win overall.

v1.1 is successful if it can answer at least one of these questions clearly:

- On exact-repeat corpora, flat dictionary dominates and the report explains why.
- On structured prefix and suffix family corpora, the cube becomes competitive or wins, showing that geometry helps in its intended niche.
- Or, if the cube still loses there, the report makes clear that the current region design does not provide enough advantage over explicit structured dictionaries.

That is the decision point.

---

# 12) Code quality priority

Prioritize:
1. clarity
2. determinism
3. observability
4. fairness of comparison

Do not prioritize cleverness or extra features.

The value of v1.1 is in producing trustworthy evidence.

---

# 13) Deliverables

v1.1 shall include:
- updated code
- updated tests
- new synthetic corpus generator
- new baselines
- new diagnostic reports
- updated README with v1.1 experiment instructions
- at least one ready-to-run benchmark matrix example

---

## Short cover note

Please implement v1.1 as a diagnostic-focused iteration. Do not broaden scope. The goal is to determine whether the cube and route structure provides any real advantage over explicit phrase dictionaries on structured phrase-family corpora. Prioritize cost breakdowns, fair baselines, synthetic corpus generation, and interpretable benchmark reporting over new compression features.
