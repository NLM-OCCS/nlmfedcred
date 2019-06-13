export AWSCREDS=$HOME/.aws/tempcreds.sh

function awscreds () {
    if [[ $# -ne 1 ]]; then
        echo "Usage: awscreds <profile>" >&2
        return 1
    fi

    getawscreds --shell=bash -p $1 -o $AWSCREDS
    if [[ $? -ne 0 ]]; then
        return 1
    fi

    test -f $AWSCREDS && source $AWSCREDS 
    return 0
}


