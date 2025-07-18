from pathlib import Path
from typing import Iterable

from linkedin_ai_matcher.utils import extract_tag_content, create_logger
from linkedin_ai_matcher.utils.models import (
    ApplicantSummary,
    Document,
)
from .llms import LLM


CREATE_SUMMARY_PROMPT = """
-- INSTRUCTIONS --
**ROLE**: You are an AI assistant tasked with creating a summary of an applicant based on their documents to determine what kind of job they might be suitable for.
**TASK**: Extract relevant information, including education, skills, character, and additional notes from the provided documents to accurately represent the applicant's profile. Before stating the summary, thoroughly analyze the documents and state your thoughts and reasoning leading to the conclusions.

**GUIDANCE**:
The summary should be concise, informative, and structured. Do not be overly verbose or redundant, and do not include subjective judgements or assumptions.

Use the following format in your response:

<thinking>
    (thoughts)
</thinking>

<ApplicantSummary>
    <education>
        (education)
    </education>
    <skills>
        (skills)
    </skills>
    <character>
        (character)
    </character>
    <additional_notes>
        (additional_notes)
    </additional_notes>
</ApplicantSummary>

Ensure that the summary is well-organized and easy to read. Use bullet points or lists where appropriate to enhance clarity.

-- END OF INSTRUCTIONS --

-- DOCUMENTS --
{documents}
-- END OF DOCUMENTS --
"""


class ApplicantSummarizer:
    def __init__(self, llm: LLM):
        """
        Initialize the ApplicantSummarizer with an LLM instance.

        Args:
            llm (LLM): An instance of the LLM to use for generating summaries.
        """
        self.llm = llm
        self.logger = create_logger(__name__)

        self.logger.info("%s initialized with LLM: %s", __class__, llm.model_name)

    def create_applicant_summary(
        self, documents: Iterable[Document]
    ) -> ApplicantSummary:
        """
        Create an applicant summary from a list of documents by extracting relevant information
        such as education, skills, character, and additional notes using an LLM.

        Args:
            documents (Iterable[Document]): List of documents containing applicant information.

        Returns:
            ApplicantSummary: A summary of the applicant's education, skills, character, and additional notes.
        """
        documents_string = "\n".join(str(document) for document in documents)
        prompt = CREATE_SUMMARY_PROMPT.format(documents=documents_string)

        response = self.llm(prompt)
        if not response:
            raise ValueError(
                "LLM response is empty. Unable to create applicant summary."
            )

        self.logger.info("LLM response received for applicant summary.")

        return ApplicantSummary(
            education=extract_tag_content(response, "education"),
            skills=extract_tag_content(response, "skills"),
            character=extract_tag_content(response, "character"),
            additional_notes=extract_tag_content(response, "additional_notes"),
        )

    def summary_from_paths(
        self,
        document_paths: Iterable[Path],
        additional_documents: Iterable[Document] = (),
    ) -> ApplicantSummary:
        """
        Create an applicant summary from a list of document paths and additional documents.

        Args:
            document_paths (Iterable[Path]): Paths to the documents containing applicant information.
            additional_documents (Iterable[Document], optional): Additional documents to include in the summary,
                e.g., a user-inputted text block.

        Returns:
            ApplicantSummary: A summary of the applicant's education, skills, character, and additional notes.
        """
        documents = [Document.from_file(path) for path in document_paths]
        documents.extend(additional_documents)

        return self.create_applicant_summary(documents)
