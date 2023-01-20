#!/bin/sh

# The markdown mode of aspell does not make code be ignored (but it is still
# useful for not spellchecking links). This sed command removes both inline code
# and code blocks.

# sed -e 's/\s*`\b.*\b`//g' -e '/```.*/,/```/d' README.md -i
# aspell --home-dir=.github --personal=data/wordlist.txt --lang=en_US --mode=markdown list < README.md | sort -u > badwords
# if [ -s badwords ]
# then
#     grep -w -C 3 --color=always -f badwords README.md
#     printf "\n-----------------------------------------------------------------------\n"
#     printf "The following words are not in the English, nor the project's dictionary:\n"
#     cat badwords
#     printf "\nCheck your spelling and if you think you've spelled correctly, update the file\n.github/data/wordlist.txt"
#     exit 1
# else
#     echo "No misspelled words discovered!"
#     exit 0
# fi

green=$(tput -T xterm setaf 2)
red=$(tput -T xterm setaf 1)
normal=$(tput -T xterm sgr0)
misspelled_files="no_exists"

find * -name "*.md" |
    {
    while read -r file_to_check
        do
            {
                printf "\n-----------------------------------------------------"
                printf -- "---------------------------\n"

            }
            {
                printf "Checking spelling of file %b. " "$file_to_check"
                printf "Potentially misspelled words will be highlighted.\n\n"
            } | fmt --width=80 -
            tmp_dir="/tmp/reviewcheck-spelling"
            mkdir "$tmp_dir" --parents
            # We will use the basename so we don't have to create more
            # subdirectories in the /tmp folder. But when printing we use the
            # full path so the user can see the relative location of the file in
            # the repository.
            file_to_check_basename=$(basename "$file_to_check")
            cp "$file_to_check" $tmp_dir
            sed -ri \
                -e 's/\s*`[^`]+`//g' \
                -e '/```.*/,/```/d' \
                "$tmp_dir/$file_to_check_basename"
            aspell \
                --home-dir=./ \
                --personal=.github/data/wordlist.txt \
                --lang=en_US \
                --mode=markdown \
                list < "$tmp_dir/$file_to_check_basename" |
                sort -u > "$tmp_dir/badwords"
            if [ -s "$tmp_dir/badwords" ]
            then
                misspelled_files="exists"
                grep \
                    -w \
                    -C 3 \
                    --color=always \
                    -f "$tmp_dir/badwords" \
                    "$tmp_dir/$file_to_check_basename"
                printf -- "--\n\n"
                {
                    printf "%sSuspected spelling errors found in file " "$red"
                    printf "%s%s. " "$file_to_check" "$normal"
                    printf "The following words are neither in the English, "
                    printf "nor the project's dictionary:\n\n"
                } | fmt --width=80 -
                sed -e 's/\(.*\)/- "\1"/' "$tmp_dir/badwords"
                {
                    printf "\nCheck your spelling and if you think you've "
                    printf "spelled correctly, update the file "
                    printf ".github/data/wordlist.txt."
                } | fmt --width=80 -
            else
                printf "%sNo misspelled words found in %s.%s\n" \
                    "$green" "$file_to_check" "$normal"
            fi
            rm "$tmp_dir/badwords"
        done

        if [ $misspelled_files = "exists" ]; then
            exit 1
        else
            printf "\n%sNo misspelled words found in any markdown file!%s\n" \
                "$green" "$normal"
            exit 0
        fi
}
