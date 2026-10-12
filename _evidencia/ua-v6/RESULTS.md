# ua_length audit (v6) — train / val / train+val

Source: training/splits/train.parquet, training/splits/val.parquet (columns label, ua_length, ua_present). test.parquet NOT opened.
Long UA = ua_length > 40. Present = ua_present > 0. CI = Wilson 95 %.

| Partition | Class | n | ua>40 | % | Wilson 95 % | ua_present>0 | % present |
|---|---|---:|---:|---:|---|---:|---:|
| train | benign | 69472 | 251 | 0.36 | [0.32, 0.41] | 339 | 0.49 |
| train | sqli | 159154 | 130016 | 81.69 | [81.50, 81.88] | 130172 | 81.79 |
| train | xss | 20962 | 6970 | 33.25 | [32.62, 33.89] | 7075 | 33.75 |
| train | path_traversal | 11799 | 11532 | 97.74 | [97.45, 97.99] | 11572 | 98.08 |
| train | cmdi | 6853 | 3715 | 54.21 | [53.03, 55.39] | 4004 | 58.43 |
| val | benign | 14887 | 56 | 0.38 | [0.29, 0.49] | 69 | 0.46 |
| val | sqli | 34107 | 27862 | 81.69 | [81.28, 82.10] | 27894 | 81.78 |
| val | xss | 4491 | 1493 | 33.24 | [31.88, 34.64] | 1516 | 33.76 |
| val | path_traversal | 2528 | 2466 | 97.55 | [96.87, 98.08] | 2479 | 98.06 |
| val | cmdi | 1468 | 806 | 54.90 | [52.35, 57.43] | 866 | 58.99 |
| train+val | benign | 84359 | 307 | 0.36 | [0.33, 0.41] | 408 | 0.48 |
| train+val | sqli | 193261 | 157878 | 81.69 | [81.52, 81.86] | 158066 | 81.79 |
| train+val | xss | 25453 | 8463 | 33.25 | [32.67, 33.83] | 8591 | 33.75 |
| train+val | path_traversal | 14327 | 13998 | 97.70 | [97.45, 97.94] | 14051 | 98.07 |
| train+val | cmdi | 8321 | 4521 | 54.33 | [53.26, 55.40] | 4870 | 58.53 |

## Thesis / docs figures (corpus_ua_skew.py, unified.jsonl, all rows incl. test)

| Class | n | ua>40 % | Thesis 0.4 / 33.3 / 97.7 | train | val | train+val |
|---|---:|---:|---|---:|---:|---:|
| benign | 99245 | 0.4 | 0.4 | 0.36 (Δ -0.04) | 0.38 | 0.36 |
| xss | 29897 | 33.3 | 33.3 | 33.25 (Δ -0.05) | 33.24 | 33.25 |
| cmdi | 9758 | 54.4 | — | 54.21 (Δ -0.19) | 54.90 (Δ +0.50) | 54.33 (Δ -0.07) |
| path_traversal | 16839 | 97.7 | 97.7 | 97.74 (Δ +0.04) | 97.55 (Δ -0.15) | 97.70 (Δ 0.00) |
| sqli | 227344 | 81.7 | — | 81.69 (Δ -0.01) | 81.69 | 81.69 |
