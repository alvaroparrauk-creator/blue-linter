"""Internal parsed document models for rule execution."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BlockType = Literal["paragraph", "heading", "bullet", "list_item", "unknown"]


class DocumentBlock(BaseModel):
    """A traceable text block extracted from a source document."""

    model_config = ConfigDict(extra="forbid")

    block_id: str = Field(min_length=1)
    paragraph_index: int = Field(ge=0)
    text: str
    style_name: str = Field(min_length=1)
    block_type: BlockType
    section_title: str | None = None


class ParsedDocument(BaseModel):
    """Document representation consumed by deterministic style rules."""

    model_config = ConfigDict(extra="forbid")

    source_name: str | None = None
    blocks: list[DocumentBlock]
