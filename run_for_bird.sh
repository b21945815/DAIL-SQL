#!/bin/bash

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "--- 1. Data Preprocessing ---"
python data_preprocess.py --data_type bird --data_dir ./dataset/bird

echo "--- 2. Stage 1: Generate Questions ---"
python generate_question.py --data_type bird \
--split test --tokenizer gpt-3.5-turbo --prompt_repr SQL \
--selector_type EUCDISQUESTIONMASK --max_seq_len 4096 --k_shot 7 --example_type QA

echo "--- 3. Stage 2: Preliminary Prediction (Skeleton) ---"
python ask_llm.py \
--openai_api_key $OPENAI_API_KEY \
--model gpt-4o \
--question ./dataset/process/BIRD-TEST_SQL_7-SHOT_EUCDISQUESTIONMASK_QA-EXAMPLE_CTX-200_ANS-4096/ \
--db_dir ./dataset/bird/database

echo "--- 4. Stage 3: DAIL Selection ---"
python generate_question.py --data_type bird --split test --tokenizer gpt-3.5-turbo \
--prompt_repr SQL --max_seq_len 4096 --k_shot 7 --example_type QA --selector_type EUCDISMASKPRESKLSIMTHR \
--pre_test_result ./dataset/process/BIRD-TEST_SQL_7-SHOT_EUCDISQUESTIONMASK_QA-EXAMPLE_CTX-200_ANS-4096/RESULTS_MODEL-gpt-4o.txt

echo "--- 5. Stage 4: Final Prediction (GPT-4o) ---"
python ask_llm.py \
--openai_api_key $OPENAI_API_KEY \
--model gpt-4o \
--question ./dataset/process/BIRD-TEST_SQL_7-SHOT_EUCDISMASKPRESKLSIMTHR_QA-EXAMPLE_CTX-200_ANS-4096/ \
--db_dir ./dataset/bird/database

python to_bird_output.py --dail_output ./dataset/process/BIRD-TEST_SQL_7-SHOT_EUCDISMASKPRESKLSIMTHR_QA-EXAMPLE_CTX-200_ANS-4096/RESULTS_MODEL-gpt-4o.txt

echo "--- 6. Copying Result ---"
cp ./dataset/process/BIRD-TEST_SQL_7-SHOT_EUCDISMASKPRESKLSIMTHR_QA-EXAMPLE_CTX-200_ANS-4096/RESULTS_MODEL-gpt-4o.json ./RESULTS_MODEL-gpt-4o.json