# note 300

This note records the staleness sweep and what the project takes from it.

## Observation

At a stale fraction of 0.1 the measured error was 0.04.

## Method

A single layer, mean aggregation, sixteen dimensions.

Weights were left untrained and the model was held in eval mode, so nothing in the
measurement depends on what the network had learned.
