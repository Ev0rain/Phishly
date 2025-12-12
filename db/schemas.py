from typing import Optional
from pydantic import BaseModel, ConfigDict


class AdminUserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class DepartmentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TargetDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    department_id: Optional[int] = None


class TargetListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_by_id: Optional[int] = None


class TargetListMemberDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    target_list_id: int
    target_id: int


class EmailTemplateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_by_id: Optional[int] = None


class LandingPageDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_by_id: Optional[int] = None


class CampaignDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_by_id: Optional[int] = None
    email_template_id: Optional[int] = None
    landing_page_id: Optional[int] = None


class CampaignTargetListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    campaign_id: int
    target_list_id: int


class CampaignTargetDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    campaign_id: int
    target_id: int
    email_template_id: Optional[int] = None
    landing_page_id: Optional[int] = None


class EmailJobDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    campaign_target_id: Optional[int] = None


class EventTypeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class EventDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    campaign_target_id: Optional[int] = None
    event_type_id: Optional[int] = None


class FormTemplateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    landing_page_id: Optional[int] = None
    created_by_id: Optional[int] = None


class FormQuestionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    form_template_id: Optional[int] = None


class FormSubmissionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    campaign_target_id: Optional[int] = None
    form_template_id: Optional[int] = None


class FormAnswerDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    form_submission_id: Optional[int] = None
    form_question_id: Optional[int] = None
