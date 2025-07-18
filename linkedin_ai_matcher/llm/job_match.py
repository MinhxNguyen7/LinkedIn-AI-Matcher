from linkedin_ai_matcher.utils.log import create_logger

from .llms import LLM

from linkedin_ai_matcher.utils import extract_tag_content
from linkedin_ai_matcher.utils.models import (
    ApplicantInfo,
    JobMatchResult,
    JobInfo,
    JobFit,
)


JOB_MATCH_PROMPT = """
-- INSTRUCTIONS --
**ROLE**: You are an AI assistant tasked with deciding how well a job matches an applicant based on their applicant profile.
**TASK**: Compare the provided applicant profile with the job information to determine how well the job matches the applicant. Consider both technical requirements and cultural fit.

**GUIDANCE**:
- Be objective and unopinionated in your assessment.
- Judge the match critically, and provide clear reasoning for your decision.
- Use specific examples from the applicant profile and job information to support your assessment.
- Consider the following factors:
  * Technical skills alignment (required vs. preferred)
  * Experience level match (junior, mid-level, senior)
  * Domain/industry experience relevance
  * Career trajectory and growth potential
  * Cultural fit based on company values and work style
  * Geographic and other practical considerations

**MATCH CRITERIA**:
- Excellent: Strong alignment across all key requirements, candidate exceeds expectations
- Good: Solid match with minor gaps that can be addressed through training/growth
- Fair: Moderate fit with some significant gaps
- Poor: Major misalignment in critical requirements or experience level

**OUTPUT FORMAT**:
<thinking>
    [Systematically analyze: 1) Technical skills match, 2) Experience level fit, 3) Domain relevance, 4) Growth potential, 5) Any red flags or strong positives]
</thinking>

<MatchResult>
    <fit>
        [One of: Excellent, Good, Fair, Poor]
    </fit>
    <reasons>
        [Bullet-pointed reasoning covering: technical alignment, experience match, domain fit, and any notable strengths or concerns. Be specific and reference both applicant profile and job requirements.]
    </reasons>
</MatchResult>

-- END OF INSTRUCTIONS --

-- APPLICANT PROFILE --
{applicant_info}

-- JOB INFORMATION --
{job_info}
-- END OF JOB INFORMATION --
"""


class JobMatchChecker:
    def __init__(self, llm: LLM):
        """
        Initialize the JobMatchChecker with an LLM instance.

        Args:
            llm (LLM): An instance of the LLM to ask how well a job matches an applicant.
        """
        self.llm = llm
        self.logger = create_logger(__class__.__name__)

        self.logger.info("%s initialized with LLM: %s", __class__, llm.model_name)

    def check_job_match(
        self, applicant_info: ApplicantInfo, job_info: JobInfo
    ) -> JobMatchResult:
        """
        Check how well a job matches an applicant based on their profile.

        Args:
            applicant_info (ApplicantInfo): The applicant's profile information
            job_info (JobInfo): The job posting information

        Returns:
            JobMatchResult: Result containing fit assessment and reasoning
        """
        prompt = JOB_MATCH_PROMPT.format(
            applicant_info=applicant_info,
            job_info=job_info.content,
        )

        self.logger.info(
            f"Checking job match for job ID: {job_info.id} ({job_info.content.title} @ {job_info.content.company})"
        )
        response = self.llm(prompt)

        if not response:
            self.logger.error("LLM response is empty. Unable to check job match.")
            raise ValueError("LLM response is empty. Unable to check job match.")

        self.logger.info("LLM response received for job match check.")

        fit_str = extract_tag_content(response, "fit").strip()
        reasons = extract_tag_content(response, "reasons")

        try:
            fit = JobFit.from_value(fit_str)
        except ValueError as e:
            self.logger.warning(
                f"Failed to parse fit '{fit_str}': {e}. Defaulting to FAIR."
            )
            fit = JobFit.FAIR

        return JobMatchResult(job_info=job_info, fit=fit, reasons=reasons)
