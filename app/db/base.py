from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

from app.models.organization import Organization  # noqa
from app.models.project_type import ProjectType  # noqa
from app.models.project import Project  # noqa
from app.models.plant import Plant  # noqa
from app.models.process_system import ProcessSystem  # noqa
from app.models.facility import Facility  # noqa
from app.models.facility_unit import FacilityUnit  # noqa
from app.models.document import Document  # noqa
from app.models.document_link import DocumentStructureLink  # noqa
from app.models.document_analysis import DocumentAnalysis  # noqa
from app.models.structure_candidate import StructureCandidate  # noqa
from app.models.candidate_evidence import CandidateEvidence  # noqa
