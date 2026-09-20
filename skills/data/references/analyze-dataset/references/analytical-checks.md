# Checks that can change the answer

Use only the sections relevant to the analysis. A descriptive summary does not require a modeling pipeline or significance test.

## Joins and population coverage

Write the expected relationship before joining: one-to-one, many-to-one, or an intentional expansion. In pandas, use `merge(..., validate="many_to_one", indicator=True)` for a fact-to-dimension enrichment, replacing the cardinality with the actual contract. Reconcile unmatched keys and input/output totals before interpreting segments. pandas matches null merge keys to each other, unlike ordinary SQL equality joins; decide whether to exclude or separately classify unknown keys. See [pandas merge semantics](https://pandas.pydata.org/docs/reference/api/pandas.merge.html).

Example: ten orders joined to two historical customer rows each produce twenty rows. Removing duplicates after summing cannot restore the order total. Select the dimension version valid at each order's timestamp or aggregate at the intended grain before joining.

## Rates and comparisons

Keep numerator and eligible denominator together through aggregation. If group A has 1 success out of 2 trials and group B has 90 out of 100, the overall rate is 91/102, not the average of 50% and 90%. Conversely, equal weighting may be the intended answer to an average-group question; name the estimand rather than silently choosing weights.

State whether a partial latest period is comparable to complete earlier periods. Check composition shifts before attributing an aggregate trend to within-group changes. Preserve excluded/missing observations in the population accounting; absence from a table does not necessarily mean no event.

## Prediction and uncertainty

When comparing predictive models, split before fitting imputation, scaling, feature selection, or tuning. Fit preprocessing on training folds and apply it to held-out data; a pipeline helps keep this boundary intact. See [scikit-learn on leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

Choose time or entity separation when the intended prediction concerns future events or unseen entities. Repeated measurements from the same person are not automatically independent observations. Match resampling and uncertainty estimates to the sampling unit, and describe exploratory comparisons as exploratory rather than retroactively presenting them as prespecified tests.
