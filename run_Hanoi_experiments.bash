#!/bin/bash

for N in {3..10}; do
    # Without --use_thinking
    python -m illusion_of_thinking.run_experiment --simulator_type TowerOfHanoi --N "$N" --output_folder logs

    # With --use_thinking
    python -m illusion_of_thinking.run_experiment --simulator_type TowerOfHanoi --N "$N" --use_thinking --output_folder logs
done
