# vcd-state-ledger

Account for exact 0/1/x/z bit-time and transition evidence in small digital VCD captures.

For: RTL verification engineers reviewing a short simulation capture. A plot alone does not provide a reproducible unknown-state duration ledger across aliased signals.

## Quickstart

Python 3.10 or newer; no runtime packages or network access. The wheel build needs setuptools from the normal Python package registry.

```sh
git clone https://github.com/nripankadas07/vcd-state-ledger.git
cd vcd-state-ledger
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/vcd-state-ledger example.vcd --end-tick 15
```

The example intentionally exits 1: bus unknown bit-time is 10 bit-ticks. Clock 0/1 durations are 10/5 ticks; bus 0/1/x durations are 10/10/10 bit-ticks. Aliases share one signal record.

Windows equivalents use `.venv\Scripts\python.exe` and `.venv\Scripts\vcd-state-ledger.exe`; Windows/macOS are not executed by this release’s Linux CI.

## Contract

ASCII VCD with one timescale, module scopes and wire/reg/logic variables. Binary and scalar values; widths 1–256. Initial bits are x at tick zero. Initialization x-to-known counts as a value change; known scalar 0-to-1/1-to-0 counts as rising/falling evidence. Same-tick changes count but consume no duration. The last timestamp ends the interval unless --end-tick explicitly extends the final held values. Unknown bit-time includes x and z; all per-bit durations sum to width times end tick.

JSON goes to stdout. Exit 0 means a valid report without findings; exit 1 means a valid report with the documented findings; exit 2 means invalid input or an I/O failure, with an error on stderr and no partial report. `--help` describes options. Review outputs before sharing them; they may contain input identifiers.

## Limits

2 MiB, 250,000 tokens, 512 unique IDs, 2,000 names, 100,000 value events and scope depth 32. No real values, EVCD, FST, dump-on/off intervals, analog timing or power inference. This is a deliberately small capture parser, not a waveform viewer.

## Verify

```sh
python3 -m unittest -v test_behavior
python3 -m compileall -q .
python3 -m pip wheel --no-deps --wheel-dir dist .
python3 -m venv /tmp/vcd-state-ledger-check
/tmp/vcd-state-ledger-check/bin/python -m pip install --no-deps dist/*.whl
python3 verify_installed.py /tmp/vcd-state-ledger-check/bin/python
```

Installed-command checks run outside the checkout. See [validation](VALIDATION.md), [research](RESEARCH.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md) and [security](SECURITY.md).

Original implementation and invented fixtures developed with AI assistance. MIT license. No production adoption, competitor feature-absence or performance-superiority claim.
