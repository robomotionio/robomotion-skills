# /mnemos-status — Show Mnemos Memory Status

Show current Mnemos fatigue level, active node counts, and checkpoint status.

## Steps

1. Run `python3 -m mnemos status` in the project directory
2. Run `python3 -m mnemos fatigue` for detailed breakdown
3. Report the fatigue state and any recommended actions
4. If fatigue >= 0.60, suggest writing a checkpoint with `python3 -m mnemos checkpoint --force`
