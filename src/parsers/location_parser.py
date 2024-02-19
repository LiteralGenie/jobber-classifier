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
Do not include any extra punctuation like periods.
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
            lines = answer.splitlines()

            for ln in lines:
                split = ln.split(",")
                if len(split) != 3:
                    raise Exception(f"Expected 3 vals but got {len(split)}: {ln}")

                [country, state, city] = split
                locs.append(
                    LocationAnswer(
                        country=country.strip(),
                        state=state.strip(),
                        city=city.strip(),
                    )
                )

            return locs
        except:
            traceback.print_exc()
            return []
