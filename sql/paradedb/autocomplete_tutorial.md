# Autocomplete Tutorial

In user-facing search, autocomplete refers to the process of suggesting relevant results as the user is typing.
Several of ParadeDB’s search APIs can be mixed and matched to build a full-fledged autocomplete experience.

For testing purposes, we will use the mock_item table:
```sql
CALL paradedb.create_bm25_test_table(
  schema_name => 'public',
  table_name => 'mock_items'
);
```

## 1. Fuzzy Term

Suppose we want to find all documents containing shoes, but the user typed in shoez.
The fuzzy_term query can find search results that approximately match the query term while allowing for minor typos in the input.

```sql
SELECT description, rating, category
FROM search_idx.search(
    query => paradedb.fuzzy_term(
        field => 'description',
        value => 'shoez'
    )
);
```

output:
```
     description     | rating | category
---------------------+--------+----------
 Sleek running shoes |      5 | Footwear
 White jogging shoes |      3 | Footwear
 Generic shoes       |      4 | Footwear
(3 rows)
```

## 2. Fuzzy Phrase

Suppose the user provides a misspelled phrase like ruining shoez when searching for running shoes.
Because fuzzy_term treats value as a single token, passing the entire phrase to fuzzy_term will not yield any matches.
Instead, fuzzy_phrase should be used. fuzzy_phrase finds documents where any of the query’s tokens are a fuzzy_term match.

```sql
SELECT description, rating, category
FROM search_idx.search(
    query => paradedb.fuzzy_phrase(
        field => 'description',
        value => 'ruining shoez'
    )
);
```
output:
```
     description     | rating | category
---------------------+--------+----------
 Sleek running shoes |      5 | Footwear
 White jogging shoes |      3 | Footwear
 Generic shoes       |      4 | Footwear
(3 rows)
```

For a stricter result set, fuzzy_phrase can be configured to match documents if all query tokens match:
```sql
SELECT description, rating, category
FROM search_idx.search(
    query => paradedb.fuzzy_phrase(
        field => 'description',
        value => 'ruining shoez',
        match_all_terms => true
    )
);
```
output:
```
     description     | rating | category
---------------------+--------+----------
 Sleek running shoes |      5 | Footwear
(1 row)
```

## 3. Multiple Fuzzy Terms

Suppose we want to compare a query against both description and category. The boolean query can be used to query across multiple fields:
```sql
SELECT description, rating, category
FROM search_idx.search(
    query => paradedb.boolean(
        should => ARRAY[
            paradedb.fuzzy_phrase(field => 'description', value => 'ruining shoez'),
            paradedb.fuzzy_phrase(field => 'category', value => 'ruining shoez')
        ]
    )
);
```
output:
```
     description     | rating | category
---------------------+--------+----------
 Sleek running shoes |      5 | Footwear
 White jogging shoes |      3 | Footwear
 Generic shoes       |      4 | Footwear
(3 rows)
```

## 4. Ngram Term

Suppose we want to suggest results when the user has only typed part of a word, like sho.
In this scenario, the ngrams tokenizer can be used to convert documents into ngram tokens.

For the purpose of this example, let’s assume that we have an index called ngrams_idx, and search with partial word (sho):
```sql
-- Create an index with ngram tokenizer
CALL paradedb.create_bm25(
    index_name => 'ngrams_idx',
    schema_name => 'public',
    table_name => 'mock_items',
    key_field => 'id',
    text_fields => paradedb.field(
        'description',
        tokenizer => paradedb.tokenizer('ngram', min_gram => 3, max_gram => 3, prefix_only => false)
    )
);

-- partial word search
SELECT description, rating, category
FROM ngrams_idx.search('description:sho');
```
output:
```
     description     | rating | category
---------------------+--------+----------
 Sleek running shoes |      5 | Footwear
 White jogging shoes |      3 | Footwear
 Generic shoes       |      4 | Footwear
(3 rows)
```

## 5. Ngram Term Set

When querying against an ngrams field, all ngrams of the query must match in order for the document to be considered a match.
This means that a query like hsoes does not match shoes, because the hso token does not match any of the tokens of shoes.

To match documents where any ngram token of the query matches, the fuzzy_phrase query can again be used.
Since we are looking for exact ngram matches, the distance parameter can be lowered to 0.

```sql
SELECT description, rating, category
FROM ngrams_idx.search(
    query => paradedb.fuzzy_phrase(
        field => 'description',
        value => 'hsoes',
        distance => 0
    )
);
```
output:
```
     description     | rating | category
---------------------+--------+----------
 Sleek running shoes |      5 | Footwear
 White jogging shoes |      3 | Footwear
 Generic shoes       |      4 | Footwear
(3 rows)
```
