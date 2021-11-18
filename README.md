# dreamviews_ds

Turning the public [DreamViews Dream Journal](https://www.dreamviews.com/blogs/) into a usable dataset. There's lots of descriptive output and such, but the final dataset, to be used for other projects and such, can be found [here](https://media.giphy.com/media/St0Nd0Qt4WNMLy29vi/giphy.gif).

### Part 1 - Data collection and cleaning
The first thing we do is grab all the data and tidy it up a bit (without being very invasive or restrictive).
1. **collect**/scrape the DreamViews journal and relevant public profiles
2. **convert** the html files to tsv, super minimal cleaning just to prevent errors
3. **clean** the raw tsv data a bit for final/usable post and user files
4. export plots and summary statistics describing the dataset
5. minor validation steps (e.g., lucid vs non-lucid word clouds)

### Part 2 - Manual annotations and validation
We also manually clean and annotate a subset of the dataset. This subset can be used for further validation, finer-grained analyses, and development of algorithms for automated detection of lucidity. See our custom [Dream Report Annotation Manual](https://d-re-a-m.readthedocs.io/) for annotation details.
1. extract a principled subset of the data
2. upload the data to tagtog for annotating
3. download and convert the tagtog data
4. visualize and analyze interrater reliability for annotations
5. minor results from annotations (e.g., temporal moment of lucidity)
6. validate user-defined lucidity against experimenter-defined lucidity
7. develop a classifier that can be used to determine lucid from non-lucid dreams and apply to the rest of the dataset (with probabilities saved out on final dataset)


## Linear code layout

See `config.py` for directory info and other configuration stuff.

Run `init_data_directory_structure.py` before anything else, after manually setting the `DATA_DIR` in `config.py` to match your desired data output location.

### Collect, convert, and clean data

```bash
# collect raw dream journal posts as html files
# (note we also get raw user html files, but we need to convert the
#  raw posts first because we grab only the users who contribute posts)
python collect-posts.py     # ==> DATA_DIR/source/dreamviews-posts.zip
```

Need to jump out and insert the timestamp of day data was collected in the `config.py` file. This is mildly annoying, but the most recent blog/journal posts are stamped as coming from "today" or "yesterday", so those need a reference. Should be a `YYYY-MM-DD` string.

```bash
# convert raw dream journal posts to minimally-cleaned text files
python convert-posts.py     # ==> DATA_DIR/derivatives/posts-raw.tsv
                            # ==> DATA_DIR/derivatives/users-anon_key.json

# now, with the usernames generated, we can collect relevant user profiles
python collect-users.py     # ==> DATA_DIR/source/dreamviews-users.zip

# convert the users too, and clean them as well
python convert-users.py     # ==> DATA_DIR/derivatives/users-raw.csv
python clean-users.py       # ==> DATA_DIR/derivatives/users-clean.csv

# clean the dream journal posts, exporting a tsv and also a folder of text files
python clean-posts.py       # ==> DATA_DIR/derivatives/posts-clean.tsv
python tsv2txt-posts.py     # ==> DATA_DIR/derivatives/posts/<post_id>.txt
```


### Describe data

```bash
# frequency of posts over time
python describe-timecourse.py       # ==> DATA_DIR/results/describe-timecourse.png/eps

# lucid/non-lucid/nightmare overlap
python describe-labeloverlap1.py    # ==> DATA_DIR/results/describe-labeloverlap1.png/eps
                                    # ==> DATA_DIR/results/describe-labeloverlap1.tsv

# number of participants with both lucid and non-lucid posts
python describe-labeloverlap2.py    # ==> DATA_DIR/results/describe-labeloverlap2.png/eps
                                    # ==> DATA_DIR/results/describe-labeloverlap2.tsv

# reported gender and age
python describe-demographics1.py    # ==> DATA_DIR/results/describe-demographics1.png/eps
                                    # ==> DATA_DIR/results/describe-demographics1.tsv

# reported location/country
python describe-demographics2.py    # ==> DATA_DIR/results/describe-demographics2.png/eps
                                    # ==> DATA_DIR/results/describe-demographics2.tsv

# post length before and after preprocessing (for word and token counts)


# number of dreams per user

# top categories and labels

# word clouds of lucid/non-lucid/nightmares

```