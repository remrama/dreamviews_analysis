"""
save out 2 csvs
1 for top categories
1 for top tags
Categories are more useful bc they are constrained by the DreamViews site.
Tags are a free-for-all so lots of misspellings etc.
"""
import os
import pandas as pd
import config as c


# export filename changes over 2 loop iterations so see below

N_MIN_LABELS = 10
N_MIN_USERS = 10 # per label

df = c.load_dreamviews_posts()

for col in ["tags", "categories"]:

    # tag and category columns are strings with double colons separating labels
    # convert them to lists
    df[col] = df[col].str.split("::")
    
    # generate a new axis name
    singular = "tag" if col == "tags" else "category"
    
    # explode each list so each row is one label
    labels = df.explode(col).dropna(subset=[col])

    # get a count for each label (tag or category)
    label_counts = labels[col].value_counts(
        ).rename("n_posts").rename_axis(singular)

    # get a count of how many unique users there are for each label
    user_counts = labels.groupby(col
        ).user_id.nunique(
        ).rename("n_users").rename_axis(singular)

    # merge into one dataframe that accounts for both total and user frequency
    res = pd.concat([label_counts, user_counts], axis=1, join="inner")

    # drop really low counts from the table entirely
    res = res[ res["n_posts"] >= N_MIN_LABELS ]
    res = res[ res["n_users"] >= N_MIN_LABELS ]

    res = res.sort_values("n_posts", ascending=False)

    # export
    export_fname = os.path.join(c.DATA_DIR, "derivatives", f"describe-top{col}.tsv")
    res.to_csv(export_fname, sep="\t", encoding="utf-8", index=True)
