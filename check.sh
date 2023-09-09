#! /usr/bin/env nix-shell
#!nix-shell -p python310Full python310Packages.virtualenv python310Packages.flake8 python310Packages.coverage
#!nix-shell -i bash

main () {
    setup

    test_flake
    test_files
    test_coverage

}

setup () {
    SCRIPT_PATH=$(readlink -f "${BASH_SOURCE:-$0}")
    BASE_DIR=$(dirname "${SCRIPT_PATH}")
    
    [[ -f "${BASE_DIR}/venv" ]] || python -m venv "${BASE_DIR}/venv"
    [[ -z "${VIRTUAL_ENV}" ]] && source "${BASE_DIR}/venv/bin/activate"
    [[ -d "$(readlink -f ${BASE_DIR}/venv/lib/python*/site-packages/alembic)" ]] || pip3 install -r ${BASE_DIR}/requirements.txt
}

test_flake () {
    flake8 src/middleware tests/middleware
}

test_files () {
    # Check Plugins
    for plugin in ./src/middleware/invocado/plugins/*.py; do
        p=$(basename ${plugin})
        p=${p%.*}
        defs=($(awk -F'[ (]*' '/ def / {print $3}' ${plugin} | egrep -v "__init__|__init_subclass__|_fk_pragma"))
        readarray -t a_defs < <(printf '%s\n' "${defs[@]}" | sort)
        # Check Alphabetical
        if [[ "${defs[@]}" != "${a_defs[@]}" ]]; then
            echo ${plugin} is not in alphabetical order
            diff_arrays defs a_defs
        fi
#        # Check Missing Documentation
#        for def in ${defs[@]}; do
#            grep "## ${p}.${def}" ./docs/src/components/middleware/plugins/${p}.md > /dev/null 2>&1
#            if [[ $? != 0 ]]; then
#                grep "def ${def}(" ${plugin} -B1 | grep "@property" > /dev/null 2>&1
#                if [[ $? != 0 ]]; then
#                    echo ${p} missing documentation for: ${def}
#                fi
#            fi
#        done
    done
    
    # Check Tests
    for test in ./tests/middleware/test_*.py; do
        defs=($(awk -F'[ (]*' '/ def / {print $3}' ${test} | egrep -v "__init__|setUp"))
        readarray -t a_defs < <(printf '%s\n' "${defs[@]}" | sort)
        # Check Alphabetical
        if [[ "${defs[@]}" != "${a_defs[@]}" ]]; then
            echo -e "${test} is not in alphabetical order"
            diff_arrays defs a_defs
        fi
    done
    
    # Check Docs
    for doc in ./docs/src/components/middleware/plugins/*.md; do
        defs=($(awk -F'[ (]*' '/## / {print $2}' ${doc}))
        readarray -t a_defs < <(printf '%s\n' "${defs[@]}" | sort)
        # Check Alphabetical
        if [[ "${defs[@]}" != "${a_defs[@]}" ]]; then
            echo ${doc} is not in alphabetical order
            diff_arrays defs a_defs
        fi
    done
}

test_coverage () {
    python -m coverage run --source=src/middleware/invocado --omit=src/middleware/invocado/db/alembic/env.py,src/middleware/invocado/db/alembic/versions/*.py -m unittest discover tests/middleware/
    python -m coverage report | egrep -v "^[^T].*100%"
    python -m coverage html
}

diff_arrays () {
    local -n _one=$1
    local -n _two=$2
    echo "Alphabetical Order                                Current Order"
    echo "---------------------------------------------------------------"
    for ((i=0; i<${#_one[@]}; i++)); do
        _two[$i]="${_two[$i]}                                                   "
        #echo -e "${t:0:50}${_one[$i]}"
        echo -e "${_two[$i]:0:50}${_one[$i]}"
    done
}

main $@
