#!/bin/zsh
echo "Strat running main program..."

for i in {1..5}; do
    run
done

echo "End running main program..."
read input

function run(){
    echo "Please choose your mode: [A] visualization mode  [B] cmd mode"
    read mode
    if [ $mode = "A" ]; then
        echo "Start running in visualization mode..."
        python3 src/main_control.py
    elif [ $mode = "B" ]; then
        echo "Start running in cmd mode..."
        python3 src/main_control.py -d
    else
        echo "Invalid input, please try again."
        echo "Please choose your mode: [A] visualization mode  [B] cmd mode"
        read mode
    fi
}
