import traceback
from typing import TypedDict

from guidance import gen
from guidance.models import Model

from .parser import Parser

# Telling model to write 'null' or 'nothing' causes it to
# append extra text like "... because blah blah"
NULL_LOCATION = "No locations are listed"


class LocationAnswer(TypedDict):
    country: str | None
    state: str | None
    city: str | None


class LocationParser(Parser[list[LocationAnswer]]):
    def create_prompt(self):
        prompt = f"""
List all the locations this job is located in.

Answer using the following format for each location:
COUNTRY, STATE_OR_REGION, CITY

Each location should be on a different line.
Use only unabbreviated names.
Do not include any trailing punctuation like periods.
Do not include any extra commentary or clarifications.
If the region or city is not specified, write null.
If no locations are listed, write '{NULL_LOCATION}'.
""".strip()

        prompt += "\n\nAnswer: " + gen("locations", stop=NULL_LOCATION)

        return prompt

    def extract_answer(self, output: Model) -> list[LocationAnswer]:
        answer = output["locations"]
        if not answer:
            return []

        answer = answer.strip()
        if answer == NULL_LOCATION:
            return []

        try:
            locs: list[LocationAnswer] = []
            lines = [ln for ln in answer.splitlines() if ln.strip()]

            for ln in lines:
                split = ln.split(",")
                if len(split) != 3:
                    raise Exception(f"Expected 3 vals but got {len(split)}: {ln}")

                [country, state, city] = split
                locs.append(
                    LocationAnswer(
                        country=self._clean(country),
                        state=self._clean(state),
                        city=self._clean(city),
                    )
                )

            return locs
        except:
            traceback.print_exc()
            return []

    def _clean(self, text: str) -> str:
        text = text.strip()

        if text.endswith("."):
            text = text[:-1]

        return text
