#!/bin/bash
echo "--- PROJECT README ---" > context_for_llm.txt
cat README.md >> context_for_llm.txt
echo -e "\n\n--- DIRECTORY STRUCTURE ---" >> context_for_llm.txt
ls -R >> context_for_llm.txt
echo -e "\n\n--- SOURCE CODE ---" >> context_for_llm.txt
for file in app.py index.html assistant/assistant.py assistant/session.py config/config.py Docker/rebuild_and_run.sh contexts/rules.txt contexts/prompt.txt; do
    echo -e "\n\n--- START OF FILE $file ---" >> context_for_llm.txt
    cat "$file" >> context_for_llm.txt
done