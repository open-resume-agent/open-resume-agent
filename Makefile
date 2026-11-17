# Open Resume Agent — build pipeline
TODAY ?= $(shell date +%F)
PY = python3 -I
EXAMPLES = $(wildcard examples/*.resume-agent.json)

.PHONY: all schema agents samples site validate test check clean
all: schema agents samples site validate test

schema:
	$(PY) tools/build_schema.py

agents: schema
	@for f in $(EXAMPLES); do b=$$(basename $$f .json); $(PY) tools/build_md.py $$f -o agents/$$b.md --today $(TODAY); done
	$(PY) tools/to_agent_card.py examples/tech-executive.resume-agent.json > agents/tech-executive.agent-card.json

samples: agents
	$(PY) tools/render.py agents/tech-executive.resume-agent.md --format docx --view rv-head-eng -o samples/jane-doe-head-eng.docx --today $(TODAY)
	$(PY) tools/render.py agents/tech-executive.resume-agent.md --format pdf --view rv-staff-eng --template ats -o samples/jane-doe-staff-eng-ats.pdf --today $(TODAY)
	$(PY) tools/render.py agents/tech-executive.resume-agent.md --format json-resume -o samples/jane-doe.resume.json --today $(TODAY)
	$(PY) tools/render.py agents/tech-executive.resume-agent.md --format txt -o samples/jane-doe.txt --today $(TODAY)
	$(PY) tools/render.py agents/research-scientist.resume-agent.md --format pdf -o samples/priya-raman-academic-cv.pdf --today $(TODAY)
	$(PY) tools/render.py agents/registered-nurse.resume-agent.md --format docx --template ats -o samples/maria-santos-ats.docx --today $(TODAY)
	$(PY) tools/render.py agents/electrician.resume-agent.md --format md -o samples/dwayne-carter.md --today $(TODAY)
	$(PY) tools/render.py agents/veteran-logistics.resume-agent.md --format html --view rv-driver -o samples/sam-okafor-driver.html --today $(TODAY)

site: schema
	$(PY) tools/build_site.py

validate:
	$(PY) tools/validate.py $(EXAMPLES) agents/*.md --today $(TODAY)

test:
	$(PY) tests/test_validator.py
	$(PY) tests/test_agent_file.py

# Local CI: fails if generated files are stale, then validates and tests
check:
	$(PY) tools/build_schema.py >/dev/null && git diff --exit-code schema/
	$(MAKE) -s agents TODAY=2026-11-17 && git diff --exit-code agents/
	$(PY) tools/build_site.py >/dev/null && git diff --exit-code docs/
	$(MAKE) -s validate test TODAY=2026-11-17

clean:
	rm -rf samples/* build
