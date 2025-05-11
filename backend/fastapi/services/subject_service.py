from typing import List, Optional

from models.subject import Subject
from models.DTOs.subject_dto import SubjectCreate, SubjectUpdate, SubjectResponse
from repositories.abstract.subject_repository_interface import ISubjectRepository
from services.abstract.subject_service_interface import ISubjectService

class SubjectService(ISubjectService):
    def __init__(self, subject_repository: ISubjectRepository):
        self.subject_repository = subject_repository

    def get_all_subjects(self) -> List[SubjectResponse]:
        subjects = self.subject_repository.get_all()
        return [SubjectResponse.model_validate(subject) for subject in subjects]

    def get_subject_by_id(self, subject_id: int) -> Optional[SubjectResponse]:
        subject = self.subject_repository.get_by_id(subject_id)
        if subject:
            return SubjectResponse.model_validate(subject)
        return None
    
    def get_subjects_by_group_id(self, group_id: int) -> List[SubjectResponse]:
        subjects = self.subject_repository.get_by_group_id(group_id)
        return [SubjectResponse.model_validate(subject) for subject in subjects]
    
    def get_subjects_by_teacher_id(self, teacher_id: int) -> List[SubjectResponse]:
        subjects = self.subject_repository.get_by_teacher_id(teacher_id)
        return [SubjectResponse.model_validate(subject) for subject in subjects]

    def create_subject(self, subject_data: SubjectCreate) -> SubjectResponse:
        # Create new subject object
        subject = Subject(
            name=subject_data.name,
            shortName=subject_data.shortName,
            studyProgram=subject_data.studyProgram,
            studyYear=subject_data.studyYear,
            groupId=subject_data.groupId,
            teacherId=subject_data.teacherId
        )
        
        # Save to database
        created_subject = self.subject_repository.create(subject)
        return SubjectResponse.model_validate(created_subject)

    def update_subject(self, subject_id: int, subject_data: SubjectUpdate) -> Optional[SubjectResponse]:
        subject = self.subject_repository.get_by_id(subject_id)
        if not subject:
            return None
            
        # Update subject fields if provided
        if subject_data.name is not None:
            subject.name = subject_data.name
        if subject_data.shortName is not None:
            subject.shortName = subject_data.shortName
        if subject_data.studyProgram is not None:
            subject.studyProgram = subject_data.studyProgram
        if subject_data.studyYear is not None:
            subject.studyYear = subject_data.studyYear
        if subject_data.groupId is not None:
            subject.groupId = subject_data.groupId
        if subject_data.teacherId is not None:
            subject.teacherId = subject_data.teacherId
            
        # Save changes
        updated_subject = self.subject_repository.update(subject)
        return SubjectResponse.model_validate(updated_subject)

    def delete_subject(self, subject_id: int) -> bool:
        return self.subject_repository.delete(subject_id)
