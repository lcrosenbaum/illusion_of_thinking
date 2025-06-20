#!/bin/bash

for N in {2..3}; do
    # Without --use_thinking
    python -m illusion_of_thinking.run_experiment --simulator_type RiverCrossing --N "$N" --k 2 --output_folder logs

    # With --use_thinking
    python -m illusion_of_thinking.run_experiment --simulator_type RiverCrossing --N "$N" --k 2 --use_thinking --output_folder logs
done

for N in {4..5}; do
    # Without --use_thinking
    python -m illusion_of_thinking.run_experiment --simulator_type RiverCrossing --N "$N" --k 3 --output_folder logs

    # With --use_thinking
    python -m illusion_of_thinking.run_experiment --simulator_type RiverCrossing --N "$N" --k 3 --use_thinking --output_folder logs
done
