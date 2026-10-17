# Research — 17 October 2026

User: RTL verification engineers reviewing a short simulation capture.

Pain: A plot alone does not provide a reproducible unknown-state duration ledger across aliased signals.

Smallest useful capability: Account for exact 0/1/x/z bit-time and transition evidence in small digital VCD captures.

Acceptance: Exact duration conservation, aliases, same-tick glitches, scalar edges and x/z propagation; reject undeclared identifiers, invalid widths, incomplete scopes and decreasing timestamps.

Demand is inferred from the workflow and adjacent public evidence, not a verified request for this product. Discovery path: descriptive GitHub topics, a runnable invented example and the chronological portfolio index. No unsolicited outreach or activity manipulation.

## Current alternatives

Live GitHub repository search, sorted **Most stars**, query `VCD waveform` and the related broad queries recorded in [provenance](RESEARCH_PROVENANCE.json). Highest-star relevant comparable found in this inspected scope: **gtkwave/gtkwave**. This is not an exhaustive global ranking.

| Repository | Stars observed | Last push observed (UTC) | Archived | API license classification |
| --- | ---: | --- | --- | --- |
| [gtkwave/gtkwave](https://github.com/gtkwave/gtkwave) | 1033 | 2026-10-12T04:06:19Z | False | GPL-2.0 |
| [cirosantilli/vcdvcd](https://github.com/cirosantilli/vcdvcd) | 71 | 2025-10-19T19:52:12Z | False | NOASSERTION |
| [ics-jku/wal](https://github.com/ics-jku/wal) | 188 | 2026-09-22T11:52:31Z | False | BSD-3-Clause |

GTKWave offers interactive waveform inspection and many more formats. vcdvcd exposes timestamps and alias references; WAL provides programmable waveform analysis. WAL issue 46 discusses large-capture memory; that is adjacent demand evidence, not a request for this tool or proof of an unresolved defect. Our bounded JSON accounting does not replace these systems.

Use GTKWave, script vcdvcd, or write a WAL analysis.

Current README, selected source semantics and up to five issue/PR records were read. Exact observation times, source blob identities, queries and public issue URLs are in provenance. API NOASSERTION means unclassified license, not permission to copy. No third-party implementation or fixtures are bundled.

Our small Python wheel installs with one command after checkout and includes a direct example. Established alternatives have broader APIs, formats, documentation, examples and support communities. Competitor installations, time to first useful result, reliability, support response and performance were not measured. Our example only proves our documented behavior. Stars inform discovery, not quality or performance.

Portfolio distinction: The existing traceweave repository analyzes AI-agent JSONL traces. This project reads hardware Value Change Dump signal state and bit-time; it is not another JSONL trace formatter.

No technical performance benchmark, speed/memory superiority or exhaustive feature-gap claim is made. Standard file formats and algorithms are not inventions of this project. Source references informed semantic review; implementation, prose and invented fixtures are original. No copied branding or sample user data is included.
