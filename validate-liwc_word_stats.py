"""Analyze word-level LIWC scores between lucid and non-lucid dreams.
***Note this does not re-run LIWC, but loads in prior results.

IMPORTS
=======
    - original post info,     dreamviews-posts.tsv
    - word-level LIWC scores, validate-liwc_wordscores.tsv
    - LIWC dictionary,        dictionaries/custom.dic
EXPORTS
=======
    - effect sizes (d) for top words from each category, validate-liwc_wordscores-stats.tsv


Some of this is copy/pasted from the general liwc_stats script,
but this is way messier so better alone.
1. only a subset
2. need to load in numpy stuff
3. need to look up vocabs in whole lexicon for subsetting
4. don't need all the summary statistic details
5. don't want to run both stats on this, too out of hand just pick one
6. export is different, here it's the top N words of a few categories and their effect sizes
"""
import liwc
import numpy as np
import pandas as pd
import pingouin as pg
from scipy import sparse
import tqdm

import config as c


################################################################################
# SETUP
################################################################################

LIWC_CATEGORIES = ["insight", "agency"]
top_n = 20  # Top n contributing tokens/words for each category.

import_path_dict = c.DATA_DIR / "dictionaries" / "custom.dic"
import_path_data = c.DATA_DIR / "derivatives" / "validate-liwc_wordscores-data.npz"
import_path_attr = c.DATA_DIR / "derivatives" / "validate-liwc_wordscores-attr.npz"
export_path = c.DATA_DIR / "derivatives" / "validate-liwc_wordscores-stats.tsv"

#### load in the original posts file to get attributes lucidity and user_id
# and drop un-labeled posts.
# merge the clean data file and all its attributes with the liwc results
posts = c.load_dreamviews_posts()
posts = posts.set_index("post_id")[["user_id", "lucidity"]]
posts = posts[ posts["lucidity"].str.contains("lucid") ]

# #### load prior full LIWC results (i.e., category results)
# liwccats = pd.read_csv(import_fname_liwc, sep="\t", encoding="utf-8",
#     index_col="category", usecols=["category", "cohen-d"], squeeze=True)
# liwccats = liwccats.loc[LIWC_CATEGORIES]

#### load in dictionary lexicon
# and flip key/value from token/category to category/word_list
# and only for the liwc categories of interest
lexicon, _ = liwc.read_dic(import_fname_dict)
wordlists = { c: [ t for t, cats in lexicon.items() if c in cats ]
    for c in LIWC_CATEGORIES }
# and grab a subset of all the vocab so to reduce unnecessary memory later
vocab = set([ t for wlist in wordlists.values() for t in wlist ])

#### load in numpy arrays of token scores and generate dataframe
sparse_matr_attributes = np.load(import_fname_attr, allow_pickle=True)
tokens = sparse_matr_attributes["token"]
token_index = [ t in vocab for t in tokens ]
relevant_tokens = tokens[token_index]
sparse_matr = sparse.load_npz(import_fname_data)
scores = pd.DataFrame(sparse_matr[:,token_index].toarray(),
    columns=relevant_tokens,
    index=sparse_matr_attributes["post_id"])

# merge the post attributes with LIWC token scores
df = posts.join(scores, how="left")
assert len(df) == len(posts)


################################################################################
# STATISTICAL TESTS
################################################################################

# Average the LD and NLD scores of each token for each user.
# Some users might not have both dream types and they'll be removed.
avgs = df.groupby(["user_id", "lucidity"]
    ).mean().rename_axis(columns="token"
    ).pivot_table(index="user_id", columns="lucidity"
    ).dropna()

# We already have only relevant tokens, so get effect
# sizes for all of them.
effectsize_results = []
for tok in tqdm.tqdm(relevant_tokens, desc="stats on word-level LIWC scores"):
    ld, nld = avgs[tok][["lucid", "nonlucid"]].T.values
    stats = {}
    stats["cohen-d"] = pg.compute_effsize(ld, nld, paired=True, eftype="cohen")
    stats["cohen-d_lo"], stats["cohen-d_hi"] = pg.compute_bootci(ld, nld,
        paired=True, func="cohen", method="cper",
        confidence=.95, n_boot=2000, decimals=4)
    effectsize_results.append(pd.DataFrame(stats, index=[tok]))

es_df = pd.concat(effectsize_results).rename_axis("token")


# Each LIWC category will utilize a different set of tokens/words.
# Find the top N contributors to the overall effect.
# Find the direction of overall effect by looking at previous LIWC category output.
token_rank_results = []
for cat in LIWC_CATEGORIES:
    # generate an index of relevant tokens for this category
    cat_index = es_df.index.map(lambda t: t in wordlists[cat])
    # extract only rows in this category
    df_ = es_df.loc[cat_index]
    # # get direction of effect and remove rows not in line
    # d_sign = np.sign(liwccats.loc[cat])
    # if d_sign > 0:
    #     df_ = df_[ df_["cohen-d"] > 0 ]
    # else:
    #     df_ = df_[ df_["cohen-d"] < 0 ]
    # sort by effect size
    df_ = df_.sort_values("cohen-d", ascending=False, key=abs)
    # take top rows and clean up a bit
    df_ = df_[:TOP_N]
    df_[f"{cat}_rank"] = np.arange(TOP_N) + 1
    token_rank_results.append(df_)


out = pd.concat(token_rank_results)

# Export.
out.to_csv(export_path, float_format="%.4f", index=True, na_rep="NA", sep="\t", encoding="utf-8")
