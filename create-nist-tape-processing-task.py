#!/usr/bin/env python

import getopt
import os
import sys
from enum import auto, Enum

import questionary
from todoist_api_python.api import TodoistAPI

from lib.tasks import create_task, create_subtask, TaskType, WorkType


ARCHIVING_PROJECT_ID = 2288914343
TAPE_PROCESSING_SECTION_ID = 156150000
VIDEO_SOURCES = {
    "EnhancedWTCVideos": "https://www.youtube.com/@WTCFOIAVideos",
    "MrKoenig1985": "https://www.youtube.com/@MrKoenig1985",
    "WTC911Videos": "https://www.youtube.com/@wtc911videos5",
    "Organized WTC Visual Databases": "https://www.youtube.com/@themkmonarch",
    "911NewsCoverage": "https://www.youtube.com/@911newscoverage6",
    "Allen Williams": "https://www.youtube.com/@DovidoxVideos",
    "famartin1": "https://www.youtube.com/@famartin1",
    "The Media Stash": "https://www.youtube.com/@themediastash1711",
    "News from the Past": "https://www.youtube.com/@NewsfromthePast",
    "911AnalysisVideo": "https://www.youtube.com/@911analysisvideo8",
    "CTV911": "https://www.youtube.com/@CTV911/videos",
    "11septembervideos": "https://www.youtube.com/@11septembervideos",
    "11-Septembre OFFICIEL": "https://www.youtube.com/@11SeptembreOFFICIEL",
    "WTC911demolition": "https://www.youtube.com/@WTC911demolition",
    "AE911Truth": "https://www.youtube.com/@ae911truthvideos",
    "NIST Review Archive Collection": "https://archive.org/details/nistreview",
    "September 11 Television Archive" : "https://archive.org/details/sept_11_tv_archive",
    "NBC: September 11th Television Archive" : "https://archive.org/details/NBC_TV"
}


class TapeType(Enum):
    AMATEUR = auto()
    NEWS = auto()
    PROFESSIONAL = auto()


def main(tape_name, tape_type):
    api_token = os.getenv("TODOIST_API_TOKEN")
    if not api_token:
        raise Exception("The TODOIST_API_TOKEN environment variable must be set")
    api = TodoistAPI(api_token)

    if not tape_name:
        tape_name = questionary.text("Supply the name of the tape:").ask()
    if not tape_type:
        tape_type = questionary.select(
            "Select the tape type", choices=[t.name for t in TapeType]
        ).ask()
        tape_type = TapeType[tape_type]

    if tape_type == TapeType.NEWS:
        parent = create_task(
            api,
            f"Process `{tape_name}` NIST tape [news broadcast]",
            ARCHIVING_PROJECT_ID,
            TaskType.RESEARCH,
            WorkType.PERSONAL,
            section_id=TAPE_PROCESSING_SECTION_ID
        )
        create_subtask(
            api,
            "Find the tape in the NIST dataset",
            ARCHIVING_PROJECT_ID,
            TaskType.RESEARCH,
            WorkType.PERSONAL,
            parent.id,
        )
        create_subtask(
            api,
            "Create or identify an existing news network",
            ARCHIVING_PROJECT_ID,
            TaskType.RESEARCH,
            WorkType.PERSONAL,
            parent.id,
        )
        create_subtask(
            api,
            "Create or identify an existing news affiliate",
            ARCHIVING_PROJECT_ID,
            TaskType.RESEARCH,
            WorkType.PERSONAL,
            parent.id,
        )
        create_subtask(
            api,
            "Create a news broadcast record",
            ARCHIVING_PROJECT_ID,
            TaskType.RESEARCH,
            WorkType.PERSONAL,
            parent.id,
        )
        create_subtask(
            api,
            "Determine if footage is continuous",
            ARCHIVING_PROJECT_ID,
            TaskType.RESEARCH,
            WorkType.PERSONAL,
            parent.id,
        )
        create_subtask(
            api,
            "Timestamps pass through",
            ARCHIVING_PROJECT_ID,
            TaskType.RESEARCH,
            WorkType.PERSONAL,
            parent.id,
        )
        create_subtask(
            api,
            "Camera sources pass through",
            ARCHIVING_PROJECT_ID,
            TaskType.RESEARCH,
            WorkType.PERSONAL,
            parent.id,
        )
        create_subtask(
            api,
            "Create and populate master video record",
            ARCHIVING_PROJECT_ID,
            TaskType.RESEARCH,
            WorkType.PERSONAL,
            parent.id,
        )
        for name, url in VIDEO_SOURCES.items():
            create_subtask(
                api,
                f"Create video record from [{name}]({url}) if applicable",
                ARCHIVING_PROJECT_ID,
                TaskType.RESEARCH,
                WorkType.PERSONAL,
                parent.id,
            )


if __name__ == "__main__":
    tape_name = None
    tape_type = None
    opts, args = getopt.getopt(sys.argv[1:], "", ["tape-name=", "tape-type="])
    for opt, arg in opts:
        if opt in "--tape-name":
            tape_name = arg
        elif opt in "--tape-type":
            tape_type = TapeType[arg]
    sys.exit(main(tape_name, tape_type))
